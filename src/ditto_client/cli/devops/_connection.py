import asyncio
import json
from pathlib import Path
from typing import Annotated, Any

import typer
from kiota_abstractions.base_request_configuration import RequestConfiguration
from typer import Context, Typer

from ditto_client.cli._output import (
    output_json,
    output_message,
    output_table,
)
from ditto_client.generated.api.two.connections.connections_request_builder import ConnectionsRequestBuilder
from ditto_client.generated.api.two.connections.item.with_connection_item_request_builder import (
    WithConnectionItemRequestBuilder,
)
from ditto_client.generated.models.new_connection import NewConnection

connection_app = Typer()


def _connection_to_dict(connection: Any) -> dict[str, Any]:
    """Convert a Connection object to a dictionary."""
    connection_dict: dict[str, Any] = {}
    if connection.id:
        connection_dict["id"] = connection.id
    if connection.connection_status:
        connection_dict["connectionStatus"] = connection.connection_status
    if connection.connection_type:
        connection_dict["connectionType"] = connection.connection_type
    if connection.uri:
        connection_dict["uri"] = connection.uri
    if hasattr(connection, "additional_data") and connection.additional_data:
        connection_dict.update(connection.additional_data)
    return connection_dict


@connection_app.command()
def create(
    ctx: Context,
    connection_id: Annotated[str, typer.Argument(help="The ID of the connection to create")],
    connection_file: Annotated[Path, typer.Argument(help="Path to connection definition")],
) -> None:
    """Create a new connection."""
    state = ctx.obj

    async def _run() -> None:
        # Read the connection data
        connection_data = json.loads(connection_file.read_text())

        # Create the new connection
        new_connection = NewConnection(additional_data=connection_data)

        await state.client.api.two.connections.by_connection_id(connection_id).put(body=new_connection)
        output_message(f"Successfully created connection '{connection_id}'", level="success")

    asyncio.run(_run())


@connection_app.command()
def list(
    ctx: Context,
    fields: Annotated[
        str | None,
        typer.Option(help="Comma-separated list of fields to include (e.g., 'id,connectionStatus,uri')"),
    ] = None,
) -> None:
    """List connections from Ditto."""
    state = ctx.obj
    use_table = state.table

    async def _run() -> None:
        # Build query parameters if provided
        request_config = None
        if fields:
            query_params = ConnectionsRequestBuilder.ConnectionsRequestBuilderGetQueryParameters()
            if fields:
                query_params.fields = fields

            request_config = RequestConfiguration(query_parameters=query_params)

        response = await state.client.api.two.connections.get(request_configuration=request_config)

        if not response:
            if use_table:
                output_message("No connections found", level="warning")
            else:
                output_json([])
            return

        if use_table:
            rows = []
            for connection in response:
                rows.append(
                    [
                        connection.id or "",
                        connection.connection_status or "",
                        connection.connection_type or "",
                        connection.uri or "N/A",
                    ],
                )

            output_table(
                title="Ditto Connections",
                columns=[
                    ("Connection ID", "left", "cyan"),
                    ("Status", "center", "green"),
                    ("Type", "center", "yellow"),
                    ("URI", "left", "blue"),
                ],
                rows=rows,
            )
        else:
            output_json([_connection_to_dict(connection) for connection in response])

    asyncio.run(_run())


@connection_app.command()
def get(
    ctx: Context,
    connection_id: Annotated[str, typer.Argument(help="The ID of the connection to retrieve")],
    fields: Annotated[str | None, typer.Option(help="Comma-separated list of fields to include")] = None,
) -> None:
    """Get a specific connection by ID."""
    state = ctx.obj

    async def _run() -> None:
        # Build query parameters if provided
        request_config = None
        if fields:
            query_params = WithConnectionItemRequestBuilder.WithConnectionItemRequestBuilderGetQueryParameters()
            query_params.fields = fields
            request_config = RequestConfiguration(query_parameters=query_params)

        response = await state.client.api.two.connections.by_connection_id(connection_id).get(
            request_configuration=request_config,
        )

        if not response:
            output_message(f"Connection '{connection_id}' not found", level="error")
            return

        output_json(_connection_to_dict(response))

    asyncio.run(_run())


@connection_app.command()
def delete(
    ctx: Context,
    connection_id: Annotated[str, typer.Argument(help="The ID of the connection to delete")],
    confirm: Annotated[bool, typer.Option(help="Skip confirmation prompt")] = False,
) -> None:
    """Delete a connection."""
    if not confirm:
        if not typer.confirm(f"Are you sure you want to delete connection '{connection_id}'?"):
            output_message("Operation cancelled", level="warning")
            return

    state = ctx.obj

    async def _run() -> None:
        await state.client.api.two.connections.by_connection_id(connection_id).delete()
        output_message(f"Successfully deleted connection '{connection_id}'", level="success")

    asyncio.run(_run())
