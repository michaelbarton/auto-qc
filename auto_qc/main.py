import argparse

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

    if args["json"]:
        f = printers.json
    else:
        f = printers.simple

    print(f(status["qc_dict"]))


def cli() -> None:
    parser = argparse.ArgumentParser(
        description="Calculates if sample passes based on QC thresholds"
    )
    parser.add_argument("--analysis-file", "-a", dest="analysis_file", required=True)
    parser.add_argument("--threshold-file", "-t", dest="threshold_file", required=True)

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--json-output", "-j", dest="json", action="store_true")

    args = vars(parser.parse_args())
    run(args)
