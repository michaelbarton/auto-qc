from fn import iters as it
import funcy as fn
from functools import reduce

def is_variable(var):
    """
    Is the string a variable reference?
    """
    return isinstance(var, str) and it.head(var) == ':'

def is_variable_path_valid(analysis, path):
    """
    Does the variable path have a matching path in the analysis?
    """
    try:
        get_variable_value(analysis, path)
    except KeyError as e:
        return False
    return True

def get_variable_value(analysis, path):
    """
    Get variable's value by traversing its path into the analysis
    """
    drop_colon = path[1:]
    path_array = drop_colon.split('/')
    return reduce(lambda a, k: a[k], path_array, analysis['data'])

def get_variable_names(qc_node):
    return fn.select(is_variable, fn.flatten(qc_node))
