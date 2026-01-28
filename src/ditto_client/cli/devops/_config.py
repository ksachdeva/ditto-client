import asyncio
from typing import cast

import typer
from typer import Typer

from ditto_client.cli.utils._output import extract_additional_data, output_json, output_warning
from ditto_client.generated.ditto_client import DittoClient

config_app = Typer()


@config_app.command()
def get(ctx: typer.Context) -> None:
    """Get configuration from Ditto services."""

    client = cast(DittoClient, ctx.obj)

    async def _run() -> None:
        response = await client.devops.config.get()

        if not response:
            output_warning("No configuration found")
            return

        output_json(extract_additional_data(response))

    asyncio.run(_run())
