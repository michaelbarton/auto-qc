from functools import partial, wraps
from inspect   import getargspec
from functools import reduce

def thread_status(functions, status):

    def reducer(status, item):
        f    = item[0]
        args = item[1] if len(item) > 1 else []

        if 'error' in status:
            return status
        else:
            parameterised = reduce(partial, args, f)
            return parameterised(status)

    return reduce(reducer, functions, status)

def exit_if_error(status):
    if 'error' in status:
        from sys import stderr
        stderr.write(status['error'] + "\n")
        exit(1)

def exit_status(status):
    '''
    Exit code based on the status
    '''
    exit_if_error(status)
    exit(0)

def validate_status_key(status_key):

    def decorator(func):

        def check_keys_in_args(*args):
            status = args[-1]
            key = args[getargspec(func).args.index(status_key)]

            if key not in status:
                status['error'] = \
                        "Internal error - key '{}' not found in method '{}'.".format(key, func.__name__)
                return status
            else:
                return func(*args)

        return wraps(func)(check_keys_in_args)

    return decorator
