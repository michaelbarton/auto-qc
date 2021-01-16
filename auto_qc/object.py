import dataclasses
import json
import textwrap
import typing

import funcy
import pydantic

from auto_qc import version
from auto_qc.evaluate import exception


class ThresholdNode(pydantic.BaseModel):
    """Validator for each node in the thresholds."""

    name: str
    fail_code: str
    rule: typing.List[typing.Any]


class Thresholds(pydantic.BaseModel):
    """Validator for the thresholds object."""

    version: str
    thresholds: typing.List[ThresholdNode]

    @pydantic.validator("version")
    def validate_version(cls, ver: str) -> str:
        """Validate the version number in the threshold files is correct."""
        if version.major_version(ver) != version.major_version(version.__version__):
            raise exception.VersionNumberException(
                textwrap.dedent(
                    f"""
            Incompatible threshold file syntax: {ver}.
            Please update the syntax to version >= {version.__version__}.0.0.
                    """
                )
            )
        return ver


class AutoQC(pydantic.BaseModel):
    """Container for all data used by auto-qc."""

    thresholds: Thresholds
    data: typing.Dict[str, typing.Any]


@dataclasses.dataclass(frozen=True)
class AutoQCEvaluation:
    """Container for the result of evaluating the QC dictionary."""

    is_pass: bool
    fail_codes: typing.List[str]
    evaluation: typing.List[typing.Dict[str, typing.Any]]

    def to_evaluation_string(self, json_output: bool) -> str:
        """Generate a string representation of the auto-qc evaluation tree.

        Args:
            json_output: Whether or not to return as JSON.

        Returns:
            String representation of the evaluation state.

        """

        if not json_output:
            return "PASS" if self.is_pass else f"FAIL: {', '.join(self.fail_codes)}"

        return json.dumps(
            {
                "qc": [funcy.omit(x, ["variables"]) for x in self.evaluation],
                "auto_qc_version": version.__version__,
                "pass": self.is_pass,
                "fail_codes": self.fail_codes,
            },
            indent=4,
            sort_keys=True,
        )
