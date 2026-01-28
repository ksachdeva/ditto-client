import asyncio
import json
from pathlib import Path
from typing import Annotated, cast

import typer
from typer import Typer

from ditto_client.cli.utils._output import extract_additional_data, output_error, output_json, output_success, output_warning
from ditto_client.generated.ditto_client import DittoClient
from ditto_client.generated.models.new_policy import NewPolicy

policy_app = Typer()


@policy_app.command()
def create(
    ctx: typer.Context,
    policy_id: Annotated[str, typer.Argument(help="The ID of the policy to create")],
    policy_file: Annotated[Path, typer.Argument(help="Path to JSON file containing policy definition")],
) -> None:
    """Create a new policy."""

    client = cast(DittoClient, ctx.obj)

    async def _run() -> None:
        # Read the policy data
        policy_data = json.loads(policy_file.read_text())

        # Create the new policy
        new_policy = NewPolicy(additional_data=policy_data)

        response = await client.api.two.policies.by_policy_id(policy_id).put(body=new_policy)

        if response:
            output_success(f"Successfully created policy '{policy_id}'")
            output_json(extract_additional_data(response))
        else:
            output_error(f"Failed to create policy '{policy_id}'")

    asyncio.run(_run())


@policy_app.command()
def get(
    ctx: typer.Context,
    policy_id: Annotated[str, typer.Argument(help="The ID of the policy to retrieve")],
) -> None:
    """Get a specific policy by ID."""
    client = cast(DittoClient, ctx.obj)

    async def _run() -> None:
        response = await client.api.two.policies.by_policy_id(policy_id).get()

        if not response:
            output_error(f"Policy '{policy_id}' not found")
            return

        output_json(_extract_additional_data(response))

    asyncio.run(_run())


@policy_app.command()
def entries(
    ctx: typer.Context,
    policy_id: Annotated[str, typer.Argument(help="The ID of the policy")],
) -> None:
    """List policy entries."""
    client = cast(DittoClient, ctx.obj)

    async def _run() -> None:
        response = await client.api.two.policies.by_policy_id(policy_id).entries.get()

        if not response:
            output_warning("No policy entries found")
            return

        output_json(_extract_additional_data(response))

    asyncio.run(_run())


@policy_app.command()
def delete(
    ctx: typer.Context,
    policy_id: Annotated[str, typer.Argument(help="The ID of the policy to delete")],
    confirm: Annotated[bool, typer.Option(help="Skip confirmation prompt")] = False,
) -> None:
    """Delete a policy."""

    if not confirm:
        if not typer.confirm(f"Are you sure you want to delete policy '{policy_id}'?"):
            output_warning("Operation cancelled")
            return

    client = cast(DittoClient, ctx.obj)

    async def _run() -> None:
        await client.api.two.policies.by_policy_id(policy_id).delete()
        output_success(f"Successfully deleted policy '{policy_id}'")

    asyncio.run(_run())
