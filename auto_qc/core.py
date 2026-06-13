import functools
import typing

import pydantic

from auto_qc import exception, models
from auto_qc.evaluate import error, qc

_F = typing.TypeVar("_F", bound=typing.Callable[..., typing.Any])


def _recursion_guarded(func: _F) -> _F:
    """Convert a ``RecursionError`` into an :class:`AutoQCError`.

    Rules and data are walked recursively, so a document nested absurdly
    deeply — or one whose YAML aliases form a cycle (``&a [*a]``) — would
    otherwise escape as a raw ``RecursionError``.
    """

    @functools.wraps(func)
    def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        try:
            return func(*args, **kwargs)
        except RecursionError:
            raise exception.AutoQCError(
                "The documents are nested too deeply to evaluate. "
                "Check for recursive YAML anchors/aliases."
            ) from None

    return typing.cast(_F, wrapper)


def _validated(thresholds: typing.Any, data: dict[str, typing.Any]) -> models.AutoQC:
    """Validate a parsed thresholds document, wrapping every failure mode.

    Raises:
        AutoQCError: If the document is not a mapping or fails validation.
    """
    if not isinstance(thresholds, dict):
        raise exception.AutoQCError(
            "The thresholds document must be a YAML/JSON mapping with 'version' "
            f"and 'thresholds' keys, but it parsed as {type(thresholds).__name__}."
        )
    try:
        return models.AutoQC.model_validate({**thresholds, "data": data})
    except pydantic.ValidationError as err:
        raise exception.AutoQCError(str(err)) from err


@_recursion_guarded
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
    state = _validated(thresholds, data)
    error.check_node_paths(state)
    error.check_operators(state)
    error.check_arity(state)
    error.check_messages(state)
    return state


@_recursion_guarded
def build_thresholds(thresholds: dict[str, typing.Any]) -> models.AutoQC:
    """Validate a thresholds document on its own, without a data document.

    Used by ``--lint``, which reasons about the rules themselves and so needs no
    metrics. The operator and arity checks still run, but the metric-path check
    is skipped — there is no data to resolve pointers against.

    Args:
        thresholds: Parsed thresholds document (``version`` and ``thresholds``).

    Returns:
        A validated :class:`~auto_qc.models.AutoQC` whose ``data`` is empty.

    Raises:
        AutoQCError: If the document is invalid or uses an unknown operator.
    """
    state = _validated(thresholds, {})
    error.check_operators(state)
    error.check_arity(state)
    error.check_messages(state)
    return state


@_recursion_guarded
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
