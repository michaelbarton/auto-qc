import sys
import typing
from importlib import resources

import click
import yaml
from rich import console, markdown

import auto_qc
import auto_qc.evaluate.error
from auto_qc import object
from auto_qc.evaluate import error, qc
from auto_qc.util import workflow

METHOD_CHAIN = [
    (error.check_node_paths, ["thresholds", "data"]),
    (error.check_operators, ["thresholds"]),
    (error.check_failure_codes, ["thresholds"]),
    (qc.evaluate, ["qc_dict", "thresholds", "data"]),
]


def run(
    thresholds: typing.Dict[str, typing.Any], data: typing.Dict[str, typing.Any]
) -> object.AutoqcEvaluation:
    status = workflow.thread_status(METHOD_CHAIN, object.AutoQC(thresholds=thresholds, data=data))
    return status["qc_dict"]


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
    except auto_qc.evaluate.error.AutoQCError as err:
        stderr.print(f"[red]Errors[/red]:\n{err}")
        sys.exit(1)

    print(evaluation.to_evaluation_string(json_output))
