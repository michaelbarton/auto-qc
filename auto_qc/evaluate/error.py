import funcy

from auto_qc import node, variable


def variable_error_message(variable):
    msg = "No matching metric path '{}' found in data."
    return msg.format(variable)


def operator_error_message(operator):
    msg = "Unknown operator '{}.'"
    return msg.format(operator)


def fail_code_error_message(node):
    msg = "The QC entry '{}' is missing a failure code"
    return msg.format(funcy.get_in(node, [0, "name"]))


def generator_error_string(f, xs):
    return "\n".join([f(x) for x in xs])


def check_node_paths(nodes, analyses, status):
    """
    Checks that all variable paths listed in the QC file are valid. Sets an error
    message in the status if not.
    """
    variables = variable.get_variable_names(status[nodes]["thresholds"])
    f = funcy.partial(variable.is_variable_path_valid, status[analyses])
    errors = set(funcy.remove(f, variables))

    if len(errors) > 0:
        status["error"] = generator_error_string(variable_error_message, errors)

    return status


def check_operators(node_ref, status):
    """
    Checks that all operators listed in the QC file are valid. Sets an error
    message in the status if not.
    """
    operators = funcy.mapcat(node.get_all_operators, status[node_ref]["thresholds"])
    errors = list(funcy.remove(node.is_operator, operators))

    if len(errors) > 0:
        status["error"] = generator_error_string(operator_error_message, errors)

    return status


def check_failure_codes(node_ref, status):
    """
    Checks all QC entries have defined failure codes
    """
    errors = list(funcy.remove(lambda x: "fail_code" in x[0], status[node_ref]["thresholds"]))
    if len(errors) > 0:
        status["error"] = generator_error_string(fail_code_error_message, errors)
    return status


class AutoQCError(Exception):
    """Auto QC generic error type."""
    pass


class VersionNumberError(AutoQCError):
    """Incorrect version number error."""
    pass