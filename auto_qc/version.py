__version__ = "3.0.0"


def major_version(ver: str) -> int:
    return int(ver.split(".")[0])
