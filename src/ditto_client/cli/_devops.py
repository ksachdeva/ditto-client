# ruff: noqa: B008

import asyncio

from rich import print as rprint
from rich.console import Console
from rich.table import Table
from typer import Typer

from ._utils import create_ditto_client

devops_app = Typer()


@devops_app.command()
def whoami() -> None:
    """Get current user information."""

    async def _run() -> None:
        client = create_ditto_client()

        response = await client.api.two.whoami.get()

        if not response:
            rprint("[red]Failed to get user information[/red]")
            return

        # Create a table for better display
        table = Table(title="Current User Information")
        table.add_column("Property", justify="right", style="cyan", no_wrap=True)
        table.add_column("Value", justify="left", style="green")

        table.add_row("Default Subject", response.default_subject or "N/A")
        table.add_row("Subjects", ", ".join(response.subjects) if response.subjects else "None")

        console = Console()
        console.print(table)

    asyncio.run(_run())
