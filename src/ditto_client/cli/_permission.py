import asyncio
import json
from pathlib import Path
from typing import Annotated, cast

import typer
from typer import Typer

from ditto_client.cli.utils._output import output_error, output_json, output_warning
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
            output_error("Permission check failed")
            return

        # Display the permission check results
        if response.additional_data:
            output_json(response.additional_data)
        else:
            output_warning("No permission check results returned")

    asyncio.run(_run())
