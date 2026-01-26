import asyncio
import json
from pathlib import Path
from typing import Annotated, Any, cast

import typer
from rich import print as rprint
from typer import Typer

from ditto_client.generated.ditto_client import DittoClient
from ditto_client.generated.models.new_policy import NewPolicy

policy_app = Typer()


def _output_json(data: Any) -> None:
    """Output data as JSON."""
    json_str = json.dumps(data, indent=2, default=str)
    print(json_str)


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
            policy_dict: dict[str, Any] = {}
            if hasattr(response, "additional_data") and response.additional_data:
                policy_dict = response.additional_data
            _output_json(policy_dict)
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

        policy_dict: dict[str, Any] = {}
        if hasattr(response, "additional_data") and response.additional_data:
            policy_dict = response.additional_data
        _output_json(policy_dict)

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

        entries_dict: dict[str, Any] = {}
        if hasattr(response, "additional_data") and response.additional_data:
            entries_dict = response.additional_data
        _output_json(entries_dict)

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
