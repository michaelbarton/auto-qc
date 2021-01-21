from nose import tools

from auto_qc import object
from auto_qc.evaluate import qc

METADATA = {"name": "Example test", "pass_msg": "passes", "fail_msg": "fails", "fail_code": "ERR01"}


def test_build_passing_qc_node_with_two_literals():
    threshold_node = object.ThresholdNode(
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
    }
    tools.assert_equal(qc.build_qc_node(threshold_node, {}), expected)


def test_build_failing_qc_node_with_literal_and_variable():
    threshold_node = object.ThresholdNode(
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
    }
    tools.assert_equal(qc.build_qc_node(threshold_node, a), expected)


def test_build_passing_qc_node_with_interpolated_msg():
    threshold_node = object.ThresholdNode(
        **{
            **METADATA,
            "rule": ["less_than", ":ref/metric_1", 1],
            "fail_msg": "Metric is {ref/metric_1}",
        }
    )
    a = {"ref": {"metric_1": 2}}
    node = qc.build_qc_node(threshold_node, a)
    tools.assert_equal(node["message"], "Metric is 2")
