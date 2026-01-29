import asyncio
import json
from pathlib import Path
from typing import Annotated, cast

import typer
from typer import Context, Typer

from ditto_client._types import CmdState
from ditto_client.cli._output import output_json, output_message
from ditto_client.generated.models.permission_check_request import PermissionCheckRequest

permission_app = Typer()


@permission_app.command()
def check(
    ctx: Context,
    request_file: Annotated[Path, typer.Argument(help="Path to JSON file containing permission check request")],
) -> None:
    """Check permissions on specified resources."""
    state = cast(CmdState, ctx.obj)

    async def _run() -> None:
        # Read the permission check request data
        request_data = json.loads(request_file.read_text())

        # Create the permission check request
        permission_request = PermissionCheckRequest(additional_data=request_data)

        response = await state.client.api.two.check_permissions.post(body=permission_request)

        if not response:
            output_message("Permission check failed", level="error")
            return

        # Display the permission check results
        if response.additional_data:
            output_json(response.additional_data)
        else:
            output_message("No permission check results returned", level="warning")

    asyncio.run(_run())
