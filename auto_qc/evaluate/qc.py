import typing

from auto_qc import node, object, variable


def evaluate(state: object.AutoQC) -> object.AutoQCEvaluation:
    """
    Build a dict QC containing all data about this evaluation.
    """
    nodes = [build_qc_node(x, state.data) for x in state.thresholds]
    failure_codes = {x["fail_code"] for x in nodes if not x["pass"]}
    evaluation = object.AutoQCEvaluation(
        is_pass=not failure_codes,
        fail_codes=list(failure_codes),
        evaluation=nodes,
    )
    return evaluation


def create_variable_dict(input_node, analysis):
    return dict(
        list(
            map(
                lambda x: (x[1:], variable.get_variable_value(analysis, x)),
                variable.get_variable_names(input_node),
            )
        )
    )


def does_node_pass(input_node: object.ThresholdNode, analysis):
    """
    Evaluates the PASS/FAIL status of a QC node.

    Args:
      input_node: An s-expression list in the form of [operator, arg1, arg2, ...].

      analysis (dict): A dictionary containing to the variables referenced in the
      given QC node

    Yields:
      True if the node passes QC, False if it fails QC.
    """
    return node.evaluate_rule(node.eval_variables(analysis, input_node.rule))


def create_qc_message(
    is_pass: bool, input_node: object.ThresholdNode, variables: typing.Dict[str, typing.Any]
):
    if is_pass:
        return input_node.pass_msg.format(**variables)
    return input_node.fail_msg.format(**variables)


def build_qc_node(input_node: object.ThresholdNode, analysis: typing.Dict[str, typing.Any]):
    is_pass = does_node_pass(input_node, analysis)
    variables = create_variable_dict(input_node, analysis)

    return {
        "variables": variables,
        "name": input_node.name,
        "pass": is_pass,
        "fail_code": input_node.fail_code,
        "tags": input_node.tags or [],
        "message": create_qc_message(is_pass, input_node, variables),
    }
