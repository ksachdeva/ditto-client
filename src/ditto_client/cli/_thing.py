import asyncio
import json
from pathlib import Path
from typing import Annotated, Any, Optional, cast

import jsonpatch
import typer
from kiota_abstractions.base_request_configuration import RequestConfiguration
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from typer import Typer

from ditto_client.generated.api.two.things.things_request_builder import ThingsRequestBuilder
from ditto_client.generated.ditto_client import DittoClient
from ditto_client.generated.models.new_thing import NewThing
from ditto_client.generated.models.patch_thing import PatchThing
from ditto_client.generated.models.thing import Thing

thing_app = Typer()


def _get_table_flag(ctx: typer.Context) -> bool:
    """Get the table flag from context by traversing up the parent chain."""
    current = ctx
    while current:
        if hasattr(current, "meta") and current.meta and "table" in current.meta:
            return current.meta["table"]
        if hasattr(current, "parent"):
            current = current.parent
        else:
            break
    return False


def _output_json(data: Any) -> None:
    """Output data as JSON."""
    json_str = json.dumps(data, indent=2, default=str)
    print(json_str)


@thing_app.command()
def create(
    ctx: typer.Context,
    thing_id: Annotated[str, typer.Argument(help="The ID of the thing to create")],
    data_file: Annotated[Path, typer.Argument(help="Path to JSON file containing thing additional data")],
) -> None:
    """Create a new thing."""
    client = cast(DittoClient, ctx.obj)

    async def _run() -> None:
        # Build the thing data
        thing_data = json.loads(data_file.read_text())

        # Create the new thing
        new_thing = NewThing(additional_data=thing_data)

        await client.api.two.things.by_thing_id(thing_id).put(body=new_thing)
        rprint(f"[green]Successfully created thing '{thing_id}'[/green]")

    asyncio.run(_run())


@thing_app.command()
def list(
    ctx: typer.Context,
    fields: Annotated[
        Optional[str],
        typer.Option(
            "--fields", "-f", help="Comma-separated list of fields to include (e.g., 'thingId,attributes,features')"
        ),
    ] = None,
    ids: Annotated[Optional[str], typer.Option(help="Comma-separated list of thing IDs to retrieve")] = None,
    timeout: Annotated[Optional[str], typer.Option(help="Request timeout (e.g., '30s', '1m')")] = None,
) -> None:
    """List things from Ditto."""
    client = cast(DittoClient, ctx.obj)
    use_table = _get_table_flag(ctx)

    async def _run() -> None:
        # Build query parameters if provided
        request_config = None
        if fields or ids or timeout:
            query_params = ThingsRequestBuilder.ThingsRequestBuilderGetQueryParameters()
            if fields:
                query_params.fields = fields
            if ids:
                query_params.ids = ids
            if timeout:
                query_params.timeout = timeout

            request_config = RequestConfiguration(query_parameters=query_params)

        response = await client.api.two.things.get(request_configuration=request_config)

        if not response:
            if use_table:
                rprint("[yellow]No things found[/yellow]")
            else:
                _output_json([])
            return

        if use_table:
            table = Table(title="Ditto Things")
            table.add_column("Thing ID", justify="left", style="cyan", no_wrap=True)
            table.add_column("Features", justify="center", style="yellow")

            for thing in response:
                features_count = (
                    len(thing.features.additional_data) if thing.features and thing.features.additional_data else 0
                )
                table.add_row(thing.thing_id, str(features_count))

            console = Console()
            console.print(table)
        else:
            output_data = []
            for thing in response:
                thing_dict: dict[str, Any] = {}
                if thing.thing_id:
                    thing_dict["thingId"] = thing.thing_id
                if thing.policy_id:
                    thing_dict["policyId"] = thing.policy_id
                if thing.definition:
                    thing_dict["definition"] = thing.definition
                if thing.attributes and thing.attributes.additional_data:
                    thing_dict["attributes"] = thing.attributes.additional_data
                if thing.features and thing.features.additional_data:
                    thing_dict["features"] = thing.features.additional_data
                output_data.append(thing_dict)
            _output_json(output_data)

    asyncio.run(_run())


