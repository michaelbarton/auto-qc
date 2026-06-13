"""Run a suite of test cases against a thresholds file.

QC rules are production logic, so auto-qc lets you test them like code. A
fixtures file pairs sample data with the outcome you expect, and
``auto-qc --test`` checks every case and reports — pytest style — which ones
disagree.
"""

import os
import typing

import pydantic
import yaml
from rich.console import Console

from auto_qc import core, exception, models


def _load_yaml(path: str) -> typing.Any:
    """Parse the YAML document at ``path``.

    Raises:
        AutoQCError: If the file is not valid YAML.
    """
    with open(path) as handle:
        try:
            return yaml.safe_load(handle)
        except yaml.YAMLError as err:
            raise exception.AutoQCError(f"Could not parse '{path}' as YAML/JSON:\n{err}") from err


def _format_outcome(is_pass: bool, fail_codes: list[str]) -> str:
    """Render an outcome the same way a case author would write it."""
    if is_pass:
        return "PASS"
    if fail_codes:
        return f"FAIL ({', '.join(fail_codes)})"
    return "FAIL"


def _check_case(case: models.TestCase, thresholds: dict[str, typing.Any]) -> str | None:
    """Return ``None`` if the case meets its expectation, else why it didn't."""
    try:
        evaluation = core.run(thresholds, case.data)
    except exception.AutoQCError as err:
        return f"raised an error: {err}"

    actual = _format_outcome(evaluation.is_pass, evaluation.fail_codes)

    if case.expect == "pass":
        return None if evaluation.is_pass else f"expected PASS, got {actual}"

    # The case expects a failure.
    if evaluation.is_pass:
        return f"expected {_format_outcome(False, case.codes or [])}, got PASS"
    if case.codes is not None and sorted(set(case.codes)) != evaluation.fail_codes:
        return f"expected {_format_outcome(False, case.codes)}, got {actual}"
    return None


def run_file(path: str, console: Console) -> bool:
    """Run the test suite at ``path``, printing a report. Return True if all pass.

    The thresholds path inside the suite is resolved relative to the suite
    file, so a suite can sit next to the rules it tests.

    Raises:
        AutoQCError: If the suite file itself is invalid, or the thresholds
            file it references cannot be read or parsed.
    """
    base_dir = os.path.dirname(os.path.abspath(path))
    suite_doc = _load_yaml(path)

    try:
        suite = models.TestSuite(**suite_doc)
    except (pydantic.ValidationError, TypeError) as err:
        raise exception.AutoQCError(str(err)) from err

    thresholds_path = os.path.join(base_dir, suite.thresholds)
    try:
        thresholds = _load_yaml(thresholds_path)
    except OSError as err:
        raise exception.AutoQCError(
            f"Could not read thresholds file '{suite.thresholds}' "
            f"referenced by the test suite: {err}"
        ) from err

    console.print(
        f"Testing [cyan]{suite.thresholds}[/cyan] against [bold]{len(suite.cases)}[/bold] cases\n"
    )

    failures = 0
    for case in suite.cases:
        reason = _check_case(case, thresholds)
        if reason is None:
            console.print(f"  [green]✓[/green] {case.name}")
        else:
            failures += 1
            console.print(f"  [red]✗[/red] {case.name}")
            console.print(f"      [dim]{reason}[/dim]")

    passed = len(suite.cases) - failures
    console.print()
    if failures:
        console.print(f"  [red]{failures} failed[/red], [green]{passed} passed[/green]")
    else:
        console.print(f"  [bold green]{passed} passed[/bold green] ✨")
    return failures == 0
