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
        help="Read messages from stdin",
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
    for msg in inbox.iter_messages():
        if contains and contains not in msg.message:
            continue
        numbers += 1
        typer.echo(f"[{msg.author}: {msg.id}] {msg.title}: {msg.message}")

    typer.echo(f"\nTotal: {numbers}")
