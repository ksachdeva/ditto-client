import asyncio
import json
from typing import Annotated, Any, Optional, cast

import typer
from kiota_abstractions.base_request_configuration import RequestConfiguration
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from typer import Typer

from ditto_client.generated.api.two.search.things.count.count_request_builder import CountRequestBuilder
from ditto_client.generated.api.two.search.things.things_request_builder import ThingsRequestBuilder
from ditto_client.generated.ditto_client import DittoClient

search_app = Typer()


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


@search_app.command()
def query(
    ctx: typer.Context,
    filter: Annotated[
        Optional[str], typer.Option(help="RQL filter expression (e.g., 'eq(attributes/location,\"kitchen\")')")
    ] = None,
    fields: Annotated[Optional[str], typer.Option(help="Comma-separated list of fields to include")] = None,
    namespaces: Annotated[Optional[str], typer.Option(help="Comma-separated list of namespaces to search")] = None,
    option: Annotated[Optional[str], typer.Option(help="Search options (e.g., 'size(10),sort(+thingId)')")] = None,
    timeout: Annotated[Optional[str], typer.Option(help="Request timeout (e.g., '30s', '1m')")] = None,
) -> None:
    """Search for things in Ditto."""
    client = cast(DittoClient, ctx.obj)

    async def _run() -> None:
        # Build query parameters if provided
        request_config = None
        if filter or fields or namespaces or option or timeout:
            query_params = ThingsRequestBuilder.ThingsRequestBuilderGetQueryParameters()
            if filter:
                query_params.filter = filter
            if fields:
                query_params.fields = fields
            if namespaces:
                query_params.namespaces = namespaces
            if option:
                query_params.option = option
            if timeout:
                query_params.timeout = timeout

            request_config = RequestConfiguration(query_parameters=query_params)

        response = await client.api.two.search.things.get(request_configuration=request_config)

        if not response or not response.items:
            if use_table:
                rprint("[yellow]No things found[/yellow]")
            else:
                _output_json([])
            return

        if use_table:
            # Create a table for better display
            table = Table(title="Ditto Things")
            table.add_column("Thing ID", justify="left", style="cyan", no_wrap=True)
            table.add_column("Features", justify="center", style="yellow")

            for thing in response.items:
                # Features is a Features object, not a dict, so we need to check if it has any data
                features_count = (
                    len(thing.features.additional_data) if thing.features and thing.features.additional_data else 0
                )
                table.add_row(thing.thing_id, str(features_count))

            console = Console()
            console.print(table)
        else:
            output_data = []
            for thing in response.items:
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


@search_app.command()
def count(
    ctx: typer.Context,
    filter: Annotated[
        Optional[str], typer.Option(help="RQL filter expression (e.g., 'eq(attributes/location,\"kitchen\")')")
    ] = None,
    namespaces: Annotated[Optional[str], typer.Option(help="Comma-separated list of namespaces to search")] = None,
) -> None:
    """List things from Ditto."""
    client = cast(DittoClient, ctx.obj)

    async def _run() -> None:
        # Build query parameters if provided
        request_config = None
        if filter or namespaces:
            query_params = CountRequestBuilder.CountRequestBuilderGetQueryParameters()
            if filter:
                query_params.filter = filter
            if namespaces:
                query_params.namespaces = namespaces

            request_config = RequestConfiguration(query_parameters=query_params)

        response = await client.api.two.search.things.count.get(request_configuration=request_config)
        _output_json({"count": response})

    asyncio.run(_run())
