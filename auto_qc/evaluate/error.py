import fn.iters as it
import string   as st
from fn import F, _

import funcy

import auto_qc.version         as ver
import auto_qc.variable        as var
import auto_qc.node            as nd
import auto_qc.util.functional as fn


def variable_error_message(variable):
    msg = "No matching metric '{}' found."
    return msg.format(variable)


def operator_error_message(operator):
    msg = "Unknown operator '{}.'"
    return msg.format(operator)

def fail_code_error_message(node):
    msg = "The QC entry '{}' is missing a failure code"
    return msg.format(funcy.get_in(node, [0, 'name']))

def generator_error_string(f, xs):
    return st.join(list(map(f, xs)), "\n")

def check_version_number(threshold, status):
    version =  ver.major_version()
    threshold_version = str(status[threshold]['metadata']['version']['auto-qc'])

    if  version != threshold_version.split('.')[0]:
        status['error'] = """\
Incompatible threshold file syntax: {}.
Please update the syntax to version >= {}.0.0.
        """.format(threshold_version, version)

    return status


def check_node_paths(nodes, analyses, status):
    """
    Checks that all variable paths listed in the QC file are valid. Sets an error
    message in the status if not.
    """
    variables = var.get_variable_names(status[nodes]['thresholds'])
    f = funcy.partial(var.is_variable_path_valid, status[analyses])
    errors = set(funcy.remove(f, variables))

    if len(errors) > 0:
        status['error'] = generator_error_string(variable_error_message, errors)

    return status


def check_operators(node_ref, status):
    """
    Checks that all operators listed in the QC file are valid. Sets an error
    message in the status if not.
    """
    operators = funcy.mapcat(nd.get_all_operators, status[node_ref]['thresholds'])
    errors    = funcy.remove(nd.is_operator, operators)

    if len(errors) > 0:
        status['error'] = generator_error_string(operator_error_message, errors)

    return status


def check_failure_codes(node_ref, status):
    """
    Checks all QC entries have defined failure codes
    """
    errors = funcy.remove(lambda x: 'fail_code' in x[0], status[node_ref]['thresholds'])
    if len(errors) > 0:
        status['error'] = generator_error_string(fail_code_error_message, errors)
    return status
