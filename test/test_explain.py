from rich.console import Console

from auto_qc import core, explain


def _render(thresholds_doc, data):
    state = core.build(thresholds_doc, data)
    console = Console(record=True, width=100, force_terminal=False)
    explain.render(state, console)
    return console.export_text()


def test_explain_marks_pass_and_resolved_values():
    output = _render(
        {
            "version": "3.0.0",
            "thresholds": [
                {
                    "name": "Coverage too low",
                    "fail_code": "LOW_COVERAGE",
                    "rule": ["greater_than", ":coverage/mean_depth", 30],
                }
            ],
        },
        {"coverage": {"mean_depth": 18.6}},
    )
    assert "FAIL" in output
    assert "Coverage too low" in output
    assert "LOW_COVERAGE" in output
    # The metric pointer is resolved to its value in the tree.
    assert ":coverage/mean_depth" in output
    assert "18.6" in output


def test_explain_renders_nested_boolean_rule():
    output = _render(
        {
            "version": "3.0.0",
            "thresholds": [
                {
                    "name": "Either threshold",
                    "fail_code": "QC",
                    "rule": [
                        "or",
                        ["greater_than", ":a", 10],
                        ["greater_than", ":b", 10],
                    ],
                }
            ],
        },
        {"a": 20, "b": 5},
    )
    assert "PASS" in output
    assert "or" in output
    assert "greater_than" in output
