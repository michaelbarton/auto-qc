import funcy

from auto_qc import exception, node, object, variable


def check_node_paths(state: object.AutoQC) -> None:
    """
    Checks that all variable paths listed in the QC file are valid. Sets an error
    message in the status if not.
    """

    variable_names = funcy.flatten(
        [variable.get_variable_names(x.rule) for x in state.thresholds]
    )
    invalid_variables = {
        x for x in variable_names if not variable.is_variable_path_valid(state.data, x)
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
    operators = funcy.flatten([node.get_all_operators(x.rule) for x in state.thresholds])
    errors = {x for x in operators if not node.is_operator(x)}

    if errors:
        raise exception.AutoQCError("\n".join([f"Unknown operator '{x}.'" for x in errors]))
