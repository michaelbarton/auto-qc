import typing

import funcy


def is_variable(var: str) -> bool:
    """
    Is the string a variable reference?
    """
    return isinstance(var, str) and var.startswith(":")


def is_variable_path_valid(data: typing.Dict[str, typing.Any], path: str) -> bool:
    """
    Does the variable path have a matching path in the analysis?
    """
    value = get_variable_value(data, path)
    if value is None:
        return False
    return True


def get_variable_value(data: typing.Dict[str, typing.Any], path: str) -> typing.Any:
    """Get variable's value by traversing its path into the data file.

    Args:
        data: Source data to fetch value from.
        path: Path to value.

    Returns:
        The value of the variable pointed to by the path.

    Notes:
        If the value is a list, the `list` string is appended to the start of the list. This is necessary because
        lists are treated as SEXPs where the first node in each list is an operator.

    """
    drop_colon = path[1:]
    path_array = drop_colon.split("/")
    var_value = funcy.get_in(data, path_array)
    if isinstance(var_value, list):
        return ["list", *var_value]
    return var_value


def get_variable_names(qc_node):
    return list(funcy.select(is_variable, funcy.flatten(qc_node)))
