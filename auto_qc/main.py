import sys
from importlib import resources

import click
import yaml
from rich import console, markdown

import auto_qc
import auto_qc.exception
from auto_qc import core, runner
from auto_qc import explain as explain_view
from auto_qc.evaluate import qc


@click.command()
@click.option("--data", "-d", help="Path to data YAML/JSON.", type=click.Path(exists=True))
@click.option(
    "--thresholds", "-t", help="Path to thresholds YAML/JSON.", type=click.Path(exists=True)
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
    "--test",
    "-T",
    "test_suite",
    help="Run a suite of test cases against its thresholds file.",
    type=click.Path(exists=True),
)
@click.option("--manual", "-m", help="Display the manual for auto-qc.", is_flag=True, default=False)
def cli(
    data: str, thresholds: str, json_output: bool, explain: bool, test_suite: str, manual: bool
) -> None:

    stdout = console.Console(width=100)
    stderr = console.Console(width=100, stderr=True)

    if manual:
        with resources.path(auto_qc.__name__, "MANUAL.md") as manual_path:
            stdout.print(markdown.Markdown(manual_path.read_text()))
        exit(0)

    if test_suite:
        try:
            passed = runner.run_file(test_suite, stdout)
        except auto_qc.exception.AutoQCError as err:
            stderr.print(f"[red]Errors[/red]:\n{err}")
            sys.exit(1)
        sys.exit(0 if passed else 1)

    missing_flags = []
    if not data:
        missing_flags.append("--data")

    if not thresholds:
        missing_flags.append("--thresholds")

    if missing_flags:
        stderr.print(f"[red]Error[/red]: missing required flags: {', '.join(missing_flags)}")
        exit(1)

    try:
        with open(thresholds) as threshold, open(data) as analysis:
            state = core.build(yaml.safe_load(threshold), yaml.safe_load(analysis))
    except auto_qc.exception.AutoQCError as err:
        stderr.print(f"[red]Errors[/red]:\n{err}")
        sys.exit(1)

    evaluation = qc.evaluate(state)

    if explain:
        explain_view.render(state, stdout)
    else:
        print(evaluation.to_evaluation_string(json_output))

    sys.exit(0 if evaluation.is_pass else 1)
