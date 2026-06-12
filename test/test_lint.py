from rich.console import Console

from auto_qc import core, lint


def _analyse(rule):
    state = core.build_thresholds(
        {
            "version": "3.0.0",
            "thresholds": [{"name": "Rule", "fail_code": "CODE", "rule": rule}],
        }
    )
    return lint.analyse(state)


def test_contradictory_conjunction_is_an_error():
    [finding] = _analyse(["and", ["greater_than", ":x", 30], ["less_than", ":x", 10]])
    assert finding.severity == "error"
    assert ":x" in finding.message


def test_satisfiable_conjunction_is_clean():
    assert _analyse(["and", ["greater_than", ":x", 10], ["less_than", ":x", 100]]) == []


def test_bounds_on_different_metrics_do_not_collide():
    assert _analyse(["and", ["greater_than", ":x", 30], ["less_than", ":y", 10]]) == []


def test_reversed_between_is_an_empty_range():
    [finding] = _analyse(["between", ":x", 60, 30])
    assert finding.severity == "error"
    assert "empty range" in finding.message


def test_conflicting_equals_is_unsatisfiable():
    [finding] = _analyse(["and", ["equals", ":x", 1], ["equals", ":x", 2]])
    assert finding.severity == "error"


def test_equals_outside_a_range_is_unsatisfiable():
    [finding] = _analyse(["and", ["equals", ":x", 5], ["greater_than", ":x", 10]])
    assert finding.severity == "error"


def test_strict_equal_boundary_is_unsatisfiable():
    # ``x >= 10`` and ``x < 10`` share only the point 10, which ``<`` excludes.
    [finding] = _analyse(["and", ["greater_equal_than", ":x", 10], ["less_than", ":x", 10]])
    assert finding.severity == "error"


def test_touching_inclusive_bounds_are_satisfiable():
    # ``x >= 10`` and ``x <= 10`` both admit the single value 10.
    assert _analyse(["and", ["greater_equal_than", ":x", 10], ["less_equal_than", ":x", 10]]) == []


def test_literal_left_operand_is_normalised():
    # ``30 < x`` and ``x < 10`` — the metric still has no satisfying value.
    [finding] = _analyse(["and", ["less_than", 30, ":x"], ["less_than", ":x", 10]])
    assert finding.severity == "error"


def test_or_branches_are_not_treated_as_contradictions():
    # Either branch alone is satisfiable, so an ``or`` of them is fine.
    assert _analyse(["or", ["greater_than", ":x", 30], ["less_than", ":x", 10]]) == []


def test_constant_rule_that_always_fails_is_an_error():
    [finding] = _analyse(["less_than", 5, 3])
    assert finding.severity == "error"
    assert "never pass" in finding.message


def test_constant_rule_that_always_passes_is_a_warning():
    [finding] = _analyse(["greater_than", 5, 3])
    assert finding.severity == "warning"
    assert "always passes" in finding.message


def test_unmeasurable_conjuncts_are_ignored():
    # A membership test carries no interval, so it neither helps nor false-positives.
    assert _analyse(["and", ["is_in", ":x", ["list", 1, 2]], ["greater_than", ":y", 0]]) == []


def _render(findings):
    console = Console(record=True, width=100, force_terminal=False)
    lint.render(findings, console)
    return console.export_text()


def test_render_reports_a_clean_bill_of_health():
    assert "No contradictions" in _render([])


def test_render_lists_findings_with_severity_counts():
    findings = _analyse(["and", ["greater_than", ":x", 30], ["less_than", ":x", 10]])
    output = _render(findings)
    assert "error" in output
    assert "Rule" in output
    assert "1 error(s)" in output
