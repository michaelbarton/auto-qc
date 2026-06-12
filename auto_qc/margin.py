"""Report how close each numeric comparison is to flipping its result.

The default output answers *whether* a sample passes. ``--margin`` answers *how
robustly*: for every ordered numeric comparison in a rule it reports the
**slack** — the distance the metric could move before that comparison flips. A
coverage rule cleared by ``0.1`` is passing fragilely; one cleared by ``30`` is
passing comfortably, and the difference matters when deciding whether to trust a
whole batch.

Only the ordered comparisons have a continuous margin (``greater_than``,
``greater_equal_than``, ``less_than``, ``less_equal_than`` and ``between``).
Equality, string and membership tests are discrete — there is no "how far" to
report — so they are skipped. For a rule that is a single comparison the slack
is exactly the rule's distance to flipping; for a compound rule it is reported
per comparison, since the binding constraint then depends on the data.
"""

import dataclasses
import typing

from rich.console import Console
from rich.markup import escape

from auto_qc import models, node


@dataclasses.dataclass(frozen=True)
class Comparison:
    """One numeric comparison within a rule, with its slack to the boundary."""

    slack: float
    holds: bool
    description: str


def _format_value(value: typing.Any) -> str:
    """Render a resolved operand value compactly for the report."""
    if isinstance(value, bool):
        return repr(value)
    if isinstance(value, float):
        return f"{value:g}"
    if isinstance(value, int):
        return str(value)
    return repr(value)


def _describe_operand(trace: node.Trace) -> str:
    """Describe one operand of a comparison, with its pointer resolved."""
    if trace.kind == "variable":
        return f"{trace.variable}={_format_value(trace.result)}"
    if trace.kind in ("literal", "list"):
        return _format_value(trace.result)
    # A nested application, e.g. arithmetic feeding the comparison.
    return f"{(trace.operator or '').lower()}(…)={_format_value(trace.result)}"


def _describe(trace: node.Trace) -> str:
    """Describe a comparison node, e.g. ``:coverage/mean_depth=30.1 greater_than 30``."""
    name = (trace.operator or "").lower()
    operands = [_describe_operand(child) for child in trace.children]
    if name == "between":
        return f"{operands[0]} between {operands[1]} and {operands[2]}"
    return f"{operands[0]} {name} {operands[1]}"


def collect(trace: node.Trace) -> list[Comparison]:
    """Collect every measurable numeric comparison within ``trace``."""
    comparisons: list[Comparison] = []
    if trace.kind == "operator":
        if trace.margin is not None:
            comparisons.append(
                Comparison(
                    slack=trace.margin,
                    holds=bool(trace.result),
                    description=_describe(trace),
                )
            )
        for child in trace.children:
            comparisons.extend(collect(child))
    return comparisons


def _slack_text(comparison: Comparison) -> str:
    """Phrase a comparison's slack as passing room or a shortfall."""
    magnitude = f"{abs(comparison.slack):g}"
    return f"slack {magnitude}" if comparison.holds else f"short by {magnitude}"


def render(state: models.AutoQC, console: Console) -> None:
    """Print the slack of every numeric comparison in each rule."""
    for threshold in state.thresholds:
        trace = node.evaluate(threshold.rule, state.data)
        status = "[bold green]PASS[/bold green]" if trace.result else "[bold red]FAIL[/bold red]"
        console.print(
            f"{status} {escape(threshold.name)} [dim]({escape(threshold.fail_code)})[/dim]"
        )

        comparisons = collect(trace)
        if not comparisons:
            console.print("    [dim]no numeric comparisons to measure[/dim]")
            console.print()
            continue

        tightest = min(comparisons, key=lambda comparison: abs(comparison.slack))
        for comparison in comparisons:
            mark = "[green]✓[/green]" if comparison.holds else "[red]✗[/red]"
            note = " [dim]← tightest[/dim]" if comparison is tightest else ""
            console.print(
                f"    {mark} {escape(comparison.description)} "
                f"[dim]→[/dim] [yellow]{escape(_slack_text(comparison))}[/yellow]{note}"
            )
        console.print()
