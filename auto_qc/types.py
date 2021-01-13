import dataclasses
import json
import typing

from auto_qc import version


class AutoQCEvaluationError(Exception):
    """Auto QC specific error type."""

    pass


@dataclasses.dataclass(frozen=True)
class AutoqcEvaluation:
    """Container for the result of evaluating the QC dictionary."""

    is_pass: bool
    fail_codes: typing.List[str]
    evaluation = typing.List[typing.Dict[str, typing.Any]]

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
            {"qc": self.evaluation, "auto_qc_version": version.__version__},
            indent=4,
            sort_keys=True,
        )
