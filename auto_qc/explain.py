"""Render a rich tree explaining how each QC rule was evaluated.

The standard ``PASS`` / ``FAIL: <code>`` output answers *whether* a sample
passed. ``--explain`` answers *why*: it renders the :class:`~auto_qc.node.Trace`
produced by the one evaluator, resolving each metric pointer to its value and
marking the passing and failing branches, so a failure is self-explanatory.
"""

import typing

from rich.console import Console
from rich.markup import escape
from rich.tree import Tree

from auto_qc import models, node


def _mark(value: typing.Any) -> str:
    if value is True:
        return "[green]✓[/green]"
    if value is False:
        return "[red]✗[/red]"
    return "[blue]•[/blue]"


def _operator_label(op: str, result: typing.Any) -> str:
    name = escape(op.lower())
    if isinstance(result, bool):
        color = "green" if result else "red"
        return f"{_mark(result)} [bold {color}]{name}[/bold {color}]"
    return (
        f"{_mark(result)} [bold]{name}[/bold] [dim]→[/dim] [yellow]{escape(repr(result))}[/yellow]"
    )


def _render_trace(trace: node.Trace) -> Tree:
    """Turn a :class:`~auto_qc.node.Trace` into a rich tree."""
    if trace.kind == "variable":
        label = (
            f"[cyan]{escape(str(trace.variable))}[/cyan] [dim]=[/dim] "
            f"[yellow]{escape(repr(trace.result))}[/yellow]"
        )
        return Tree(label)

    if trace.kind in ("literal", "list"):
        return Tree(f"[yellow]{escape(repr(trace.result))}[/yellow]")

    tree = Tree(_operator_label(trace.operator or "", trace.result))
    for child in trace.children:
        tree.add(_render_trace(child))
    return tree


def render(state: models.AutoQC, console: Console) -> None:
    """Print an evaluation tree for every threshold in the QC document."""
    for threshold in state.thresholds:
        trace = node.evaluate(threshold.rule, state.data)
        status = "[bold green]PASS[/bold green]" if trace.result else "[bold red]FAIL[/bold red]"
        root = Tree(f"{status} {escape(threshold.name)} [dim]({escape(threshold.fail_code)})[/dim]")
        root.add(_render_trace(trace))
        console.print(root)
        console.print()
