import asyncio
import json
from pathlib import Path
from typing import Annotated, cast

import typer
from rich import print as rprint
from typer import Typer

from ditto_client.generated.ditto_client import DittoClient
from ditto_client.generated.models.permission_check_request import PermissionCheckRequest

permission_app = Typer()


@permission_app.command()
def check(
    ctx: typer.Context,
    request_file: Annotated[Path, typer.Argument(help="Path to JSON file containing permission check request")],
) -> None:
    """Check permissions on specified resources."""
    client = cast(DittoClient, ctx.obj)

    async def _run() -> None:
        # Read the permission check request data
        request_data = json.loads(request_file.read_text())

        # Create the permission check request
        permission_request = PermissionCheckRequest(additional_data=request_data)

        response = await client.api.two.check_permissions.post(body=permission_request)

        if not response:
            rprint("[red]Permission check failed[/red]")
            return

        # Display the permission check results
        if response.additional_data:
            rprint("[green]Permission Check Results:[/green]")
            rprint(json.dumps(response.additional_data, indent=2, default=str))
        else:
            rprint("[yellow]No permission check results returned[/yellow]")

    asyncio.run(_run())
