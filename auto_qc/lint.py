"""Statically check the *rules* themselves, before any data is involved.

``--explain`` and ``--margin`` answer questions about one sample. ``--lint``
answers a question about the thresholds file alone: *can these rules even do what
they claim?* Because a rule is an s-expression — an inspectable tree — some
mistakes are decidable without ever seeing a metric:

- a rule that can never pass (e.g. ``and`` of ``greater_than :x 30`` and
  ``less_than :x 10`` — no value is both), which would silently fail every
  sample;
- a ``between`` whose bounds are reversed, an empty range;
- a rule with no metric pointers at all, so its outcome is fixed regardless of
  the data.

The analysis is deliberately *sound*: it only reports a problem it can prove, and
stays quiet on anything it cannot reason about (``or`` / ``not`` branches, nested
arithmetic), so a clean lint never means "looks fine" by guesswork — it means no
provable contradiction exists.
"""

import dataclasses
import math
import typing

from rich.console import Console
from rich.markup import escape

from auto_qc import models, node, variable
from auto_qc.evaluate import exception

# Operators whose ``[op, variable, number]`` form constrains one numeric metric.
_ORDERED = {"greater_than", "greater_equal_than", "less_than", "less_equal_than"}


@dataclasses.dataclass(frozen=True)
class Finding:
    """One problem found in a threshold's rule.

    ``severity`` is ``"error"`` for a rule that can never behave as a gate (it
    always fails, or always errors) and ``"warning"`` for one that is merely
    suspicious (it always passes), so callers can fail CI on errors alone.
    """

    severity: str  # "error" | "warning"
    name: str
    fail_code: str
    message: str


