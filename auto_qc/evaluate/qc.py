from auto_qc import objects
from auto_qc import variable
from auto_qc import node
import functools

import funcy


def evaluate(destination: str, thresholds, analysis, status) -> objects.AutoqcEvaluation:
    """
    Build a dict QC containing all data about this evaluation.
    """
    f = funcy.rpartial(build_qc_node, status[analysis])
    nodes = list(map(f, status[thresholds]["thresholds"]))
    failures = funcy.rcompose(
        functools.partial(funcy.remove, does_pass),
        functools.partial(map, fail_code),
        funcy.distinct,
    )(nodes)

    evaluation = objects.AutoqcEvaluation(
        is_pass=not list(failures),
        fail_codes=list(failures),
        evaluation=nodes,
    )

    status[destination] = evaluation
    return status


def does_pass(node):
    return node["pass"]


def fail_code(node):
    return node["fail_code"]


def create_variable_dict(input_node, analysis):
    f = lambda x: (x[1:], variable.get_variable_value(analysis, x))
    return dict(list(map(f, variable.get_variable_names(input_node))))


def does_node_pass(input_node, analysis):
    """
    Evaluates the PASS/FAIL status of a QC node.

    Args:
      node (list): An s-expression list in the form of [operator, arg1, arg2, ...].

      analysis (dict): A dictionary containing to the variables referenced in the
      given QC node

    Yields:
      True if the node passes QC, False if it fails QC.
    """
    return node.eval(node.eval_variables(analysis, input_node))


def create_qc_message(is_pass, input_node, variables):
    x = "pass_msg" if is_pass else "fail_msg"
    return funcy.get_in(input_node, [0, x]).format(**variables)


def build_qc_node(input_node, analysis):
    is_pass = does_node_pass(input_node, analysis)
    variables = create_variable_dict(input_node, analysis)

    return {
        "variables": variables,
        "name": funcy.get_in(input_node, [0, "name"]),
        "pass": is_pass,
        "fail_code": funcy.get_in(input_node, [0, "fail_code"]),
        "tags": funcy.get_in(input_node, [0, "tags"]) or [],
        "message": create_qc_message(is_pass, input_node, variables),
    }
