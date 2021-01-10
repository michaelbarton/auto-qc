import os, sys, pkg_resources
import argparse

import auto_qc.util.file_system as fs
import auto_qc.util.workflow as flow
import auto_qc.printers as prn
import auto_qc.evaluate.qc as qc
import auto_qc.evaluate.error as er


method_chain = [
    (fs.check_for_file, ["analysis_file"]),
    (fs.check_for_file, ["threshold_file"]),
    (fs.read_yaml_file, ["threshold_file", "thresholds"]),
    (fs.read_yaml_file, ["analysis_file", "analyses"]),
    (er.check_version_number, ["thresholds"]),
    (er.check_node_paths, ["thresholds", "analyses"]),
    (er.check_operators, ["thresholds"]),
    (er.check_failure_codes, ["thresholds"]),
    (qc.build_qc_dict, ["qc_dict", "thresholds", "analyses"]),
]


def run(args):
    status = flow.thread_status(method_chain, args)

    flow.exit_if_error(status)

    if args["json"]:
        f = prn.json
    else:
        f = prn.simple

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
