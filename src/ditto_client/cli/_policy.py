import asyncio
import json
from pathlib import Path
from typing import Annotated, cast

import typer
from rich import print as rprint
from typer import Typer

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
            rprint(f"[green]Successfully created policy '{policy_id}'[/green]")
            rprint(response)
        else:
            rprint(f"[red]Failed to create policy '{policy_id}'[/red]")

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
            rprint(f"[red]Policy '{policy_id}' not found[/red]")
            return

        rprint(response)

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
            rprint("[yellow]No policy entries found[/yellow]")
            return

        rprint(response)

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
            rprint("[yellow]Operation cancelled[/yellow]")
            return

    client = cast(DittoClient, ctx.obj)

    async def _run() -> None:
        await client.api.two.policies.by_policy_id(policy_id).delete()
        rprint(f"[green]Successfully deleted policy '{policy_id}'[/green]")

    asyncio.run(_run())
