import difflib as dl
import os
import types as ty

import nose.tools as nt


def assert_file_permission(file_, expected):
    observed = oct(os.stat(file_).st_mode & 0o777)
    nt.assert_equal(
        expected, observed, "File '{}' has permission {} not {}.".format(file_, observed, expected)
    )


def assert_is_dictionary(x):
    nt.assert_is_instance(x, ty.DictType, "Should be a dictionary: {}".format(x))


def assert_is_list(x):
    nt.assert_is_instance(x, ty.ListType, "Should be a list: {}".format(x))


def assert_is_string(x):
    nt.assert_is_instance(x, str, "Should be a string: {}".format(x))


def assert_not_empty(x):
    nt.assert_not_equal(len(x), 0, "Should not be empty")


def assert_empty(xs):
    nt.assert_equal(0, len(xs), "{} is not empty".format(str(xs)))


def assert_diff(str1, str2):
    assert_is_string(str1)
    assert_is_string(str2)
    diff = dl.Differ().compare(str1.split("\n"), str2.split("\n"))
    str_diff = "\n" + "\n".join(diff)
    nt.assert_equal(str1, str2, str_diff)
