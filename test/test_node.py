from auto_qc import node


def test_eval_greater_than_with_two_literals():
    n = ["greater_than", 2, 1]
    assert node.evaluate_rule(n)


def test_eval_less_than_with_two_literals():
    n = ["less_than", 2, 1]
    assert not node.evaluate_rule(n)


def test_operators_are_case_insensitive():
    assert node.is_operator("OR")
    assert node.is_operator("Greater_Than")
    assert node.evaluate_rule(["AND", ["GREATER_THAN", 2, 1], ["greater_than", 3, 1]])


def test_non_string_is_not_an_operator():
    assert not node.is_operator(5)


def test_eval_true_with_nested_lists():
    n = ["and", ["greater_than", 2, 1], ["greater_than", 2, 1]]
    assert node.evaluate_rule(n)


def test_eval_false_with_nested_lists():
    n = ["and", ["greater_than", 1, 2], ["greater_than", 1, 2]]
    assert not node.evaluate_rule(n)


def test_eval_with_list():
    n = ["list", 2, 1]
    assert [2, 1] == node.evaluate_rule(n)


def test_eval_with_in():
    n = ["is_in", 2, ["list", 2, 1]]
    assert node.evaluate_rule(n)


def test_eval_with_is_not_in():
    n = ["is_not_in", 2, ["list", 2, 1]]
    assert not node.evaluate_rule(n)


def test_eval_variable_with_literal_and_variable():
    n = ["less_than", ":ref/metric_1", 1]
    a = {"ref": {"metric_1": 2}}
    assert ["less_than", 2, 1] == node.eval_variables(a, n)


def test_eval_variable_with_nested_list():
    n = ["and", ["less_than", ":ref/metric_1", 1], ["less_than", ":ref/metric_1", 1]]
    a = {"ref": {"metric_1": 2}}

    assert ["and", ["less_than", 2, 1], ["less_than", 2, 1]] == node.eval_variables(a, n)


def test_eval_with_doc_string():
    n = ["greater_than", 2, 1]
    assert node.evaluate_rule(n)


def test_get_all_operators_with_single_threshold():
    n = ["less_than", 2, 1]
    assert node.get_all_operators(n) == ["less_than"]


def test_get_all_operators_with_nested_threshold():
    n = ["and", ["or", ["less_than", 2, 1]]]
    assert node.get_all_operators(n) == ["and", "or", "less_than"]


def test_get_all_operators_with_doc_string():
    n = ["less_than", 2, 1]
    assert node.get_all_operators(n) == ["less_than"]
