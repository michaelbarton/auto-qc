import behave
import json as json


@behave.then("the JSON-format standard {stream} should equal")
def step_impl(context, stream):
    def refmt(t):
        return json.dumps(json.loads(t), indent=4, sort_keys=True)

    if stream == "out":
        s = context.output.stdout
    elif stream == "error":
        s = context.output.stderr
    else:
        raise RuntimeError('Unknown stream "{}"'.format(stream))
    asrt.assert_diff(refmt(context.text), refmt(s))
