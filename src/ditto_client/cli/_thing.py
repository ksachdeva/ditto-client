import asyncio
import json
from pathlib import Path
from typing import Annotated, Any

import jsonpatch
import typer
from kiota_abstractions.base_request_configuration import RequestConfiguration
from typer import Context, Typer

from ditto_client.cli._output import (
    model_to_dict,
    output_json,
    output_message,
    output_table,
)
from ditto_client.generated.api.two.things.things_request_builder import ThingsRequestBuilder
from ditto_client.generated.models.new_thing import NewThing
from ditto_client.generated.models.patch_thing import PatchThing
from ditto_client.generated.models.thing import Thing

thing_app = Typer()


@thing_app.command()
def create(
    ctx: Context,
    thing_id: Annotated[str, typer.Argument(help="The ID of the thing to create")],
    data_file: Annotated[Path, typer.Argument(help="Path to JSON file containing thing additional data")],
) -> None:
    """Create a new thing."""
    state = ctx.obj

    async def _run() -> None:
        # Build the thing data
        thing_data = json.loads(data_file.read_text())

        # Create the new thing
        new_thing = NewThing(additional_data=thing_data)

        await state.client.api.two.things.by_thing_id(thing_id).put(body=new_thing)
        output_message(f"Successfully created thing '{thing_id}'", level="success")

    asyncio.run(_run())


@thing_app.command()
def list(
    ctx: Context,
    fields: Annotated[
        str | None,
        typer.Option(
            "--fields",
            "-f",
            help="Comma-separated list of fields to include (e.g., 'thingId,attributes,features')",
        ),
    ] = None,
    ids: Annotated[str | None, typer.Option(help="Comma-separated list of thing IDs to retrieve")] = None,
    timeout: Annotated[str | None, typer.Option(help="Request timeout (e.g., '30s', '1m')")] = None,
) -> None:
    """List things from Ditto."""
    state = ctx.obj
    use_table = state.table

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

        response = await state.client.api.two.things.get(request_configuration=request_config)

        if not response:
            if use_table:
                output_message("No things found", level="warning")
            else:
                output_json([])
            return

        if use_table:
            rows = []
            for thing in response:
                features_count = (
                    len(thing.features.additional_data) if thing.features and thing.features.additional_data else 0
                )
                rows.append([thing.thing_id or "", str(features_count)])

            output_table(
                title="Ditto Things",
                columns=[
                    ("Thing ID", "left", "cyan"),
                    ("Features", "center", "yellow"),
                ],
                rows=rows,
            )
        else:
            output_json([model_to_dict(thing) for thing in response])

    asyncio.run(_run())


@thing_app.command()
def get(
    ctx: Context,
    thing_id: Annotated[str, typer.Argument(help="The ID of the thing to retrieve")],
    revision: Annotated[int | None, typer.Option(help="Historical revision number to retrieve")] = None,
) -> None:
    """Get a specific thing by ID."""
    state = ctx.obj

    async def _run() -> None:
        # Build request configuration with custom headers if revision is specified
        request_config: RequestConfiguration[Any] | None = None
        if revision is not None:
            request_config = RequestConfiguration()
            request_config.headers.add("at-historical-revision", str(revision))

        response = await state.client.api.two.things.by_thing_id(thing_id).get(request_configuration=request_config)

        if not response:
            output_message(f"Thing '{thing_id}' not found", level="error")
            return

        output_json(model_to_dict(response))

    asyncio.run(_run())


@thing_app.command()
def update(
    ctx: Context,
    thing_id: Annotated[str, typer.Argument(help="The ID of the thing to update")],
    patch_file: Annotated[Path, typer.Argument(help="Path to JSON patch file")],
) -> None:
    """Update a thing using JSON patch."""
    state = ctx.obj

    async def _run() -> None:
        # Read the patch data
        patch_data = json.loads(patch_file.read_text())

        # Create the patch thing
        patch_thing = PatchThing(additional_data=patch_data)

        await state.client.api.two.things.by_thing_id(thing_id).patch(body=patch_thing)
        output_message(f"Successfully updated thing '{thing_id}'", level="success")

    asyncio.run(_run())


@thing_app.command()
def diff(
    ctx: Context,
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

    state = ctx.obj

    async def _run() -> None:
        # Get current thing
        current_response = await state.client.api.two.things.by_thing_id(thing_id).get()
        if not current_response:
            output_message(f"Thing '{thing_id}' not found", level="error")
            return

        # Get historical revision
        request_config: RequestConfiguration[Any] = RequestConfiguration()
        request_config.headers.add("at-historical-revision", str(revision))

        historical_response = await state.client.api.two.things.by_thing_id(thing_id).get(
            request_configuration=request_config,
        )
        if not historical_response:
            output_message(f"Thing '{thing_id}' revision {revision} not found", level="error")
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
            output_json({"diff": [], "message": f"No differences found between current thing and revision {revision}"})
        else:
            output_json({"diff": list(patch)})

    asyncio.run(_run())


@thing_app.command()
def delete(
    ctx: Context,
    thing_id: Annotated[str, typer.Argument(help="The ID of the thing to delete")],
    confirm: Annotated[bool, typer.Option(help="Skip confirmation prompt")] = False,
) -> None:
    """Delete a thing."""
    if not confirm:
        if not typer.confirm(f"Are you sure you want to delete thing '{thing_id}'?"):
            output_message("Operation cancelled", level="warning")
            return

    state = ctx.obj

    async def _run() -> None:
        await state.client.api.two.things.by_thing_id(thing_id).delete()
        output_message(f"Successfully deleted thing '{thing_id}'", level="success")

    asyncio.run(_run())
