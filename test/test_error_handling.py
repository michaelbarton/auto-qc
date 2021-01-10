from nose.tools import *
import auto_qc.evaluate.error as er


def test_check_version_number():
    def version(v):
        return {"threshold": {"metadata": {"version": {"auto-qc": v}}}}

    status = er.check_version_number("threshold", version("3.0.0"))
    assert_not_in("error", status)

    status = er.check_version_number("threshold", version("0.1.0"))
    assert_in("error", status)

    status = er.check_version_number("threshold", version("1.1.0"))
    assert_in("error", status)


def test_check_node_paths_with_valid_node():
    n = [["less_than", ":ref/metric_1", 1]]
    a = {"metadata": {}, "data": {"ref": {"metric_1": 2}}}

    status = {"nodes": {"thresholds": n}, "analyses": a}
    assert_not_in("error", status)


def test_check_node_paths_with_unknown_path():
    n = [["less_than", ":ref/unknown", 1]]
    a = {"metadata": {}, "data": {"ref": {"metric_1": 2}}}

    status = {"nodes": {"thresholds": n}, "analyses": a}
    result = er.check_node_paths("nodes", "analyses", status)
    assert_in("error", result)
    assert_equal(result["error"], "No matching metric ':ref/unknown' found.")


def test_check_operators_with_known_operator():
    n = [["less_than", 2, 1]]
    status = {"nodes": {"thresholds": n}}
    assert_not_in("error", er.check_operators("nodes", status))


def test_check_operators_with_unknown_operator():
    n = [["unknown", 2, 1]]
    status = {"nodes": {"thresholds": n}}
    assert_in("error", er.check_operators("nodes", status))
    assert_equal(status["error"], "Unknown operator 'unknown.'")


def test_check_operators_with_unknown_nested_operator():
    n = [["and", ["or", ["unknown", 2, 1]]]]
    status = {"nodes": {"thresholds": n}}
    assert_in("error", er.check_operators("nodes", status))
    assert_equal(status["error"], "Unknown operator 'unknown.'")


def test_check_operators_with_doc_string():
    n = [[{"name": "my qc threshold"}, "less_than", 2, 1]]
    status = {"nodes": {"thresholds": n}}
    assert_not_in("error", er.check_operators("nodes", status))


def test_check_unknown_operator_with_doc_string():
    n = [[{"name": "my qc threshold"}, "unknown", 2, 1]]
    status = {"nodes": {"thresholds": n}}
    assert_in("error", er.check_operators("nodes", status))
    assert_equal(status["error"], "Unknown operator 'unknown.'")


def test_check_operators_with_unknown_nested_operator_with_doc_string():
    n = [[{"name": "my qc threshold"}, "unknown", ["or", ["less_than", 2, 1]]]]
    status = {"nodes": {"thresholds": n}}
    assert_in("error", er.check_operators("nodes", status))
    assert_equal(status["error"], "Unknown operator 'unknown.'")


def test_check_node_paths_with_no_failure_code():
    n = [[{"name": "test"}, "less_than", ":metric_1", 1]]
    a = {"metadata": {}, "data": {"metric_1": 2}}

    status = {"nodes": {"thresholds": n}, "analyses": a}
    result = er.check_failure_codes("nodes", status)
    assert_in("error", result)
    assert_equal(result["error"], "The QC entry 'test' is missing a failure code")


def test_check_node_paths_with_failure_code():
    n = [[{"name": "test", "fail_code": "ERR"}, "less_than", ":metric_1", 1]]
    a = {"metadata": {}, "data": {"metric_1": 2}}

    status = {"nodes": {"thresholds": n}, "analyses": a}
    result = er.check_failure_codes("nodes", status)
    assert_not_in("error", result)
