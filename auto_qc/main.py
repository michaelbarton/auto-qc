import sys
import typing
from importlib import resources

import click
import yaml
from rich import console, markdown

import auto_qc
from auto_qc import objects
from auto_qc.evaluate import error, qc
from auto_qc.util import workflow

METHOD_CHAIN = [
    (error.check_version_number, ["thresholds"]),
    (error.check_node_paths, ["thresholds", "analyses"]),
    (error.check_operators, ["thresholds"]),
    (error.check_failure_codes, ["thresholds"]),
    (qc.evaluate, ["qc_dict", "thresholds", "analyses"]),
]


def run(
    thresholds: typing.Dict[str, typing.Any], analysis: typing.Dict[str, typing.Any]
) -> objects.AutoqcEvaluation:
    status = workflow.thread_status(METHOD_CHAIN, {"thresholds": thresholds, "analyses": analysis})
    return status["qc_dict"]


@click.command()
@click.option(
    "--analysis-file", "-a", help="Path to analysis YAML/JSON.", type=click.Path(exists=True)
)
@click.option(
    "--threshold-file", "-t", help="Path to threshold YAML/JSON.", type=click.Path(exists=True)
)
@click.option(
    "--json-output",
    "-j",
    help="Create JSON output of quality control.",
    is_flag=True,
    default=False,
)
@click.option("--manual", "-m", help="Display the manual for auto-qc.", is_flag=True, default=False)
def cli(analysis_file: str, threshold_file: str, json_output: bool, manual: bool) -> None:

    if manual:
        with resources.path(auto_qc.__name__, "MANUAL.md") as manual_path:
            manual = markdown.Markdown(manual_path.read_text())
            console.Console(width=100).print(manual)
        exit(0)

    if not analysis_file:
        sys.stderr.write("Missing required flag: --analysis-file / -a\n")
        exit(1)

    if not threshold_file:
        sys.stderr.write("Missing required flag: --threshold-file / -t\n")
        exit(1)

    try:
        with open(threshold_file) as threshold, open(analysis_file) as analysis:
            evaluation = run(yaml.safe_load(threshold), yaml.safe_load(analysis))
    except objects.AutoQCEvaluationError as err:
        sys.stderr.write(f"{err}\n")
        sys.exit(1)

    print(evaluation.to_evaluation_string(json_output))
