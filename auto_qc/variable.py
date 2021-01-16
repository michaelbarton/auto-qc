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
    """
    Get variable's value by traversing its path into the analysis
    """
    drop_colon = path[1:]
    path_array = drop_colon.split("/")
    return funcy.get_in(data, path_array)


def get_variable_names(qc_node):
    return list(funcy.select(is_variable, funcy.flatten(qc_node)))
