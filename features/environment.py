from scripttest import TestFileEnvironment
from rich import traceback

# Generates nice stack traces
traceback.install()


def before_scenario(context, scenario):
    context.env = TestFileEnvironment("./tmp")
