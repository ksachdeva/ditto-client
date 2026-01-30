import asyncio
from typing import Annotated, cast

import typer
from kiota_abstractions.base_request_configuration import RequestConfiguration
from typer import Context, Typer

from ditto_client._types import CmdState
from ditto_client.cli._output import model_to_dict, output_json
from ditto_client.generated.api.two.search.things.count.count_request_builder import CountRequestBuilder
from ditto_client.generated.api.two.search.things.things_request_builder import ThingsRequestBuilder

search_app = Typer()


@search_app.command()
def query(
    ctx: Context,
    filter: Annotated[
        str | None,
        typer.Option(help="RQL filter expression (e.g., 'eq(attributes/location,\"kitchen\")')"),
    ] = None,
    fields: Annotated[str | None, typer.Option(help="Comma-separated list of fields to include")] = None,
    namespaces: Annotated[str | None, typer.Option(help="Comma-separated list of namespaces to search")] = None,
    option: Annotated[str | None, typer.Option(help="Search options (e.g., 'size(10),sort(+thingId)')")] = None,
    timeout: Annotated[str | None, typer.Option(help="Request timeout (e.g., '30s', '1m')")] = None,
) -> None:
    """Search for things in Ditto."""
    state = cast(CmdState, ctx.obj)

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

        response = await state.client.api.two.search.things.get(request_configuration=request_config)

        if not response or not response.items:
            output_json([])
            return

        output_json([model_to_dict(thing) for thing in response.items])

    asyncio.run(_run())


@search_app.command()
def count(
    ctx: Context,
    filter: Annotated[
        str | None,
        typer.Option(help="RQL filter expression (e.g., 'eq(attributes/location,\"kitchen\")')"),
    ] = None,
    namespaces: Annotated[str | None, typer.Option(help="Comma-separated list of namespaces to search")] = None,
) -> None:
    """Count things in Ditto."""
    state = cast(CmdState, ctx.obj)

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

        response = await state.client.api.two.search.things.count.get(request_configuration=request_config)
        output_json({"count": response})

    asyncio.run(_run())
