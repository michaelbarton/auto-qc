import textwrap

import pytest
from rich.console import Console

from auto_qc import exception, runner

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


def test_runner_reports_missing_thresholds_file_cleanly(tmp_path):
    suite = tmp_path / "qc_tests.yml"
    suite.write_text(
        textwrap.dedent(
            """
            thresholds: does_not_exist.yml
            cases:
              - name: a case
                data: { x: 1 }
            """
        )
    )
    console = Console(record=True, width=100, force_terminal=False)
    with pytest.raises(exception.AutoQCError, match="does_not_exist.yml"):
        runner.run_file(str(suite), console)


def test_runner_reports_malformed_suite_yaml_cleanly(tmp_path):
    suite = tmp_path / "qc_tests.yml"
    suite.write_text("thresholds: [\n")
    console = Console(record=True, width=100, force_terminal=False)
    with pytest.raises(exception.AutoQCError, match="Could not parse"):
        runner.run_file(str(suite), console)


def test_runner_treats_duplicate_expected_codes_as_one(tmp_path):
    ok, _ = _run(
        tmp_path,
        """
        thresholds: thresholds.yml
        cases:
          - name: duplicate codes collapse
            data:
              coverage: { mean_depth: 5 }
              contamination: { percent: 0.2 }
            expect: fail
            codes: [LOW_COVERAGE, LOW_COVERAGE]
        """,
    )
    assert ok is True
