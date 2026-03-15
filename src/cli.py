from pathlib import Path
from typing import Any

import typer
from typer import Typer

from src.inbox.core import InboxApp
from src.sources.repository import REGISTRY

cli = Typer(no_args_is_help=True)


@cli.command("plugins")
def plugins_list() -> None:
    typer.echo("Available plugins:")
    for name in sorted(REGISTRY):
        typer.echo(name)


def _build_sources(stdin: bool, jsonl: list[Path]) -> list[Any]:
    sources: list[Any] = []
    if stdin:
        sources.append(REGISTRY["stdin"]())
    for path in jsonl:
        sources.append(REGISTRY["file-jsonl"](path))
    return sources


@cli.command("read")
def read(
    stdin: bool = typer.Option(False, "--stdin", help="Read messages from stdin"),
    jsonl: list[Path] = typer.Option(
        help="Read task from JSONL file",
        default_factory=list,
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    contains: str | None = typer.Option(None, "--contains", help="Substring filter"),
):
    raw_sources = _build_sources(stdin, jsonl)
    inbox = InboxApp(raw_sources)
    numbers = 0
    for task in inbox.iter_messages():
        if contains and contains not in str(task.payload):
            continue
        numbers += 1
        typer.echo(f"[{task.id}] payload: {task.payload}")

    typer.echo(f"\nTotal tasks: {numbers}")
