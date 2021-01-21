import typing

from nose import tools

from auto_qc import exception, object, version
from auto_qc.evaluate import error


def _create_auto_qc(
    data: typing.Dict[str, typing.Any], rule: typing.List[typing.Any]
) -> object.AutoQC:
    """Helper function to create an auto-qc object."""
    return object.AutoQC(
        version=version.__version__,
        thresholds=[{"name": "example_test", "fail_code": "ERR_1", "rule": rule}],
        data=data,
    )


@tools.raises(exception.AutoQCError)
def test_check_node_paths_with_unknown_path():
    """Should raise an error with an unknown data path."""
    auto_qc_eval = _create_auto_qc({"ref": {"metric_1": 2}}, ["less_than", ":ref/unknown", 1])
    error.check_node_paths(auto_qc_eval)


def test_check_operators_with_known_operator():
    """Should not raise an error if the operators are valid"""
    auto_qc_eval = _create_auto_qc({"ref": {"metric_1": 2}}, ["less_than", ":ref/unknown", 1])
    error.check_operators(auto_qc_eval)
    # Should not raise


@tools.raises(exception.AutoQCError)
def test_check_operators_with_unknown_operator():
    """Should raise an error if one of the operators is invalid."""
    auto_qc_eval = _create_auto_qc({"ref": {"metric_1": 2}}, ["unknown", ":ref/unknown", 1])
    error.check_operators(auto_qc_eval)


@tools.raises(exception.AutoQCError)
def test_check_operators_with_unknown_nested_operator():
    """Should raise an error if one of the operators is nested and invalid."""
    auto_qc_eval = _create_auto_qc({"ref": {"metric_1": 2}}, ["and", ["or", ["unknown", 2, 1]]])
    error.check_operators(auto_qc_eval)
