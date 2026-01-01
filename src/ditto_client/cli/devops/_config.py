import asyncio
from typing import cast

import typer
from rich import print as rprint
from typer import Typer

from ditto_client.generated.ditto_client import DittoClient

config_app = Typer()


@config_app.command()
def get(ctx: typer.Context) -> None:
    """Get configuration from Ditto services."""

    client = cast(DittoClient, ctx.obj)

    async def _run() -> None:
        response = await client.devops.config.get()

        if not response:
            rprint("[yellow]No configuration found[/yellow]")
            return

        rprint(response)

    asyncio.run(_run())
