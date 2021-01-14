from rich import traceback
from scripttest import TestFileEnvironment

# Generates nice stack traces
traceback.install()


def before_scenario(context, scenario):
    context.env = TestFileEnvironment("./tmp")
