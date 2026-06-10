"""auto-qc: evaluate metrics against declarative pass/fail rules.

The public API is intentionally small::

    from auto_qc import run

    evaluation = run(thresholds, data)
    evaluation.is_pass     # bool
    evaluation.fail_codes  # list[str]
"""

from auto_qc.core import build, run
from auto_qc.exception import AutoQCError
from auto_qc.models import AutoQC, AutoQCEvaluation, ThresholdNode
from auto_qc.version import __version__

__all__ = [
    "AutoQC",
    "AutoQCError",
    "AutoQCEvaluation",
    "ThresholdNode",
    "__version__",
    "build",
    "run",
]
