import difflib
import os

from nose import tools


def assert_file_permission(file_, expected):
    observed = oct(os.stat(file_).st_mode & 0o777)
    tools.assert_equal(
        expected, observed, "File '{}' has permission {} not {}.".format(file_, observed, expected)
    )


def assert_is_dictionary(x):
    tools.assert_is_instance(x, dict, "Should be a dictionary: {}".format(x))


def assert_is_list(x):
    tools.assert_is_instance(x, list, "Should be a list: {}".format(x))


def assert_is_string(x):
    tools.assert_is_instance(x, str, "Should be a string: {}".format(x))


def assert_not_empty(x):
    tools.assert_not_equal(len(x), 0, "Should not be empty")


def assert_empty(xs):
    tools.assert_equal(0, len(xs), "{} is not empty".format(str(xs)))


def assert_string_equal_with_diff(str1, str2):
    assert_is_string(str1)
    assert_is_string(str2)
    if not str1 == str2:
        diff = difflib.Differ().compare(str1.split("\n"), str2.split("\n"))
        tools.assert_false(True, "\n" + "\n".join(diff))
