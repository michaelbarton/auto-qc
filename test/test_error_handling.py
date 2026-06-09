import typing

import pytest

from auto_qc import exception, models, version
from auto_qc.evaluate import error


def _create_auto_qc(data: dict[str, typing.Any], rule: list[typing.Any]) -> models.AutoQC:
    """Helper function to create an auto-qc object."""
    return models.AutoQC(
        version=version.__version__,
        thresholds=[{"name": "example_test", "fail_code": "ERR_1", "rule": rule}],
        data=data,
    )


def test_check_node_paths_with_unknown_path():
    """Should raise an error with an unknown data path."""
    with pytest.raises(exception.AutoQCError):
        auto_qc_eval = _create_auto_qc({"ref": {"metric_1": 2}}, ["less_than", ":ref/unknown", 1])
        error.check_node_paths(auto_qc_eval)


def test_check_node_paths_suggests_closest_metric():
    """A near-miss metric path should be suggested in the error message."""
    auto_qc_eval = _create_auto_qc(
        {"coverage": {"mean_depth": 2}}, ["less_than", ":coverage/men_depth", 1]
    )
    with pytest.raises(exception.AutoQCError, match=r"Did you mean ':coverage/mean_depth'\?"):
        error.check_node_paths(auto_qc_eval)


def test_check_operators_suggests_closest_operator():
    """A near-miss operator should be suggested in the error message."""
    auto_qc_eval = _create_auto_qc({"ref": {"metric_1": 2}}, ["greater_then", ":ref/metric_1", 1])
    with pytest.raises(exception.AutoQCError, match=r"Did you mean 'greater_than'\?"):
        error.check_operators(auto_qc_eval)


def test_check_operators_with_known_operator():
    """Should not raise an error if the operators are valid"""
    auto_qc_eval = _create_auto_qc({"ref": {"metric_1": 2}}, ["less_than", ":ref/unknown", 1])
    error.check_operators(auto_qc_eval)
    # Should not raise


def test_check_operators_with_unknown_operator():
    """Should raise an error if one of the operators is invalid."""
    with pytest.raises(exception.AutoQCError):
        auto_qc_eval = _create_auto_qc({"ref": {"metric_1": 2}}, ["unknown", ":ref/unknown", 1])
        error.check_operators(auto_qc_eval)


def test_check_operators_with_unknown_nested_operator():
    """Should raise an error if one of the operators is nested and invalid."""
    with pytest.raises(exception.AutoQCError):
        auto_qc_eval = _create_auto_qc({"ref": {"metric_1": 2}}, ["and", ["or", ["unknown", 2, 1]]])
        error.check_operators(auto_qc_eval)
