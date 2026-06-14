import typing

import pytest

from auto_qc import core, exception, models, version
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


def test_check_operators_allows_literal_list_in_value_position():
    """A plain list as an ``is_in`` set is data, not an unknown operator."""
    auto_qc_eval = _create_auto_qc(
        {"sample": {"protocol": "PCR-free"}},
        ["is_in", ":sample/protocol", ["Low Input DNA", "PCR-free"]],
    )
    error.check_operators(auto_qc_eval)  # Should not raise.


def test_check_arity_flags_too_many_arguments():
    """``not`` takes a single argument; two should be reported up front."""
    auto_qc_eval = _create_auto_qc({"ref": {"metric_1": 2}}, ["not", True, False])
    with pytest.raises(exception.AutoQCError, match="exactly 1 argument"):
        error.check_arity(auto_qc_eval)


def test_check_arity_flags_too_few_arguments():
    """A comparison needs two arguments."""
    auto_qc_eval = _create_auto_qc({"ref": {"metric_1": 2}}, ["greater_than", ":ref/metric_1"])
    with pytest.raises(exception.AutoQCError, match="exactly 2 arguments"):
        error.check_arity(auto_qc_eval)


def test_check_arity_accepts_valid_rules():
    auto_qc_eval = _create_auto_qc({"ref": {"metric_1": 2}}, ["greater_than", ":ref/metric_1", 1])
    error.check_arity(auto_qc_eval)  # Should not raise.


def test_type_mismatch_surfaces_as_autoqc_error_with_rule_name():
    """Comparing text to a number reports cleanly instead of crashing."""
    thresholds = {
        "version": version.__version__,
        "thresholds": [
            {"name": "Coverage too low", "fail_code": "LOW", "rule": ["greater_than", ":a", 3]}
        ],
    }
    with pytest.raises(exception.AutoQCError, match="Coverage too low"):
        core.run(thresholds, {"a": "not a number"})


def _create_auto_qc_with_messages(rule, **messages) -> models.AutoQC:
    return models.AutoQC(
        version=version.__version__,
        thresholds=[{"name": "example_test", "fail_code": "ERR_1", "rule": rule, **messages}],
        data={},
    )


def test_check_messages_accepts_placeholders_from_the_rule():
    auto_qc_eval = _create_auto_qc_with_messages(
        ["greater_than", ":coverage/mean_depth", 30],
        pass_msg="depth was {coverage/mean_depth:.1f}",
        fail_msg="depth was only {coverage/mean_depth}",
    )
    error.check_messages(auto_qc_eval)  # Should not raise.


def test_check_messages_flags_unknown_placeholder_with_suggestion():
    auto_qc_eval = _create_auto_qc_with_messages(
        ["greater_than", ":coverage/mean_depth", 30],
        fail_msg="depth was only {coverage/men_depth}",
    )
    with pytest.raises(exception.AutoQCError, match=r"Did you mean 'coverage/mean_depth'\?"):
        error.check_messages(auto_qc_eval)


def test_check_messages_flags_unbalanced_braces():
    auto_qc_eval = _create_auto_qc_with_messages(
        ["greater_than", ":coverage/mean_depth", 30],
        fail_msg="depth was only {coverage/mean_depth",
    )
    with pytest.raises(exception.AutoQCError, match="not a valid template"):
        error.check_messages(auto_qc_eval)


def test_check_messages_flags_positional_placeholder():
    auto_qc_eval = _create_auto_qc_with_messages(
        ["greater_than", ":coverage/mean_depth", 30],
        fail_msg="depth was only {}",
    )
    with pytest.raises(exception.AutoQCError, match="positional placeholder"):
        error.check_messages(auto_qc_eval)


def test_check_messages_allows_literal_braces():
    auto_qc_eval = _create_auto_qc_with_messages(
        ["greater_than", ":coverage/mean_depth", 30],
        fail_msg="literal {{braces}} are fine",
    )
    error.check_messages(auto_qc_eval)  # Should not raise.


def test_message_typo_is_reported_when_thresholds_are_read():
    """A bad placeholder fails at build time, not as a KeyError mid-evaluation."""
    thresholds = {
        "version": version.__version__,
        "thresholds": [
            {
                "name": "Coverage too low",
                "fail_code": "LOW",
                "rule": ["greater_than", ":a", 3],
                "fail_msg": "value was {wrong_name}",
            }
        ],
    }
    with pytest.raises(exception.AutoQCError, match="wrong_name"):
        core.run(thresholds, {"a": 5})


def test_bad_format_spec_surfaces_as_autoqc_error_with_rule_name():
    """A format spec that fails against the resolved value reports cleanly."""
    thresholds = {
        "version": version.__version__,
        "thresholds": [
            {
                "name": "Sample name",
                "fail_code": "NAME",
                "rule": ["equals", ":a", "x"],
                "fail_msg": "name was {a:.2f}",
            }
        ],
    }
    with pytest.raises(exception.AutoQCError, match="Sample name"):
        core.run(thresholds, {"a": "not x"})
