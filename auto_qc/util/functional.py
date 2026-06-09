import typing
from functools import reduce

T = typing.TypeVar("T")


def identity(x: T) -> T:
    """
    The identity function.
    """
    return x


def empty_list(*args: typing.Any) -> list[typing.Any]:
    """
    Returns an empty list, whatever the arguments.
    """
    return []


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


def recursive_apply(
    list_func: typing.Callable[[list[typing.Any]], typing.Any],
    atom_func: typing.Callable[[typing.Any], typing.Any] = identity,
) -> typing.Callable[[typing.Any], typing.Any]:
    """
    Creates a function which applies either of the two given functions: the first
    to a list, and the second to atoms within a list. Used to walk over deeply
    nested s-expressions.
    """

    def _f(x: typing.Any) -> typing.Any:
        if isinstance(x, list):
            return list_func(x)
        else:
            return atom_func(x)

    return _f
