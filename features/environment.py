from scripttest import TestFileEnvironment


def before_scenario(context, scenario):
    context.env = TestFileEnvironment("./tmp")
