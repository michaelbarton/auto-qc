import typing

import pydantic

from auto_qc import exception, models
from auto_qc.evaluate import error, qc


def build(thresholds: dict[str, typing.Any], data: dict[str, typing.Any]) -> models.AutoQC:
    """Validate the thresholds and data and return the checked ``AutoQC`` state.

    Args:
        thresholds: Parsed thresholds document (``version`` and ``thresholds``).
        data: Parsed data document of metrics to evaluate.

    Returns:
        A validated :class:`~auto_qc.models.AutoQC` ready to be evaluated.

    Raises:
        AutoQCError: If the documents are invalid, reference an unknown metric
            path, or use an unknown operator. Validation failures from pydantic
            are wrapped so that callers only ever need to catch ``AutoQCError``.
    """
    try:
        state = models.AutoQC(data=data, **thresholds)
    except pydantic.ValidationError as err:
        raise exception.AutoQCError(str(err)) from err

    error.check_node_paths(state)
    error.check_operators(state)
    return state


def run(thresholds: dict[str, typing.Any], data: dict[str, typing.Any]) -> models.AutoQCEvaluation:
    """Evaluate a set of thresholds against a data document.

    Args:
        thresholds: Parsed thresholds document (``version`` and ``thresholds``).
        data: Parsed data document of metrics to evaluate.

    Returns:
        An :class:`~auto_qc.models.AutoQCEvaluation` describing the overall
        pass/fail state and the result of every rule.

    Raises:
        AutoQCError: If the input documents are invalid in any way.
    """
    return qc.evaluate(build(thresholds, data))
