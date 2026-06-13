import json

import pytest
from click.testing import CliRunner

import auto_qc
from auto_qc.main import cli

THRESHOLDS = """
version: 3.0.0
thresholds:
  - name: Coverage too low
    fail_code: LOW_COVERAGE
    rule: ["greater_than", ":coverage/mean_depth", 30]
"""


def _write(tmp_path, name, body):
    path = tmp_path / name
    path.write_text(body)
    return str(path)


def test_version_flag_prints_version():
    result = CliRunner().invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert auto_qc.__version__ in result.output
    assert "auto-qc" in result.output


def test_missing_flags_are_reported():
    result = CliRunner().invoke(cli, [])
    assert result.exit_code == 1
    assert "missing required flags" in result.stderr


def test_reads_data_from_stdin():
    runner = CliRunner()
    with runner.isolated_filesystem():
        thresholds = _write_cwd("thresholds.yml", THRESHOLDS)
        result = runner.invoke(
            cli,
            ["-t", thresholds, "-d", "-"],
            input='{"coverage": {"mean_depth": 40}}',
        )
    assert result.exit_code == 0
    assert "PASS" in result.output


def _write_cwd(name, body):
    with open(name, "w") as handle:
        handle.write(body)
    return name


def test_both_stdin_is_rejected():
    result = CliRunner().invoke(cli, ["-t", "-", "-d", "-"], input="{}")
    assert result.exit_code == 1
    assert "stdin" in result.stderr


def test_type_mismatch_reports_rule_name_not_traceback(tmp_path):
    thresholds = _write(tmp_path, "t.yml", THRESHOLDS)
    data = _write(tmp_path, "d.yml", "coverage:\n  mean_depth: not-a-number\n")
    result = CliRunner().invoke(cli, ["-t", thresholds, "-d", data])
    assert result.exit_code == 1
    assert "Coverage too low" in result.stderr
    assert "Traceback" not in result.stderr


CONTRADICTORY_THRESHOLDS = """
version: 3.0.0
thresholds:
  - name: Impossible coverage
    fail_code: IMPOSSIBLE
    rule: ["and", ["greater_than", ":coverage/mean_depth", 30], ["less_than", ":coverage/mean_depth", 10]]
"""


def test_lint_flags_a_contradictory_rule_without_data(tmp_path):
    thresholds = _write(tmp_path, "t.yml", CONTRADICTORY_THRESHOLDS)
    result = CliRunner().invoke(cli, ["-t", thresholds, "--lint"])
    assert result.exit_code == 1
    assert "Impossible coverage" in result.output


def test_lint_passes_clean_thresholds(tmp_path):
    thresholds = _write(tmp_path, "t.yml", THRESHOLDS)
    result = CliRunner().invoke(cli, ["-t", thresholds, "--lint"])
    assert result.exit_code == 0
    assert "No contradictions" in result.output


def test_lint_requires_thresholds():
    result = CliRunner().invoke(cli, ["--lint"])
    assert result.exit_code == 1
    assert "--thresholds" in result.stderr


def test_json_output_includes_machine_readable_explain(tmp_path):
    thresholds = _write(tmp_path, "t.yml", THRESHOLDS)
    data = _write(tmp_path, "d.yml", "coverage:\n  mean_depth: 18.6\n")
    result = CliRunner().invoke(cli, ["-t", thresholds, "-d", data, "--json-output"])
    assert result.exit_code == 1
    report = json.loads(result.output)
    explain = report["qc"][0]["explain"]
    assert explain["operator"] == "greater_than"
    assert explain["result"] is False
    assert {"variable": ":coverage/mean_depth", "value": 18.6} in explain["args"]


def test_malformed_yaml_reports_cleanly(tmp_path):
    thresholds = _write(tmp_path, "t.yml", THRESHOLDS)
    data = _write(tmp_path, "d.yml", "coverage: {mean_depth: [\n")
    result = CliRunner().invoke(cli, ["-t", thresholds, "-d", data])
    assert result.exit_code == 1
    assert "Could not parse" in result.stderr
    assert "Traceback" not in result.stderr


def test_json_output_handles_yaml_dates(tmp_path):
    thresholds = _write(
        tmp_path,
        "t.yml",
        """
version: 3.0.0
thresholds:
  - name: run date check
    fail_code: DATE
    rule: ["equals", ":run_date", "2024-01-01"]
""",
    )
    data = _write(tmp_path, "d.yml", "run_date: 2024-01-01\n")
    result = CliRunner().invoke(cli, ["-t", thresholds, "-d", data, "--json-output"])
    assert result.exit_code == 1
    report = json.loads(result.output)
    assert report["qc"][0]["explain"]["args"][0]["value"] == "2024-01-01"


def test_non_mapping_thresholds_document_reports_cleanly(tmp_path):
    thresholds = _write(tmp_path, "t.yml", "just a string\n")
    data = _write(tmp_path, "d.yml", "coverage: {mean_depth: 40}\n")
    result = CliRunner().invoke(cli, ["-t", thresholds, "-d", data])
    assert result.exit_code == 1
    assert "must be a YAML/JSON mapping" in result.stderr
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("data_body", ["coverage: !!int not-a-number\n", "!!int\n"])
def test_yaml_tag_constructor_errors_report_cleanly(tmp_path, data_body):
    thresholds = _write(tmp_path, "t.yml", THRESHOLDS)
    data = _write(tmp_path, "d.yml", data_body)
    result = CliRunner().invoke(cli, ["-t", thresholds, "-d", data])
    assert result.exit_code == 1
    assert "Could not parse" in result.stderr
    assert "Traceback" not in result.stderr
