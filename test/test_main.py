import json

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
