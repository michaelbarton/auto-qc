from nose import tools

from auto_qc import node


def test_eval_greater_than_with_two_literals():
    n = ["greater_than", 2, 1]
    tools.assert_true(node.evaluate_rule(n))


def test_eval_less_than_with_two_literals():
    n = ["less_than", 2, 1]
    tools.assert_false(node.evaluate_rule(n))


def test_eval_true_with_nested_lists():
    n = ["and", ["greater_than", 2, 1], ["greater_than", 2, 1]]
    tools.assert_true(node.evaluate_rule(n))


def test_eval_false_with_nested_lists():
    n = ["and", ["greater_than", 1, 2], ["greater_than", 1, 2]]
    tools.assert_false(node.evaluate_rule(n))


def test_eval_with_list():
    n = ["list", 2, 1]
    tools.assert_equal([2, 1], node.evaluate_rule(n))


def test_eval_with_in():
    n = ["is_in", 2, ["list", 2, 1]]
    tools.assert_true(node.evaluate_rule(n))


def test_eval_with_is_not_in():
    n = ["is_not_in", 2, ["list", 2, 1]]
    tools.assert_false(node.evaluate_rule(n))


def test_eval_variable_with_literal_and_variable():
    n = ["less_than", ":ref/metric_1", 1]
    a = {"ref": {"metric_1": 2}}
    tools.assert_equal(["less_than", 2, 1], node.eval_variables(a, n))


def test_eval_variable_with_nested_list():
    n = ["and", ["less_than", ":ref/metric_1", 1], ["less_than", ":ref/metric_1", 1]]
    a = {"ref": {"metric_1": 2}}

    tools.assert_equal(["and", ["less_than", 2, 1], ["less_than", 2, 1]], node.eval_variables(a, n))


def test_eval_with_doc_string():
    n = [{"name": "my threshold"}, "greater_than", 2, 1]
    tools.assert_true(node.evaluate_rule(n))


def test_get_all_operators_with_single_threshold():
    n = ["less_than", 2, 1]
    tools.assert_equal(node.get_all_operators(n), ["less_than"])


def test_get_all_operators_with_nested_threshold():
    n = ["and", ["or", ["less_than", 2, 1]]]
    tools.assert_equal(node.get_all_operators(n), ["and", "or", "less_than"])


def test_get_all_operators_with_doc_string():
    n = [{"name": "my qc threshold"}, "less_than", 2, 1]
    tools.assert_equal(node.get_all_operators(n), ["less_than"])
