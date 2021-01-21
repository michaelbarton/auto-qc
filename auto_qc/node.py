import operator as op

import typing

from auto_qc import object

import funcy
from fn import F
from fn import iters as it

import auto_qc.util.functional as fn
import auto_qc.variable as var

OPERATORS = {
    "greater_than": op.gt,
    "greater_equal_than": op.ge,
    "less_than": op.lt,
    "less_equal_than": op.le,
    "equals": op.eq,
    "not_equals": op.ne,
    "and": lambda *args: all(args),
    "or": lambda *args: any(args),
    "not": lambda x: not x,
    "is_in": lambda x, y: x in y,
    "is_not_in": lambda x, y: x not in y,
    "list": lambda *args: list(args),
}


def is_operator(v):
    return op.contains(list(OPERATORS.keys()), v)


def operator(v):
    return OPERATORS[v]


def has_doc_dict(qc_node):
    return isinstance(it.head(qc_node), dict)


def get_all_operators(qc_node):
    """
    Returns all operators listed in a QC node
    """

    def _walk_node(n):
        if has_doc_dict(n):
            return _walk_node(list(it.tail(n)))
        else:
            operator = it.head(n)
            rest = it.tail(n)
            return [operator, *f(rest)]

    f = funcy.partial(map, fn.recursive_apply(_walk_node, fn.empty_list))

    return fn.flatten(_walk_node(qc_node))


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
        if var.is_variable(n):
            return var.get_variable_value(analyses, n)
        else:
            return n

    return list(map(fn.recursive_apply(F(eval_variables, analyses), _eval), rule))


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
    args = list(map(fn.recursive_apply(evaluate_rule), it.tail(node)))
    f = operator(it.head(node))
    return f(*args)
