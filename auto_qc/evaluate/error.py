import difflib
import itertools
import typing

from auto_qc import exception, models, node, variable


def _all_metric_paths(data: dict[str, typing.Any], prefix: str = "") -> list[str]:
    """Enumerate every ``/``-separated leaf path present in the data document."""
    paths: list[str] = []
    for key, value in data.items():
        path = f"{prefix}/{key}" if prefix else key
        if isinstance(value, dict) and value:
            paths.extend(_all_metric_paths(value, path))
        else:
            paths.append(path)
    return paths


def _suggest(candidate: str, options: typing.Iterable[str]) -> str:
    """Return a ' Did you mean ...?' hint for the closest matching option."""
    matches = difflib.get_close_matches(candidate, list(options), n=1)
    return f" Did you mean '{matches[0]}'?" if matches else ""


def check_node_paths(state: models.AutoQC) -> None:
    """
    Checks that all variable paths listed in the QC file are valid. Raises an
    error listing each missing path, with a suggestion for the closest match.
    """

    variable_names = list(
        itertools.chain.from_iterable(variable.get_variable_names(x.rule) for x in state.thresholds)
    )
    invalid_variables = {
        x for x in variable_names if not variable.is_variable_path_valid(state.data, x)
    }

    if invalid_variables:
        valid_paths = [f":{path}" for path in _all_metric_paths(state.data)]
        messages = [
            f"No matching metric path '{x}' found in data.{_suggest(x, valid_paths)}"
            for x in sorted(invalid_variables)
        ]
        raise exception.AutoQCError("\n".join(messages))


def check_operators(state: models.AutoQC) -> None:
    """
    Checks that all operators listed in the QC file are valid. Raises an error
    listing each unknown operator, with a suggestion for the closest match.
    """
    operators = list(
        itertools.chain.from_iterable(node.get_all_operators(x.rule) for x in state.thresholds)
    )
    errors = {x for x in operators if not node.is_operator(x)}

    if errors:
        messages = [
            f"Unknown operator '{x}.'{_suggest(str(x), node.OPERATORS)}" for x in sorted(errors)
        ]
        raise exception.AutoQCError("\n".join(messages))
