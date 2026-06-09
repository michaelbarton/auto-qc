"""Render a rich tree explaining how each QC rule was evaluated.

The standard ``PASS`` / ``FAIL: <code>`` output answers *whether* a sample
passed. ``--explain`` answers *why*: it walks the s-expression of every rule,
resolves each metric pointer to its value, and prints the evaluation tree with
the passing and failing branches marked, so a failure is self-explanatory.
"""

import typing

from rich.console import Console
from rich.markup import escape
from rich.tree import Tree

from auto_qc import models, node, variable


def _is_rule(expr: typing.Any) -> bool:
    """Is the expression a nested rule (a list led by a known operator)?"""
    return isinstance(expr, list) and len(expr) > 0 and node.is_operator(expr[0])


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


def _leaf(expr: typing.Any, data: dict[str, typing.Any]) -> tuple[typing.Any, Tree]:
    if variable.is_variable(expr):
        value = variable.get_variable_value(data, expr)
        label = f"[cyan]{escape(expr)}[/cyan] [dim]=[/dim] [yellow]{escape(repr(value))}[/yellow]"
        return value, Tree(label)
    return expr, Tree(f"[yellow]{escape(repr(expr))}[/yellow]")


def _evaluate(expr: typing.Any, data: dict[str, typing.Any]) -> tuple[typing.Any, Tree]:
    """Evaluate an s-expression, returning its value and a tree explaining it."""
    if not _is_rule(expr):
        return _leaf(expr, data)

    op = expr[0]
    children = [_evaluate(arg, data) for arg in expr[1:]]
    result = node.OPERATORS[op.lower()](*[value for value, _ in children])

    tree = Tree(_operator_label(op, result))
    for _, child_tree in children:
        tree.add(child_tree)
    return result, tree


def render(state: models.AutoQC, console: Console) -> None:
    """Print an evaluation tree for every threshold in the QC document."""
    for threshold in state.thresholds:
        result, rule_tree = _evaluate(threshold.rule, state.data)
        status = "[bold green]PASS[/bold green]" if result else "[bold red]FAIL[/bold red]"
        root = Tree(f"{status} {escape(threshold.name)} [dim]({escape(threshold.fail_code)})[/dim]")
        root.add(rule_tree)
        console.print(root)
        console.print()
