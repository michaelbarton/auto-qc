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


def _check_node_operators(expr: typing.Any, rule_position: bool, errors: list[str]) -> None:
    """Validate operators in ``expr``, knowing whether a rule is expected here.

    In *rule position* (the top of a threshold, or an argument to ``and`` /
    ``or`` / ``not``) a list must be led by a known operator; a list that isn't
    is reported as an unknown operator, with a did-you-mean hint. In *value
    position* a non-operator list is a legitimate literal list (e.g. the set for
    ``is_in``), so only its nested applications are checked.
    """
    if not isinstance(expr, list) or not expr:
        return

    head = expr[0]
    if node.is_operator(head):
        argument_rule_position = head.lower() in node.RULE_POSITION_OPERATORS
        for argument in expr[1:]:
            _check_node_operators(argument, argument_rule_position, errors)
    elif rule_position:
        message = f"Unknown operator '{head}.'{_suggest(str(head), node.OPERATORS)}"
        if message not in errors:
            errors.append(message)
    else:
        for element in expr:
            _check_node_operators(element, False, errors)


def check_operators(state: models.AutoQC) -> None:
    """
    Checks that all operators listed in the QC file are valid. Raises an error
    listing each unknown operator, with a suggestion for the closest match.
    """
    errors: list[str] = []
    for threshold in state.thresholds:
        _check_node_operators(threshold.rule, rule_position=True, errors=errors)

    if errors:
        raise exception.AutoQCError("\n".join(errors))


def _check_node_arity(expr: typing.Any, errors: list[str]) -> None:
    """Validate operator argument counts throughout ``expr``."""
    if not isinstance(expr, list) or not expr:
        return

    if node.is_operator(expr[0]):
        op = node.OPERATORS[expr[0].lower()]
        given = len(expr) - 1
        if given < op.min_args or (op.max_args is not None and given > op.max_args):
            message = node.arity_message(expr[0], op, given)
            if message not in errors:
                errors.append(message)
        for argument in expr[1:]:
            _check_node_arity(argument, errors)
    else:
        for element in expr:
            _check_node_arity(element, errors)


def check_arity(state: models.AutoQC) -> None:
    """
    Checks that every operator is given a valid number of arguments. Raises an
    error listing each operator called with the wrong arity.
    """
    errors: list[str] = []
    for threshold in state.thresholds:
        _check_node_arity(threshold.rule, errors)

    if errors:
        raise exception.AutoQCError("\n".join(errors))
