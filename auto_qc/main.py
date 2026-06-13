import sys
import typing
from importlib import resources

import click
import yaml
from rich import console, markdown

import auto_qc
import auto_qc.exception
from auto_qc import core, runner
from auto_qc import explain as explain_view
from auto_qc import lint as lint_view
from auto_qc import margin as margin_view
from auto_qc.evaluate import qc


def _load_document(path: str) -> typing.Any:
    """Parse a YAML/JSON document from a path, or from stdin when ``path`` is ``-``.

    Raises:
        AutoQCError: If the document is not valid YAML/JSON.
    """
    try:
        if path == "-":
            return yaml.safe_load(sys.stdin.read())
        with open(path) as handle:
            return yaml.safe_load(handle)
    # Beyond YAMLError, PyYAML's tag constructors (!!int, !!timestamp, ...)
    # raise bare ValueError/OverflowError/IndexError on values they cannot
    # convert, and its parser recurses on nesting depth.
    except (yaml.YAMLError, ValueError, OverflowError, IndexError, RecursionError) as err:
        source = "stdin" if path == "-" else f"'{path}'"
        raise auto_qc.exception.AutoQCError(
            f"Could not parse {source} as YAML/JSON:\n{err}"
        ) from err


@click.command()
@click.version_option(auto_qc.__version__, "-V", "--version", prog_name="auto-qc")
@click.option(
    "--data",
    "-d",
    help="Path to data YAML/JSON, or '-' to read from stdin.",
    type=click.Path(exists=True, allow_dash=True),
)
@click.option(
    "--thresholds",
    "-t",
    help="Path to thresholds YAML/JSON, or '-' to read from stdin.",
    type=click.Path(exists=True, allow_dash=True),
)
@click.option(
    "--json-output",
    "-j",
    help="Create JSON output of quality control.",
    is_flag=True,
    default=False,
)
@click.option(
    "--explain",
    "-e",
    help="Show a tree explaining how every rule was evaluated.",
    is_flag=True,
    default=False,
)
@click.option(
    "--margin",
    "-M",
    help="Show how far each numeric comparison is from flipping its result.",
    is_flag=True,
    default=False,
)
@click.option(
    "--lint",
    "-l",
    help="Statically check the thresholds for contradictory rules (no data needed).",
    is_flag=True,
    default=False,
)
@click.option(
    "--test",
    "-T",
    "test_suite",
    help="Run a suite of test cases against its thresholds file.",
    type=click.Path(exists=True),
)
@click.option("--manual", "-m", help="Display the manual for auto-qc.", is_flag=True, default=False)
def cli(
    data: str,
    thresholds: str,
    json_output: bool,
    explain: bool,
    margin: bool,
    lint: bool,
    test_suite: str,
    manual: bool,
) -> None:

    stdout = console.Console(width=100)
    stderr = console.Console(width=100, stderr=True)

    if manual:
        manual_text = resources.files(auto_qc).joinpath("MANUAL.md").read_text()
        stdout.print(markdown.Markdown(manual_text))
        sys.exit(0)

    if test_suite:
        try:
            passed = runner.run_file(test_suite, stdout)
        except auto_qc.exception.AutoQCError as err:
            stderr.print(f"[red]Errors[/red]:\n{err}")
            sys.exit(1)
        sys.exit(0 if passed else 1)

    if lint:
        if not thresholds:
            stderr.print("[red]Error[/red]: --lint requires --thresholds.")
            sys.exit(1)
        try:
            state = core.build_thresholds(_load_document(thresholds))
            findings = lint_view.analyse(state)
        except auto_qc.exception.AutoQCError as err:
            stderr.print(f"[red]Errors[/red]:\n{err}")
            sys.exit(1)
        lint_view.render(findings, stdout)
        sys.exit(1 if any(f.severity == "error" for f in findings) else 0)

    missing_flags = []
    if not data:
        missing_flags.append("--data")

    if not thresholds:
        missing_flags.append("--thresholds")

    if missing_flags:
        stderr.print(f"[red]Error[/red]: missing required flags: {', '.join(missing_flags)}")
        sys.exit(1)

    if data == "-" and thresholds == "-":
        stderr.print("[red]Error[/red]: only one of --data / --thresholds can read from stdin.")
        sys.exit(1)

    try:
        state = core.build(_load_document(thresholds), _load_document(data))
        evaluation = qc.evaluate(state)
        if explain:
            explain_view.render(state, stdout)
        if margin:
            margin_view.render(state, stdout)
    except RecursionError:
        stderr.print("[red]Errors[/red]:\nThe documents are nested too deeply to evaluate.")
        sys.exit(1)
    except auto_qc.exception.AutoQCError as err:
        stderr.print(f"[red]Errors[/red]:\n{err}")
        sys.exit(1)

    if not explain and not margin:
        print(evaluation.to_evaluation_string(json_output))

    sys.exit(0 if evaluation.is_pass else 1)
