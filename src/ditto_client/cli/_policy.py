import asyncio
import json
from pathlib import Path
from typing import Annotated, cast

import typer
from typer import Context, Typer

from ditto_client._types import CmdState
from ditto_client.cli._output import model_to_dict, output_json, output_message
from ditto_client.generated.models.new_policy import NewPolicy
from ditto_client.generated.models.policy_entries import PolicyEntries

policy_app = Typer()


@policy_app.command()
def create(
    ctx: Context,
    policy_id: Annotated[str, typer.Argument(help="The ID of the policy to create")],
    policy_file: Annotated[Path, typer.Argument(help="Path to JSON file containing policy definition")],
) -> None:
    """Create a new policy."""
    state = cast(CmdState, ctx.obj)

    async def _run() -> None:
        # Read the policy data
        policy_data = json.loads(policy_file.read_text())

        # Create the new policy
        new_policy = NewPolicy(entries=PolicyEntries(additional_data=policy_data))

        response = await state.client.api.two.policies.by_policy_id(policy_id).put(body=new_policy)

        if response:
            output_message(f"Successfully created policy '{policy_id}'", level="success")
            output_json(model_to_dict(response))
        else:
            output_message(f"Failed to create policy '{policy_id}'", level="error")

    asyncio.run(_run())


@policy_app.command()
def get(
    ctx: Context,
    policy_id: Annotated[str, typer.Argument(help="The ID of the policy to retrieve")],
) -> None:
    """Get a specific policy by ID."""
    state = cast(CmdState, ctx.obj)

    async def _run() -> None:
        response = await state.client.api.two.policies.by_policy_id(policy_id).get()

        if not response:
            output_message(f"Policy '{policy_id}' not found", level="error")
            return

        output_json(model_to_dict(response))

    asyncio.run(_run())


@policy_app.command()
def entries(
    ctx: Context,
    policy_id: Annotated[str, typer.Argument(help="The ID of the policy")],
) -> None:
    """List policy entries."""
    state = cast(CmdState, ctx.obj)

    async def _run() -> None:
        response = await state.client.api.two.policies.by_policy_id(policy_id).entries.get()

        if not response:
            output_message("No policy entries found", level="warning")
            return

        output_json(model_to_dict(response))

    asyncio.run(_run())


@policy_app.command()
def delete(
    ctx: Context,
    policy_id: Annotated[str, typer.Argument(help="The ID of the policy to delete")],
    confirm: Annotated[bool, typer.Option(help="Skip confirmation prompt")] = False,
) -> None:
    """Delete a policy."""
    if not confirm:
        if not typer.confirm(f"Are you sure you want to delete policy '{policy_id}'?"):
            output_message("Operation cancelled", level="warning")
            return

    state = cast(CmdState, ctx.obj)

    async def _run() -> None:
        await state.client.api.two.policies.by_policy_id(policy_id).delete()
        output_message(f"Successfully deleted policy '{policy_id}'", level="success")

    asyncio.run(_run())
