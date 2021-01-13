from auto_qc.util.workflow import validate_status_key
from os import makedirs
from os import path
import yaml


@validate_status_key("path")
def create_directory(path, status):

    makedirs(status[path])
    return status


@validate_status_key("contents")
def create_file(destination, contents, status):
    """
    Creates the given file with the given contents
    """
    if not path.isdir(path.dirname(status[destination])):
        status["error"] = "Internal Error - unable to create file: {}".format(status[destination])
    else:
        with open(status[destination], "w") as f:
            f.write(status[contents])
    return status


@validate_status_key("file_")
def chmod_file(file_, chmod_value, status):
    from os import chmod

    chmod(status[file_], chmod_value)
    return status


@validate_status_key("file_")
def read_file_contents(file_, destination, status):
    """
    Reads the file contents into the given key
    """
    with open(status[file_], "r") as f:
        status[destination] = f.read().strip()
    return status


@validate_status_key("file_")
def read_yaml_file(file_, destination, status):
    """
    Reads and parses the yaml file contents into the given key
    """

    s = read_file_contents(file_, destination, status)
    s[destination] = yaml.safe_load(s[destination])
    return status


def import_file(directory, file_name, destination, status):
    file_ = path.join(directory, file_name)
    with open(file_, "r") as f:
        contents = f.read().strip()

    try:
        status[destination] = contents.format(**status)
    except KeyError as e:
        status["error"] = "Internal Error - Can't interpolate file: {}, key: {}.".format(
            file_name, e
        )

    return status


def import_asset(asset_name, destination, status):
    asset_path = path.join(path.dirname(path.realpath(__file__)), "../../assets/")
    return import_file(asset_path, asset_name, destination, status)


@validate_status_key("contents")
def print_yaml(contents, status):
    from yaml import dump
    from sys import stdout

    stdout.write(dump(status[contents], default_flow_style=False))
    return status
