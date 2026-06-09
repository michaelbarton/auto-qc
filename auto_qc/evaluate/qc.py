import typing

from auto_qc import models, node, variable


def evaluate(state: models.AutoQC) -> models.AutoQCEvaluation:
    """
    Build a dict QC containing all data about this evaluation.
    """
    nodes = [build_qc_node(x, state.data) for x in state.thresholds]
    failure_codes = sorted({x["fail_code"] for x in nodes if not x["pass"]})
    evaluation = models.AutoQCEvaluation(
        is_pass=not failure_codes,
        fail_codes=failure_codes,
        evaluation=nodes,
    )
    return evaluation


def create_variable_dict(
    input_node: models.ThresholdNode, analysis: dict[str, typing.Any]
) -> dict[str, typing.Any]:
    return dict(
        list(
            map(
                lambda x: (x[1:], variable.get_variable_value(analysis, x)),
                variable.get_variable_names(input_node.rule),
            )
        )
    )


def does_node_pass(input_node: models.ThresholdNode, analysis: dict[str, typing.Any]) -> bool:
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
    is_pass: bool, input_node: models.ThresholdNode, variables: dict[str, typing.Any]
) -> str:
    msg = input_node.pass_msg if is_pass else input_node.fail_msg
    if msg is None:
        return ""
    return msg.format(**variables)


def build_qc_node(
    input_node: models.ThresholdNode, analysis: dict[str, typing.Any]
) -> dict[str, typing.Any]:
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
