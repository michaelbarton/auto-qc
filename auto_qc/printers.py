import auto_qc.version as ver
import funcy


def simple(qc_dict):
    return "PASS" if qc_dict["pass"] else "FAIL"


def json(qc_dict):
    import json as jsn

    qc_dict["qc"] = qc_dict["evaluation"]
    del qc_dict["evaluation"]
    for node in qc_dict["qc"]:
        del node["variables"]
    qc_dict["auto_qc_version"] = ver.__version__
    output = jsn.dumps(qc_dict, indent=4, sort_keys=True)
    return "\n".join([x.rstrip() for x in output.split("\n")])
