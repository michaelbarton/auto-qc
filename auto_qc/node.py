import functools
import operator
import typing

from auto_qc import variable
from auto_qc.util import functional

OPERATORS: dict[str, typing.Callable[..., typing.Any]] = {
    "greater_than": operator.gt,
    "greater_equal_than": operator.ge,
    "less_than": operator.lt,
    "less_equal_than": operator.le,
    "equals": operator.eq,
    "not_equals": operator.ne,
    "and": lambda *args: all(args),
    "or": lambda *args: any(args),
    "not": lambda x: not x,
    "is_in": lambda x, y: x in y,
    "is_not_in": lambda x, y: x not in y,
    "list": lambda *args: list(args),
}


def is_operator(v: typing.Any) -> bool:
    return isinstance(v, str) and v.lower() in OPERATORS


def has_doc_dict(qc_node: list[typing.Any]) -> bool:
    return isinstance(qc_node[0], dict)


def get_all_operators(qc_node: list[typing.Any]) -> list[typing.Any]:
    """
    Returns all operators listed in a QC node
    """

    def _walk_node(n: list[typing.Any]) -> list[typing.Any]:
        operator_, rest = n[0], n[1:]
        return [operator_, *f(rest)]

    f = functools.partial(map, functional.recursive_apply(_walk_node, functional.empty_list))

    return functional.flatten(_walk_node(qc_node))


def eval_variables(analyses: dict[str, typing.Any], rule: list[typing.Any]) -> list[typing.Any]:
    """
    Replace all variables in a node s-expression with their referenced literal
    value.

    Args:
      analyses: A dictionary corresponding to the values referenced in the
      given s-expression.
      rule: An s-expression list in the form of [operator, arg1, arg2, ...].

    Yields:
      A node expression with referenced values replaced with their literal values.

    Examples:
      >>> eval_variables({a: 1}, [>, :a, 2])
      [>, 1, 2]
    """

    def _eval(n: typing.Any) -> typing.Any:
        if variable.is_variable(n):
            return variable.get_variable_value(analyses, n)
        else:
            return n

    return list(
        map(functional.recursive_apply(functools.partial(eval_variables, analyses), _eval), rule)
    )


def evaluate_rule(node: list[typing.Any]) -> typing.Any:
    """
    Evaluate an s-expression by applying the operator to the rest of the arguments.

    Args:
      node (list): An s-expression list in the form of [operator, arg1, arg2, ...]

    Yields:
      The result of "applying" the operator to the arugments. Will evaluate
      recursively if any of the args are a list.

    Examples:
      >>> evaluate_rule([>, 0, 1])
      FALSE
    """
    args = list(map(functional.recursive_apply(evaluate_rule), node[1:]))
    op = node[0]
    qc_func = OPERATORS[op.lower() if isinstance(op, str) else op]
    return qc_func(*args)
