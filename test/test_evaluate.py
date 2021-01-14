from nose import tools
from auto_qc.evaluate import qc
import funcy

METADATA = {"name": "Example test", "pass_msg": "passes", "fail_msg": "fails", "fail_code": "ERR01"}


def test_build_passing_qc_node_with_two_literals():
    n = [METADATA, "greater_than", 2, 1]
    expected = {
        "variables": {},
        "name": "Example test",
        "pass": True,
        "tags": [],
        "fail_code": "ERR01",
        "message": "passes",
    }
    tools.assert_equal(qc.build_qc_node(n, {}), expected)


def test_build_failing_qc_node_with_literal_and_variable():
    n = [METADATA, "less_than", ":ref/metric_1", 1]
    a = {"metadata": {}, "data": {"ref": {"metric_1": 2}}}
    expected = {
        "variables": {"ref/metric_1": 2},
        "name": "Example test",
        "pass": False,
        "tags": [],
        "fail_code": "ERR01",
        "message": "fails",
    }
    tools.assert_equal(qc.build_qc_node(n, a), expected)


def test_build_passing_qc_node_with_interpolated_msg():
    metadata = funcy.merge(METADATA, {"fail_msg": "Metric is {ref/metric_1}"})
    n = [metadata, "less_than", ":ref/metric_1", 1]
    a = {"metadata": {}, "data": {"ref": {"metric_1": 2}}}
    node = qc.build_qc_node(n, a)
    tools.assert_equal(node["message"], "Metric is 2")
