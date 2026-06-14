import typing
from functools import reduce


def flatten(n: list[typing.Any]) -> list[typing.Any]:
    def _f(acc: list[typing.Any], x: typing.Any) -> list[typing.Any]:
        if isinstance(x, list):
            return acc + flatten(x)
        else:
            return acc + [x]

    return reduce(_f, n, [])


def get_in(data: typing.Any, keys: typing.Iterable[str]) -> typing.Any:
    """
    Return the value at the nested key path, or None if any key is missing.
    """
    for key in keys:
        if not isinstance(data, dict) or key not in data:
            return None
        data = data[key]
    return data