def _is_number(value: typing.Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


@dataclasses.dataclass
class _Interval:
    """The set of values still allowed for one metric as constraints accumulate.

    Tracks the tightest lower and upper bound seen so far, each with whether it
    is inclusive and a human phrase describing where it came from, so a
    contradiction can be reported in the rule author's own terms.
    """

    low: float = -math.inf
    low_inclusive: bool = True
    low_desc: str = ""
    high: float = math.inf
    high_inclusive: bool = True
    high_desc: str = ""

    def tighten_low(self, value: float, inclusive: bool, desc: str) -> None:
        if value > self.low or (value == self.low and not inclusive and self.low_inclusive):
            self.low, self.low_inclusive, self.low_desc = value, inclusive, desc

    def tighten_high(self, value: float, inclusive: bool, desc: str) -> None:
        if value < self.high or (value == self.high and not inclusive and self.high_inclusive):
            self.high, self.high_inclusive, self.high_desc = value, inclusive, desc

    def is_empty(self) -> bool:
        if self.low > self.high:
            return True
        return self.low == self.high and not (self.low_inclusive and self.high_inclusive)


def _flatten_conjuncts(expr: typing.Any) -> list[typing.Any]:
    """Split a rule into the parts that must *all* hold for it to pass.

    Descends only through ``and`` — the one combinator under which every branch
    is required. An ``or`` or ``not`` is returned whole, since its branches are
    not jointly required and reasoning into them would be unsound.
    """
    if node.is_application(expr) and expr[0].lower() == "and":
        conjuncts: list[typing.Any] = []
        for argument in expr[1:]:
            conjuncts.extend(_flatten_conjuncts(argument))
        return conjuncts
    return [expr]


def _apply_constraint(conjunct: typing.Any, intervals: dict[str, _Interval]) -> None:
    """Fold one comparison into the running interval for the metric it bounds.

    Recognises ``[ordered_op, variable, number]`` (either operand order),
    ``[equals, variable, number]`` and ``[between, variable, low, high]``.
    Anything else carries no interval information and is left untouched.
    """
    if not node.is_application(conjunct):
        return
    op = conjunct[0].lower()
    args = conjunct[1:]

    if op == "between" and len(args) == 3 and variable.is_variable(args[0]):
        var, low, high = args
        if _is_number(low) and _is_number(high):
            interval = intervals.setdefault(var, _Interval())
            interval.tighten_low(float(low), True, f"between {low:g} and {high:g}")
            interval.tighten_high(float(high), True, f"between {low:g} and {high:g}")
        return

    if op not in _ORDERED and op != "equals":
        return
    if len(args) != 2:
        return

    # Normalise to ``variable OP number`` regardless of which side the metric is.
    if variable.is_variable(args[0]) and _is_number(args[1]):
        var, number, flipped = args[0], float(args[1]), False
    elif variable.is_variable(args[1]) and _is_number(args[0]):
        var, number, flipped = args[1], float(args[0]), True
    else:
        return

    interval = intervals.setdefault(var, _Interval())
    if op == "equals":
        interval.tighten_low(number, True, f"= {number:g}")
        interval.tighten_high(number, True, f"= {number:g}")
        return

    # ``[gt, 30, :x]`` means ``30 > x`` i.e. ``x < 30``: flip the direction.
    lower = op in ("greater_than", "greater_equal_than")
    if flipped:
        lower = not lower
    inclusive = op in ("greater_equal_than", "less_equal_than")
    symbol = (">" if lower else "<") + ("=" if inclusive else "")
    if lower:
        interval.tighten_low(number, inclusive, f"{symbol} {number:g}")
    else:
        interval.tighten_high(number, inclusive, f"{symbol} {number:g}")


def _unsatisfiable_message(var: str, interval: _Interval) -> str:
    """Phrase an empty interval as a contradiction in the metric's own bounds."""
    if interval.low_desc == interval.high_desc:
        return f"{var} {interval.low_desc} is an empty range — no value satisfies it."
    return f"{var} cannot be both {interval.low_desc} and {interval.high_desc}."


def _analyse_rule(rule: list[typing.Any]) -> tuple[str, str] | None:
    """Return ``(severity, message)`` if ``rule`` is provably broken, else ``None``."""
    if not variable.get_variable_names(rule):
        # No metric pointers: the outcome is fixed, so evaluate it directly.
        try:
            result = node.evaluate(rule, {}).result
        except exception.EvaluationError as err:
            return ("error", f"rule always errors regardless of data: {err}")
        if result is False:
            return ("error", "rule can never pass — it fails every sample.")
        if result is True:
            return ("warning", "rule always passes regardless of the data.")
        return ("warning", f"rule does not evaluate to true/false (got {result!r}).")

    intervals: dict[str, _Interval] = {}
    for conjunct in _flatten_conjuncts(rule):
        _apply_constraint(conjunct, intervals)
    for var, interval in intervals.items():
        if interval.is_empty():
            return ("error", _unsatisfiable_message(var, interval))
    return None


def analyse(state: models.AutoQC) -> list[Finding]:
    """Return every provable problem across all thresholds in ``state``."""
    findings: list[Finding] = []
    for threshold in state.thresholds:
        result = _analyse_rule(threshold.rule)
        if result is not None:
            severity, message = result
            findings.append(Finding(severity, threshold.name, threshold.fail_code, message))
    return findings


def render(findings: list[Finding], console: Console) -> None:
    """Print the lint findings, or a clean bill of health when there are none."""
    if not findings:
        console.print("[green]✓ No contradictions found in the thresholds.[/green]")
        return

    for finding in findings:
        if finding.severity == "error":
            mark, tag = "[red]✗[/red]", "[red]error[/red]"
        else:
            mark, tag = "[yellow]![/yellow]", "[yellow]warning[/yellow]"
        console.print(
            f"{mark} {tag} {escape(finding.name)} [dim]({escape(finding.fail_code)})[/dim]"
        )
        console.print(f"    [dim]{escape(finding.message)}[/dim]")

    errors = sum(1 for finding in findings if finding.severity == "error")
    warnings = len(findings) - errors
    console.print()
    console.print(f"[red]{errors} error(s)[/red], [yellow]{warnings} warning(s)[/yellow]")
