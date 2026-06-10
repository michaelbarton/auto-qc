import textwrap

from rich.console import Console

from auto_qc import runner

THRESHOLDS = """
version: 3.0.0
thresholds:
  - name: Coverage too low
    fail_code: LOW_COVERAGE
    rule: ["greater_than", ":coverage/mean_depth", 30]
  - name: Contamination too high
    fail_code: CONTAMINATION
    rule: ["less_than", ":contamination/percent", 1.0]
"""


def _write_suite(tmp_path, suite_body):
    (tmp_path / "thresholds.yml").write_text(textwrap.dedent(THRESHOLDS))
    suite = tmp_path / "qc_tests.yml"
    suite.write_text(textwrap.dedent(suite_body))
    return str(suite)


def _run(tmp_path, suite_body):
    path = _write_suite(tmp_path, suite_body)
    console = Console(record=True, width=100, force_terminal=False)
    ok = runner.run_file(path, console)
    return ok, console.export_text()


def test_runner_reports_all_cases_passing(tmp_path):
    ok, output = _run(
        tmp_path,
        """
        thresholds: thresholds.yml
        cases:
          - name: healthy sample
            data:
              coverage: { mean_depth: 40 }
              contamination: { percent: 0.2 }
            expect: pass
          - name: low coverage is flagged
            data:
              coverage: { mean_depth: 5 }
              contamination: { percent: 0.2 }
            expect: fail
            codes: [LOW_COVERAGE]
        """,
    )
    assert ok is True
    assert "healthy sample" in output
    assert "passed" in output


def test_runner_flags_an_unmet_expectation(tmp_path):
    ok, output = _run(
        tmp_path,
        """
        thresholds: thresholds.yml
        cases:
          - name: should pass but does not
            data:
              coverage: { mean_depth: 5 }
              contamination: { percent: 0.2 }
            expect: pass
        """,
    )
    assert ok is False
    assert "expected PASS, got FAIL (LOW_COVERAGE)" in output


def test_runner_checks_exact_fail_codes(tmp_path):
    ok, output = _run(
        tmp_path,
        """
        thresholds: thresholds.yml
        cases:
          - name: wrong code asserted
            data:
              coverage: { mean_depth: 40 }
              contamination: { percent: 2.0 }
            expect: fail
            codes: [LOW_COVERAGE]
        """,
    )
    assert ok is False
    assert "expected FAIL (LOW_COVERAGE), got FAIL (CONTAMINATION)" in output


def test_runner_passes_fail_case_without_specifying_codes(tmp_path):
    ok, _ = _run(
        tmp_path,
        """
        thresholds: thresholds.yml
        cases:
          - name: any failure is fine
            data:
              coverage: { mean_depth: 5 }
              contamination: { percent: 0.2 }
            expect: fail
        """,
    )
    assert ok is True
