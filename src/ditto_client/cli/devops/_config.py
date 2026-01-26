import asyncio
import json
from typing import Any, cast

import typer
from rich import print as rprint
from typer import Typer

from ditto_client.generated.ditto_client import DittoClient

config_app = Typer()


def _output_json(data: Any) -> None:
    """Output data as JSON."""
    json_str = json.dumps(data, indent=2, default=str)
    print(json_str)


@config_app.command()
def get(ctx: typer.Context) -> None:
    """Get configuration from Ditto services."""

    client = cast(DittoClient, ctx.obj)

    async def _run() -> None:
        response = await client.devops.config.get()

        if not response:
            rprint("[yellow]No configuration found[/yellow]")
            return

        config_dict: dict[str, Any] = {}
        if hasattr(response, "additional_data") and response.additional_data:
            config_dict = response.additional_data
        _output_json(config_dict)

    asyncio.run(_run())
