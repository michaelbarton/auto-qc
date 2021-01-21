import operator
import typing

import fn
import funcy
from fn import iters

from auto_qc import variable
from auto_qc.util import functional

OPERATORS = {
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


def is_operator(v):
    return v in OPERATORS.keys()


def has_doc_dict(qc_node):
    return isinstance(iters.head(qc_node), dict)


def get_all_operators(qc_node):
    """
    Returns all operators listed in a QC node
    """

    def _walk_node(n):
        if has_doc_dict(n):
            return _walk_node(list(iters.tail(n)))
        else:
            operator_ = iters.head(n)
            rest = iters.tail(n)
            return [operator_, *f(rest)]

    f = funcy.partial(map, functional.recursive_apply(_walk_node, functional.empty_list))

    return functional.flatten(_walk_node(qc_node))


def eval_variables(analyses: typing.Dict[str, typing.Any], rule: typing.List[typing.Any]):
    """
    Replace all variables in a node s-expression with their referenced literal
    value.

    Args:
      analysis: A dictionary corresponding to the values referenced in the
      given s-expression.
      rule: An s-expression list in the form of [operator, arg1, arg2, ...].

    Yields:
      A node expression with referenced values replaced with their literal values.

    Examples:
      >>> eval_variables({a: 1}, [>, :a, 2])
      [>, 1, 2]
    """

    def _eval(n):
        if variable.is_variable(n):
            return variable.get_variable_value(analyses, n)
        else:
            return n

    return list(map(functional.recursive_apply(fn.F(eval_variables, analyses), _eval), rule))


def evaluate_rule(node: typing.List[typing.Any]) -> bool:
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
    args = list(map(functional.recursive_apply(evaluate_rule), iters.tail(node)))
    f = OPERATORS[node[0]]
    return f(*args)
