import dataclasses
import json
import textwrap
import typing

import pydantic

from auto_qc import version
from auto_qc.evaluate import exception


class ThresholdNode(pydantic.BaseModel):
    """Validator for each node in the thresholds."""

    name: str
    fail_code: str
    rule: list[typing.Any]
    pass_msg: str | None = None
    fail_msg: str | None = None
    tags: list[str] | None = None


class AutoQC(pydantic.BaseModel):
    """Container for all data used by auto-qc."""

    model_config = pydantic.ConfigDict(coerce_numbers_to_str=True)

    version: str
    thresholds: list[ThresholdNode]
    data: dict[str, typing.Any]

    @pydantic.field_validator("version")
    @classmethod
    def validate_version(cls, ver: str) -> str:
        """Validate the version number in the threshold files is correct."""
        if version.major_version(ver) != version.major_version(version.__version__):
            raise exception.VersionNumberException(
                textwrap.dedent(
                    f"""
            Incompatible threshold file syntax: {ver}.
            This release of auto-qc ({version.__version__}) requires major version {version.major_version(version.__version__)}, e.g. '{version.__version__}'.
                    """
                )
            )
        return ver


class TestCase(pydantic.BaseModel):
    """A single case in a test suite: a data document and its expected outcome."""

    name: str
    data: dict[str, typing.Any]
    expect: str = "pass"
    codes: list[str] | None = None

    @pydantic.field_validator("expect")
    @classmethod
    def validate_expect(cls, value: str) -> str:
        """Normalise and validate the expected outcome."""
        normalised = value.lower()
        if normalised not in ("pass", "fail"):
            raise ValueError("expect must be 'pass' or 'fail'")
        return normalised


class TestSuite(pydantic.BaseModel):
    """A suite of test cases run against a thresholds file."""

    thresholds: str
    cases: list[TestCase]


@dataclasses.dataclass(frozen=True)
class AutoQCEvaluation:
    """Container for the result of evaluating the QC dictionary."""

    is_pass: bool
    fail_codes: list[str]
    evaluation: list[dict[str, typing.Any]]

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
                "qc": [{k: v for k, v in x.items() if k != "variables"} for x in self.evaluation],
                "auto_qc_version": version.__version__,
                "pass": self.is_pass,
                "fail_codes": self.fail_codes,
            },
            indent=4,
            sort_keys=True,
            # YAML parses unquoted dates/times into datetime objects; render
            # any non-JSON value as its string form rather than crashing.
            default=str,
        )
