from functools import reduce


def identity(x):
    """
    The identity function.
    """
    return x


def empty_list(*args):
    """
    Returns an empty list, whatever the arguments.
    """
    return []


def flatten(n):
    def _f(acc, x):
        if isinstance(x, list):
            return acc + flatten(x)
        else:
            return acc + [x]

    return reduce(_f, n, [])


def recursive_apply(list_func, atom_func=identity):
    """
    Creates a function which applies either of the two given functions: the first
    to a list, and the second to atoms within a list. Used to walk over deeply
    nested s-expressions.
    """

    def _f(x):
        if isinstance(x, list):
            return list_func(x)
        else:
            return atom_func(x)

    return _f
