import pytest

from auto_qc import node
from auto_qc.evaluate import exception


def _eval(expr, data=None):
    return node.evaluate(expr, data or {}).result


def test_eval_greater_than_with_two_literals():
    assert _eval(["greater_than", 2, 1])


def test_eval_less_than_with_two_literals():
    assert not _eval(["less_than", 2, 1])


def test_operators_are_case_insensitive():
    assert node.is_operator("OR")
    assert node.is_operator("Greater_Than")
    assert _eval(["AND", ["GREATER_THAN", 2, 1], ["greater_than", 3, 1]])


def test_non_string_is_not_an_operator():
    assert not node.is_operator(5)


def test_eval_true_with_nested_lists():
    assert _eval(["and", ["greater_than", 2, 1], ["greater_than", 2, 1]])


def test_eval_false_with_nested_lists():
    assert not _eval(["and", ["greater_than", 1, 2], ["greater_than", 1, 2]])


def test_eval_with_list_operator():
    assert _eval(["list", 2, 1]) == [2, 1]


def test_eval_with_in():
    assert _eval(["is_in", 2, ["list", 2, 1]])


def test_eval_with_is_not_in():
    assert not _eval(["is_not_in", 2, ["list", 2, 1]])


def test_is_in_accepts_a_plain_literal_list():
    """A list not led by an operator is a literal list, no ``list`` keyword needed."""
    assert _eval(["is_in", "PCR-free", ["Low Input DNA", "PCR-free"]])
    assert not _eval(["is_in", "Standard DNA", ["Low Input DNA", "PCR-free"]])


def test_eval_resolves_variables():
    assert not _eval(["less_than", ":ref/metric_1", 1], {"ref": {"metric_1": 2}})


def test_eval_resolves_variables_in_nested_lists():
    data = {"ref": {"metric_1": 2}}
    assert not _eval(["and", ["less_than", ":ref/metric_1", 1], ["greater_than", 0, 1]], data)


def test_between_is_inclusive():
    assert _eval(["between", 5, 1, 10])
    assert _eval(["between", 1, 1, 10])
    assert not _eval(["between", 11, 1, 10])


def test_arithmetic_feeds_a_comparison():
    data = {"reads": {"mapped": 95, "total": 100}}
    assert _eval(["greater_than", ["divide", ":reads/mapped", ":reads/total"], 0.9], data)
    assert _eval(["add", 1, 2, 3]) == 6
    assert _eval(["multiply", 2, 3, 4]) == 24
    assert _eval(["subtract", 10, 3]) == 7


def test_string_predicates():
    data = {"sample": {"id": "SRX-4521"}}
    assert _eval(["matches", ":sample/id", "^SRX-"], data)
    assert _eval(["starts_with", ":sample/id", "SRX"], data)
    assert _eval(["ends_with", ":sample/id", "4521"], data)
    assert _eval(["length", ":sample/id"], data) == 8


def test_type_mismatch_raises_evaluation_error_not_typeerror():
    with pytest.raises(exception.EvaluationError):
        _eval(["greater_than", "text", 3])


def test_comparing_missing_value_raises_evaluation_error():
    with pytest.raises(exception.EvaluationError):
        _eval(["greater_than", ":missing", 3], {})


def test_divide_by_zero_raises_evaluation_error():
    with pytest.raises(exception.EvaluationError, match="divided by zero"):
        _eval(["divide", 1, 0])


def test_wrong_arity_raises_evaluation_error():
    with pytest.raises(exception.EvaluationError):
        _eval(["not", True, False])


def test_trace_to_dict_describes_the_evaluation():
    trace = node.evaluate(["greater_than", ":depth", 30], {"depth": 18.6})
    assert trace.to_dict() == {
        "operator": "greater_than",
        "result": False,
        "args": [
            {"variable": ":depth", "value": 18.6},
            {"literal": 30},
        ],
    }
