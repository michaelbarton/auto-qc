from auto_qc import models
from auto_qc.evaluate import qc

METADATA = {"name": "Example test", "pass_msg": "passes", "fail_msg": "fails", "fail_code": "ERR01"}


def test_build_passing_qc_node_with_two_literals():
    threshold_node = models.ThresholdNode(
        **{
            **METADATA,
            "rule": ["greater_than", 2, 1],
        }
    )

    expected = {
        "variables": {},
        "name": "Example test",
        "pass": True,
        "tags": [],
        "fail_code": "ERR01",
        "message": "passes",
        "explain": {
            "operator": "greater_than",
            "result": True,
            "args": [{"literal": 2}, {"literal": 1}],
            "margin": 1.0,
        },
    }
    assert qc.build_qc_node(threshold_node, {}) == expected


def test_build_failing_qc_node_with_literal_and_variable():
    threshold_node = models.ThresholdNode(
        **{
            **METADATA,
            "rule": ["less_than", ":ref/metric_1", 1],
        }
    )

    a = {"ref": {"metric_1": 2}}

    expected = {
        "variables": {"ref/metric_1": 2},
        "name": "Example test",
        "pass": False,
        "tags": [],
        "fail_code": "ERR01",
        "message": "fails",
        "explain": {
            "operator": "less_than",
            "result": False,
            "args": [{"variable": ":ref/metric_1", "value": 2}, {"literal": 1}],
            "margin": -1.0,
        },
    }
    assert qc.build_qc_node(threshold_node, a) == expected


def test_build_passing_qc_node_with_interpolated_msg():
    threshold_node = models.ThresholdNode(
        **{
            **METADATA,
            "rule": ["less_than", ":ref/metric_1", 1],
            "fail_msg": "Metric is {ref/metric_1}",
        }
    )
    a = {"ref": {"metric_1": 2}}
    node = qc.build_qc_node(threshold_node, a)
    assert node["message"] == "Metric is 2"


def test_build_qc_node_without_messages_produces_empty_string():
    threshold_node = models.ThresholdNode(
        name="Example test",
        fail_code="ERR01",
        rule=["greater_than", 2, 1],
    )
    result = qc.build_qc_node(threshold_node, {})
    assert result["pass"] is True
    assert result["message"] == ""


def test_build_failing_qc_node_without_messages_produces_empty_string():
    threshold_node = models.ThresholdNode(
        name="Example test",
        fail_code="ERR01",
        rule=["greater_than", 1, 2],
    )
    result = qc.build_qc_node(threshold_node, {})
    assert result["pass"] is False
    assert result["message"] == ""
