"""Output utilities for CLI commands."""

import json
from typing import Any

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from ditto_client.generated.models.thing import Thing


def get_table_flag(ctx: typer.Context) -> bool:
    """Get the table flag from context by traversing up the parent chain."""
    current: typer.Context | None = ctx
    while current:
        if hasattr(current, "meta") and current.meta and "table" in current.meta:
            return current.meta["table"]
        if hasattr(current, "parent"):
            current = current.parent
        else:
            break
    return False


def output_json(data: Any) -> None:
    """Output data as JSON"""
    json_str = json.dumps(data, indent=2, default=str)
    print(json_str)


def output_table(title: str, columns: list[tuple[str, str, str]], rows: list[list[str]]) -> None:
    """Output data as a rich table"""
    table = Table(title=title)
    for name, justify, style in columns:
        table.add_column(name, justify=justify, style=style, no_wrap=True)

    for row in rows:
        table.add_row(*row)

    console = Console()
    console.print(table)


def output_error(message: str) -> None:
    """Output an error message."""
    rprint(f"[red]{message}[/red]")


def output_warning(message: str) -> None:
    """Output a warning message."""
    rprint(f"[yellow]{message}[/yellow]")


def output_success(message: str) -> None:
    """Output a success message."""
    rprint(f"[green]{message}[/green]")


def thing_to_dict(thing: Thing) -> dict[str, Any]:
    """Convert a Thing object to a dictionary."""
    thing_dict: dict[str, Any] = {}
    if thing.thing_id:
        thing_dict["thingId"] = thing.thing_id
    if thing.policy_id:
        thing_dict["policyId"] = thing.policy_id
    if thing.definition:
        thing_dict["definition"] = thing.definition
    if thing.attributes and thing.attributes.additional_data:
        thing_dict["attributes"] = thing.attributes.additional_data
    if thing.features and thing.features.additional_data:
        thing_dict["features"] = thing.features.additional_data
    return thing_dict


def extract_additional_data(response: Any) -> dict[str, Any]:
    """Extract additional_data from a response object."""
    if hasattr(response, "additional_data") and response.additional_data:
        return response.additional_data
    return {}
