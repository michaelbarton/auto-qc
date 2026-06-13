import typing

from auto_qc.util import functional


def is_variable(var: str) -> bool:
    """
    Is the string a variable reference?
    """
    return isinstance(var, str) and var.startswith(":")


def is_variable_path_valid(data: dict[str, typing.Any], path: str) -> bool:
    """
    Does the variable path have a matching path in the analysis?

    Checks for the existence of the key path rather than the truthiness of the
    value so that a legitimately null/zero/false value is not reported as a
    missing metric.
    """
    node = data
    for key in path[1:].split("/"):
        if not isinstance(node, dict) or key not in node:
            return False
        node = node[key]
    return True


def resolve(data: dict[str, typing.Any], path: str) -> typing.Any:
    """Return the raw value at ``path``, or ``None`` if any key is missing.

    Lists are returned as-is, so the engine can use a referenced list directly
    (e.g. as the right-hand side of ``is_in``).
    """
    return functional.get_in(data, path[1:].split("/"))


def get_variable_names(qc_node: list[typing.Any]) -> list[str]:
    return [x for x in functional.flatten(qc_node) if is_variable(x)]
