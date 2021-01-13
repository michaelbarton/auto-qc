from importlib import resources

from rich import console
from rich import markdown
import click

import auto_qc
from auto_qc import printers
from auto_qc.evaluate import error
from auto_qc.evaluate import qc
from auto_qc.util import file_system
from auto_qc.util import workflow


method_chain = [
    (file_system.check_for_file, ["analysis_file"]),
    (file_system.check_for_file, ["threshold_file"]),
    (file_system.read_yaml_file, ["threshold_file", "thresholds"]),
    (file_system.read_yaml_file, ["analysis_file", "analyses"]),
    (error.check_version_number, ["thresholds"]),
    (error.check_node_paths, ["thresholds", "analyses"]),
    (error.check_operators, ["thresholds"]),
    (error.check_failure_codes, ["thresholds"]),
    (qc.build_qc_dict, ["qc_dict", "thresholds", "analyses"]),
]


def run(args):
    status = workflow.thread_status(method_chain, args)

    workflow.exit_if_error(status)

    if args["json_output"]:
        f = printers.json
    else:
        f = printers.simple

    print(f(status["qc_dict"]))


@click.command()
@click.option("--analysis-file", "-a", help="Path to analysis YAML/JSON.", type=click.Path())
@click.option("--threshold-file", "-t", help="Path to threshold YAML/JSON.", type=click.Path())
@click.option("--json-output", "-j", help="Create JSON output of quality control.", is_flag=True, default=False)
@click.option("--manual", "-m", help="Display the manual for auto-qc.", is_flag=True, default=False)
def cli(analysis_file: str, threshold_file: str, json_output: bool, manual: bool) -> None:

    if manual:
        with resources.path(auto_qc.__name__, 'MANUAL.md') as manual_path:
            manual = markdown.Markdown(manual_path.read_text())
            console.Console(width=100).print(manual)
        exit(0)

    if not analysis_file:
        print("Missing required flag: --analysis-file / -a")
        exit(1)

    if not threshold_file:
        print("Missing required flag: --threshold-file / -t")
        exit(1)

    run(
        {
            "analysis_file": analysis_file,
            "threshold_file": threshold_file,
            "json_output": json_output,
        }
    )
