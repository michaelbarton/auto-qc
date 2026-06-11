"""The s-expression engine: one evaluator for ``run``, ``--explain`` and tests.

A rule is a nested list (an s-expression). A list whose first element is a known
operator is an *application*; any other list is a *literal list* (e.g. the set
of allowed values for ``is_in``). Strings beginning with ``:`` are pointers into
the data document.

:func:`evaluate` is the single source of truth: it resolves pointers, applies
operators, and returns a :class:`Trace` carrying both the result and a tree that
explains how it was reached. ``--explain`` renders that tree; the JSON output
serialises it; the pass/fail logic reads ``trace.result``. There is no second
evaluator to drift out of sync.
"""

import dataclasses
import functools
import operator
import re
import typing

from auto_qc import variable
from auto_qc.evaluate import exception


@dataclasses.dataclass(frozen=True)
class Operator:
    """An operator's implementation plus the metadata used to validate it."""

    func: typing.Callable[..., typing.Any]
    min_args: int
    max_args: int | None  # ``None`` means unbounded (variadic).
    kind: str  # Used to phrase type errors, e.g. "compare" / "do arithmetic on".


def _product(values: typing.Iterable[float]) -> float:
    return functools.reduce(operator.mul, values, 1)


OPERATORS: dict[str, Operator] = {
    # Comparisons.
    "greater_than": Operator(operator.gt, 2, 2, "compare"),
    "greater_equal_than": Operator(operator.ge, 2, 2, "compare"),
    "less_than": Operator(operator.lt, 2, 2, "compare"),
    "less_equal_than": Operator(operator.le, 2, 2, "compare"),
    "equals": Operator(operator.eq, 2, 2, "compare"),
    "not_equals": Operator(operator.ne, 2, 2, "compare"),
    "between": Operator(lambda v, lo, hi: lo <= v <= hi, 3, 3, "compare"),
    # Boolean combinators. Their arguments are themselves rules.
    "and": Operator(lambda *args: all(args), 1, None, "combine"),
    "or": Operator(lambda *args: any(args), 1, None, "combine"),
    "not": Operator(lambda x: not x, 1, 1, "combine"),
    # Membership.
    "is_in": Operator(lambda x, y: x in y, 2, 2, "test membership of"),
    "is_not_in": Operator(lambda x, y: x not in y, 2, 2, "test membership of"),
    "contains": Operator(lambda x, y: y in x, 2, 2, "test membership of"),
    "list": Operator(lambda *args: list(args), 0, None, "build a list from"),
    # Arithmetic, for rules over derived values like ratios.
    "add": Operator(lambda *args: sum(args), 2, None, "do arithmetic on"),
    "subtract": Operator(lambda a, b: a - b, 2, 2, "do arithmetic on"),
    "multiply": Operator(lambda *args: _product(args), 2, None, "do arithmetic on"),
    "divide": Operator(lambda a, b: a / b, 2, 2, "do arithmetic on"),
    # String / collection predicates.
    "matches": Operator(lambda s, pattern: re.search(pattern, s) is not None, 2, 2, "match"),
    "starts_with": Operator(lambda s, prefix: s.startswith(prefix), 2, 2, "match"),
    "ends_with": Operator(lambda s, suffix: s.endswith(suffix), 2, 2, "match"),
    "length": Operator(lambda x: len(x), 1, 1, "measure the length of"),
}

# Operators whose arguments are themselves boolean rules rather than values.
RULE_POSITION_OPERATORS = {"and", "or", "not"}


def is_operator(value: typing.Any) -> bool:
    return isinstance(value, str) and value.lower() in OPERATORS


def is_application(expr: typing.Any) -> bool:
    """Is ``expr`` a rule application (a list led by a known operator)?"""
    return isinstance(expr, list) and len(expr) > 0 and is_operator(expr[0])


def _describe(value: typing.Any) -> str:
    """A short, human word for a value's type, for error messages."""
    if value is None:
        return "missing (null)"
    if isinstance(value, bool):
        return "true/false"
    if isinstance(value, (int, float)):
        return f"the number {value!r}"
    if isinstance(value, str):
        return f"the text {value!r}"
    if isinstance(value, list):
        return f"the list {value!r}"
    return repr(value)


def arity_message(op_name: str, op: Operator, given: int) -> str:
    """Phrase a wrong-number-of-arguments error."""
    if op.max_args == op.min_args:
        expected = f"exactly {op.min_args} argument{'s' if op.min_args != 1 else ''}"
    elif op.max_args is None:
        expected = f"at least {op.min_args} argument{'s' if op.min_args != 1 else ''}"
    else:
        expected = f"between {op.min_args} and {op.max_args} arguments"
    return f"Operator '{op_name.lower()}' takes {expected} but got {given}."


def _type_message(op_name: str, op: Operator, args: list[typing.Any]) -> str:
    described = " and ".join(_describe(a) for a in args)
    return (
        f"Operator '{op_name.lower()}' could not {op.kind} {described}. "
        f"Check that the rule and the data have compatible types."
    )


def _apply(op_name: str, op: Operator, args: list[typing.Any]) -> typing.Any:
    given = len(args)
    if given < op.min_args or (op.max_args is not None and given > op.max_args):
        raise exception.EvaluationError(arity_message(op_name, op, given))
    try:
        return op.func(*args)
    except ZeroDivisionError:
        raise exception.EvaluationError(f"Operator '{op_name.lower()}' divided by zero.") from None
    except (TypeError, AttributeError):
        raise exception.EvaluationError(_type_message(op_name, op, args)) from None


@dataclasses.dataclass
class Trace:
    """The result of evaluating an expression, plus an explanation tree."""

    result: typing.Any
    kind: str  # "operator" | "variable" | "literal" | "list"
    operator: str | None = None
    variable: str | None = None
    children: list["Trace"] = dataclasses.field(default_factory=list)

    def to_dict(self) -> dict[str, typing.Any]:
        """A JSON-serialisable view of this trace, for ``--json-output``."""
        if self.kind == "variable":
            return {"variable": self.variable, "value": self.result}
        if self.kind == "literal":
            return {"literal": self.result}
        if self.kind == "list":
            return {"list": [child.to_dict() for child in self.children]}
        return {
            "operator": (self.operator or "").lower(),
            "result": self.result,
            "args": [child.to_dict() for child in self.children],
        }


def evaluate(expr: typing.Any, data: dict[str, typing.Any]) -> Trace:
    """Evaluate an s-expression against ``data``, returning a :class:`Trace`.

    Raises:
        EvaluationError: If an operator is applied to incompatible types or the
            wrong number of arguments.
    """
    if variable.is_variable(expr):
        return Trace(result=variable.resolve(data, expr), kind="variable", variable=expr)

    if is_application(expr):
        op_name = expr[0]
        op = OPERATORS[op_name.lower()]
        children = [evaluate(arg, data) for arg in expr[1:]]
        result = _apply(op_name, op, [child.result for child in children])
        return Trace(result=result, kind="operator", operator=op_name, children=children)

    if isinstance(expr, list):
        children = [evaluate(element, data) for element in expr]
        return Trace(result=[child.result for child in children], kind="list", children=children)

    return Trace(result=expr, kind="literal")
