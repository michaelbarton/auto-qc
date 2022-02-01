import sys
import typing
from importlib import resources

import click
import pydantic
import yaml
from rich import console, markdown

import auto_qc
import auto_qc.evaluate.error
import auto_qc.exception
from auto_qc import object
from auto_qc.evaluate import error, qc


def run(
    thresholds: typing.Dict[str, typing.Any], data: typing.Dict[str, typing.Any]
) -> object.AutoQCEvaluation:

    auto_qc_eval = object.AutoQC(data=data, **thresholds)
    error.check_node_paths(auto_qc_eval)
    error.check_operators(auto_qc_eval)
    return qc.evaluate(auto_qc_eval)


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
@click.option("--manual", "-m", help="Display the manual for auto-qc.", is_flag=True, default=False)
def cli(data: str, thresholds: str, json_output: bool, manual: bool) -> None:

    stdout = console.Console(width=100)
    stderr = console.Console(width=100, stderr=True)

    if manual:
        with resources.path(auto_qc.__name__, "MANUAL.md") as manual_path:
            manual = markdown.Markdown(manual_path.read_text())
            stdout.print(manual)
        exit(0)

    missing_flags = []
    if not data:
        missing_flags.append("--data")

    if not thresholds:
        missing_flags.append("--thresholds")

    if missing_flags:
        stderr.print(f"[red]Error[/red]: missing required flags: {', '.join(missing_flags) }")
        exit(1)

    try:
        with open(thresholds) as threshold, open(data) as analysis:
            evaluation = run(yaml.safe_load(threshold), yaml.safe_load(analysis))
    except auto_qc.exception.AutoQCError as err:
        stderr.print(f"[red]Errors[/red]:\n{err}")
        sys.exit(1)
    except pydantic.ValidationError as err:
        stderr.print(f"[red]Errors[/red]:\n{err}")
        sys.exit(1)

    exit_code = 0 if evaluation.is_pass else 1
    print(evaluation.to_evaluation_string(json_output))
    sys.exit(exit_code)
