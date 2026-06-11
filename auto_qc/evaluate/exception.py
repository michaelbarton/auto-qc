from auto_qc.exception import AutoQCError


class VersionNumberException(AutoQCError):
    """Incorrect version number error."""

    pass


class EvaluationError(AutoQCError):
    """Raised when a rule cannot be evaluated, e.g. comparing a number to text.

    A subclass of :class:`~auto_qc.exception.AutoQCError` so that callers only
    ever need to catch ``AutoQCError``. Carries an operator-level message; the
    caller adds the rule name for context.
    """

    pass
