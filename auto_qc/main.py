import auto_qc.util.file_system as fs
import auto_qc.util.workflow    as flow
import auto_qc.printers         as prn
import auto_qc.evaluate.qc      as qc
import auto_qc.evaluate.error   as er


method_chain = [
    (fs.check_for_file, ['analysis_file']),
    (fs.check_for_file, ['threshold_file']),
    (fs.read_yaml_file, ['threshold_file', 'thresholds']),
    (fs.read_yaml_file, ['analysis_file',  'analyses']),

    (er.check_version_number, ['thresholds']),
    (er.check_node_paths,     ['thresholds', 'analyses']),
    (er.check_operators,      ['thresholds']),
    (er.check_failure_codes,  ['thresholds']),

    (qc.build_qc_dict,     ['qc_dict', 'thresholds', 'analyses'])]

def run(args):
    status = flow.thread_status(method_chain, args)

    flow.exit_if_error(status)

    if args['json']:
        f = prn.json
    else:
        f = prn.simple

    print(f(status['qc_dict']))
