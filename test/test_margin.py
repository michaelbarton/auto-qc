from rich.console import Console

from auto_qc import core, margin, node


def _collect(expr, data=None):
    return margin.collect(node.evaluate(expr, data or {}))


def test_passing_greater_than_reports_positive_slack():
    [comparison] = _collect(["greater_than", ":depth", 30], {"depth": 40})
    assert comparison.holds
    assert comparison.slack == 10


def test_failing_greater_than_reports_negative_slack():
    [comparison] = _collect(["greater_than", ":depth", 30], {"depth": 18})
    assert not comparison.holds
    assert comparison.slack == -12


def test_less_than_measures_distance_below_the_bound():
    [comparison] = _collect(["less_than", ":contam", 1.0], {"contam": 0.4})
    assert comparison.holds
    assert round(comparison.slack, 1) == 0.6


def test_between_uses_distance_to_the_nearest_bound():
    [comparison] = _collect(["between", ":depth", 30, 60], {"depth": 31})
    assert comparison.holds
    assert comparison.slack == 1


def test_between_below_range_is_a_deficit():
    [comparison] = _collect(["between", ":depth", 30, 60], {"depth": 25})
    assert not comparison.holds
    assert comparison.slack == -5


def test_equality_and_string_tests_have_no_margin():
    assert _collect(["equals", ":protocol", "Standard"], {"protocol": "Standard"}) == []
    assert _collect(["starts_with", ":id", "SRX"], {"id": "SRX-1"}) == []


def test_collect_descends_into_boolean_combinators():
    comparisons = _collect(
        ["or", ["greater_than", ":a", 10], ["less_than", ":b", 5]],
        {"a": 12, "b": 9},
    )
    assert len(comparisons) == 2
    assert {round(c.slack) for c in comparisons} == {2, -4}


def test_arithmetic_feeding_a_comparison_is_measured_once():
    [comparison] = _collect(
        ["greater_than", ["divide", ":mapped", ":total"], 0.9],
        {"mapped": 95, "total": 100},
    )
    assert comparison.holds
    assert round(comparison.slack, 2) == 0.05


def _render(thresholds_doc, data):
    state = core.build(thresholds_doc, data)
    console = Console(record=True, width=100, force_terminal=False)
    margin.render(state, console)
    return console.export_text()


def test_render_reports_slack_and_marks_the_tightest_comparison():
    output = _render(
        {
            "version": "3.0.0",
            "thresholds": [
                {
                    "name": "Coverage",
                    "fail_code": "COVERAGE",
                    "rule": [
                        "and",
                        ["greater_than", ":coverage/mean_depth", 30],
                        ["greater_than", ":quality/percent_q30", 90],
                    ],
                }
            ],
        },
        {"coverage": {"mean_depth": 30.1}, "quality": {"percent_q30": 99}},
    )
    assert "PASS" in output
    assert "slack 0.1" in output
    assert "slack 9" in output
    assert "tightest" in output


def test_render_notes_rules_without_numeric_comparisons():
    output = _render(
        {
            "version": "3.0.0",
            "thresholds": [
                {
                    "name": "Right protocol",
                    "fail_code": "PROTOCOL",
                    "rule": ["equals", ":sample/protocol", "Standard DNA"],
                }
            ],
        },
        {"sample": {"protocol": "Standard DNA"}},
    )
    assert "no numeric comparisons to measure" in output