@thing_app.command()
def get(
    ctx: typer.Context,
    thing_id: Annotated[str, typer.Argument(help="The ID of the thing to retrieve")],
    revision: Annotated[Optional[int], typer.Option(help="Historical revision number to retrieve")] = None,
) -> None:
    """Get a specific thing by ID."""
    client = cast(DittoClient, ctx.obj)

    async def _run() -> None:
        # Build request configuration with custom headers if revision is specified
        request_config: RequestConfiguration[Any] | None = None
        if revision is not None:
            request_config = RequestConfiguration()
            request_config.headers.add("at-historical-revision", str(revision))

        response = await client.api.two.things.by_thing_id(thing_id).get(request_configuration=request_config)

        if not response:
            rprint(f"[red]Thing '{thing_id}' not found[/red]")
            return

        rprint(response)

    asyncio.run(_run())


@thing_app.command()
def update(
    ctx: typer.Context,
    thing_id: Annotated[str, typer.Argument(help="The ID of the thing to update")],
    patch_file: Annotated[Path, typer.Argument(help="Path to JSON patch file")],
) -> None:
    """Update a thing using JSON patch."""
    client = cast(DittoClient, ctx.obj)

    async def _run() -> None:
        # Read the patch data
        patch_data = json.loads(patch_file.read_text())

        # Create the patch thing
        patch_thing = PatchThing(additional_data=patch_data)

        await client.api.two.things.by_thing_id(thing_id).patch(body=patch_thing)
        rprint(f"[green]Successfully updated thing '{thing_id}'[/green]")

    asyncio.run(_run())


@thing_app.command()
def diff(
    ctx: typer.Context,
    thing_id: Annotated[str, typer.Argument(help="The ID of the thing to compare")],
    revision: Annotated[int, typer.Argument(help="Historical revision number to compare with current")],
) -> None:
    """Compare current thing state with a historical revision."""

    def extract_features_and_attributes(thing_data: Thing) -> dict[Any, Any]:
        """Extract features and attributes from thing response."""
        extracted = {}

        if hasattr(thing_data, "attributes") and thing_data.attributes:
            if hasattr(thing_data.attributes, "additional_data"):
                extracted["attributes"] = thing_data.attributes.additional_data

        if hasattr(thing_data, "features") and thing_data.features:
            if hasattr(thing_data.features, "additional_data"):
                extracted["features"] = thing_data.features.additional_data

        return extracted

    client = cast(DittoClient, ctx.obj)

    async def _run() -> None:
        # Get current thing
        current_response = await client.api.two.things.by_thing_id(thing_id).get()
        if not current_response:
            rprint(f"[red]Thing '{thing_id}' not found[/red]")
            return

        # Get historical revision
        request_config: RequestConfiguration[Any] = RequestConfiguration()
        request_config.headers.add("at-historical-revision", str(revision))

        historical_response = await client.api.two.things.by_thing_id(thing_id).get(
            request_configuration=request_config
        )
        if not historical_response:
            rprint(f"[red]Thing '{thing_id}' revision {revision} not found[/red]")
            return

        # Extract features and attributes
        current_data = extract_features_and_attributes(current_response)
        historical_data = extract_features_and_attributes(historical_response)

        # Convert to JSON-serializable format to handle datetime objects
        current_json = json.loads(json.dumps(current_data, default=str))
        historical_json = json.loads(json.dumps(historical_data, default=str))

        # Generate JSON patch
        patch = jsonpatch.make_patch(historical_json, current_json)

        if not patch:
            rprint(f"[green]No differences found between current thing and revision {revision}[/green]")
        else:
            rprint(f"[cyan]Differences between revision {revision} and current state of '{thing_id}':[/cyan]")
            rprint(patch)

    asyncio.run(_run())


@thing_app.command()
def delete(
    ctx: typer.Context,
    thing_id: Annotated[str, typer.Argument(help="The ID of the thing to delete")],
    confirm: Annotated[bool, typer.Option(help="Skip confirmation prompt")] = False,
) -> None:
    """Delete a thing."""

    if not confirm:
        if not typer.confirm(f"Are you sure you want to delete thing '{thing_id}'?"):
            rprint("[yellow]Operation cancelled[/yellow]")
            return

    client = cast(DittoClient, ctx.obj)

    async def _run() -> None:
        await client.api.two.things.by_thing_id(thing_id).delete()
        rprint(f"[green]Successfully deleted thing '{thing_id}'[/green]")

    asyncio.run(_run())
