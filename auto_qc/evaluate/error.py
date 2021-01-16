import funcy

from auto_qc import exception, node, object, variable


def check_node_paths(state: object.AutoQC) -> None:
    """
    Checks that all variable paths listed in the QC file are valid. Sets an error
    message in the status if not.
    """

    invalid_variables = {
        x
        for x in variable.get_variable_names(state.thresholds)
        if not variable.is_variable_path_valid(state.data, x)
    }

    if invalid_variables:
        raise exception.AutoQCError(
            "\n".join([f"No matching metric path '{x}' found in data." for x in invalid_variables])
        )


def check_operators(state: object.AutoQC) -> None:
    """
    Checks that all operators listed in the QC file are valid. Sets an error
    message in the status if not.
    """
    operators = funcy.mapcat(node.get_all_operators, state.thresholds)
    errors = {node.is_operator(x) for x in operators}

    if errors:
        raise exception.AutoQCError("\n".join([f"Unknown operator '{x}.'" for x in errors]))
