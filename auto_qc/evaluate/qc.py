import typing

from auto_qc import models, node, variable
from auto_qc.exception import AutoQCError


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
    return {
        name[1:]: variable.resolve(analysis, name)
        for name in variable.get_variable_names(input_node.rule)
    }


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
    """Evaluate one threshold, returning its pass/fail state and explanation.

    Raises:
        AutoQCError: If the rule cannot be evaluated (e.g. it compares a number
            to text). The rule's name and fail code are added for context.
    """
    try:
        trace = node.evaluate(input_node.rule, analysis)
    except AutoQCError as err:
        raise AutoQCError(f"Rule '{input_node.name}' ({input_node.fail_code}): {err}") from err

    is_pass = bool(trace.result)
    variables = create_variable_dict(input_node, analysis)

    return {
        "variables": variables,
        "name": input_node.name,
        "pass": is_pass,
        "fail_code": input_node.fail_code,
        "tags": input_node.tags or [],
        "message": create_qc_message(is_pass, input_node, variables),
        "explain": trace.to_dict(),
    }
