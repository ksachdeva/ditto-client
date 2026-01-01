import asyncio
from typing import cast

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from typer import Typer

from ditto_client.generated.ditto_client import DittoClient

devops_app = Typer()


@devops_app.command()
def whoami(ctx: typer.Context) -> None:
    """Get current user information."""

    client = cast(DittoClient, ctx.obj)

    async def _run() -> None:
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
