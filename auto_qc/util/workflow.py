from functools import partial, wraps
from inspect import getargspec
from functools import reduce

from auto_qc import objects


def thread_status(functions, status):
    def reducer(status, item):
        f = item[0]
        args = item[1] if len(item) > 1 else []

        if "error" in status:
            raise objects.AutoQCEvaluationError(status["error"])
        else:
            parameterised = reduce(partial, args, f)
            return parameterised(status)

    return reduce(reducer, functions, status)


def validate_status_key(status_key):
    def decorator(func):
        def check_keys_in_args(*args):
            status = args[-1]
            key = args[getargspec(func).args.index(status_key)]

            if key not in status:
                status["error"] = "Internal error - key '{}' not found in method '{}'.".format(
                    key, func.__name__
                )
                return status
            else:
                return func(*args)

        return wraps(func)(check_keys_in_args)

    return decorator
