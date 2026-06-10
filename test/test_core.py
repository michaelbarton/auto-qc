import pytest

import auto_qc
from auto_qc import AutoQCError, run


def test_public_api_exports():
    """The top-level package exposes the documented public API."""
    assert hasattr(auto_qc, "run")
    assert hasattr(auto_qc, "AutoQCEvaluation")
    assert hasattr(auto_qc, "AutoQCError")
    assert auto_qc.__version__


def test_run_returns_pass_for_satisfied_rules():
    thresholds = {
        "version": auto_qc.__version__,
        "thresholds": [
            {
                "name": "coverage",
                "fail_code": "LOW_COVERAGE",
                "rule": ["greater_than", ":depth", 10],
            }
        ],
    }
    evaluation = run(thresholds, {"depth": 20})
    assert evaluation.is_pass
    assert evaluation.fail_codes == []


def test_run_returns_fail_codes_for_failed_rules():
    thresholds = {
        "version": auto_qc.__version__,
        "thresholds": [
            {
                "name": "coverage",
                "fail_code": "LOW_COVERAGE",
                "rule": ["greater_than", ":depth", 10],
            }
        ],
    }
    evaluation = run(thresholds, {"depth": 5})
    assert not evaluation.is_pass
    assert evaluation.fail_codes == ["LOW_COVERAGE"]


def test_invalid_document_raises_autoqc_error_not_pydantic():
    """Validation failures are wrapped so callers only catch AutoQCError."""
    thresholds = {
        "version": auto_qc.__version__,
        "thresholds": [{"name": "missing fail_code", "rule": ["greater_than", ":depth", 10]}],
    }
    with pytest.raises(AutoQCError):
        run(thresholds, {"depth": 5})
