import json
import os.path

import behave
from nose import tools

from features.steps import assertions


@behave.given('I create the file "{target}"')
def create_file(context, target):
    context.env.run("touch", target)


@behave.given('I delete the {_} "{target}"')
def delete_file(context, _, target):
    context.env.run("rm", "-r", target)


@behave.given('I create the file "{target}" with the contents')
def create_file_with_contents(context, target):
    path = os.path.join(context.env.cwd, target)
    with open(path, "w") as f:
        f.write(context.text)


@behave.given('I create a "{delimiter}" delimited file "{target}" with the contents')
def create_delimited_file(context, delimiter, target):
    contents = "\n".join([delimiter.join(row) for row in context.table])

    path = os.path.join(context.env.cwd, target)
    with open(path, "w") as f:
        f.write(contents)


@behave.given('I gzip the file "{file_}"')
def gzip_file(context, file_):
    import gzip

    path = os.path.join(context.env.cwd, file_)
    with open(path, "rb") as f_in:
        with gzip.open(path + ".gz", "wb") as f_out:
            f_out.writelines(f_in)


@behave.given('I create the directory "{target}"')
def create_directory(context, target):
    path = os.path.join(context.env.cwd, target)
    os.makedirs(path)


@behave.when('I run the command "{command}" with the arguments')
def run_command_with_args(context, command):
    import re

    arguments = " ".join([" ".join(row) for row in context.table])
    arguments = re.sub(r"\s+", " ", arguments.strip())

    context.output = context.env.run(
        command, *arguments.split(" "), expect_error=True, expect_stderr=True
    )


@behave.when('I run the command "{command}"')
def run_command(context, command):
    context.output = context.env.run(command, expect_error=True, expect_stderr=True)


@behave.then('the standard {stream} should contains "{output}"')
def stream_should_contain_output(context, stream, output):
    if stream == "out":
        s = context.output.stdout
    elif stream == "error":
        s = context.output.stderr
    else:
        raise RuntimeError('Unknown stream "{}"'.format(stream))
    tools.assert_in(output, s)


@behave.then("the standard {stream} should contain")
def stream_should_contain(context, stream):
    if stream == "out":
        s = context.output.stdout
    elif stream == "error":
        s = context.output.stderr
    else:
        raise RuntimeError('Unknown stream "{}"'.format(stream))
    tools.assert_in(context.text.strip(), s)


@behave.then("the standard {stream} should equal")
def stream_should_equal(context, stream):
    if stream == "out":
        s = context.output.stdout
    elif stream == "error":
        s = context.output.stderr
    else:
        raise RuntimeError('Unknown stream "{}"'.format(stream))
    assertions.assert_string_equal_with_diff(context.text, s)


@behave.then("The exit code should be non-zero")
def exit_code_non_zero(context):
    tools.assert_not_equal(context.output.returncode, 0)


@behave.then("The exit code should be {code}")
def exit_code(context, code):
    tools.assert_equal(context.output.returncode, int(code))


@behave.then('the {thing} "{target}" should exist')
def should_exist(context, thing, target):
    tools.assert_in(
        target,
        list(context.output.files_created.keys()),
        "The {0} '{1}' does not exist.".format(thing, target),
    )


@behave.then('the {thing} "{target}" should not exist')
def should_not_exist(context, thing, target):
    tools.assert_not_in(
        target,
        list(context.output.files_created.keys()),
        "The {0} '{1}' does not exist.".format(thing, target),
    )


@behave.then("the files should exist")
def files_should_exist(context):
    for f in context.table:
        context.execute_steps('then the file "{}" should exist'.format(f["file"]))


@behave.then('the file "{target}" should exist with the contents')
def file_should_exist_with_contents(context, target):
    tools.assert_in(
        target,
        list(context.output.files_created.keys()),
        "The file '{}' does not exist.".format(target),
    )
    with open(context.output.files_created[target].full, "r") as f:
        assertions.assert_string_equal_with_diff(context.text, f.read())


@behave.then('the file "{target}" should contain "{contents}"')
def step_impt(context, target, contents):
    context.execute_steps(
        '''
       Then the file "{}" should exist with the contents:
       """
       {}
       """'''.format(
            target, contents
        )
    )


@behave.then('the file "{target}" should include')
def file_should_include(context, target):
    from re import search

    with open(context.output.files_created[target].full, "r") as f:
        contents = f.read()
        for row in context.table:
            regex = row["re_match"].strip()
            tools.assert_true(
                search(regex, contents), "RE '{}' not found in: \n{}".format(regex, contents)
            )


@behave.then('the file "{target}" should should have the permissions "{permission}"')
def file_should_have_permissions(context, target, permission):
    f = context.output.files_created[target].full
    assertions.assert_permission(f, permission)


@behave.then("the standard {stream} should be empty")
def stream_should_be_empty(context, stream):
    if stream == "out":
        s = context.output.stdout
    elif stream == "error":
        s = context.output.stderr
    else:
        raise RuntimeError('Unknown stream "{}"').format(stream)
    assertions.assert_empty(s)


@behave.then("the standard {stream} should not be empty")
def stream_should_not_be_empty(context, stream):
    if stream == "out":
        s = context.output.stdout
    elif stream == "error":
        s = context.output.stderr
    else:
        raise RuntimeError(f'Unknown stream "{stream}"')
    assertions.assert_not_empty(s)


@behave.then("the JSON-format standard {stream} should equal")
def json_stream_should_equal(context, stream):
    def refmt(t):
        """Reformat a JSON object so they have identical layout"""
        return json.dumps(json.loads(t), indent=4, sort_keys=True)

    if stream == "out":
        s = context.output.stdout
    elif stream == "error":
        s = context.output.stderr
    else:
        raise RuntimeError(f'Unknown stream "{stream}"')
    assertions.assert_string_equal_with_diff(refmt(context.text), refmt(s))
