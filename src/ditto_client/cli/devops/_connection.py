import asyncio
import json
from pathlib import Path
from typing import Annotated, Any, Optional, cast

import typer
from kiota_abstractions.base_request_configuration import RequestConfiguration
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from typer import Typer

from ditto_client.generated.api.two.connections.connections_request_builder import ConnectionsRequestBuilder
from ditto_client.generated.api.two.connections.item.with_connection_item_request_builder import (
    WithConnectionItemRequestBuilder,
)
from ditto_client.generated.ditto_client import DittoClient
from ditto_client.generated.models.new_connection import NewConnection

connection_app = Typer()


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


@connection_app.command()
def create(
    ctx: typer.Context,
    connection_id: Annotated[str, typer.Argument(help="The ID of the connection to create")],
    connection_file: Annotated[Path, typer.Argument(help="Path to connection definition")],
) -> None:
    """Create a new connection."""

    client = cast(DittoClient, ctx.obj)

    async def _run() -> None:
        # Read the connection data
        connection_data = json.loads(connection_file.read_text())

        # Create the new connection
        new_connection = NewConnection(additional_data=connection_data)

        await client.api.two.connections.by_connection_id(connection_id).put(body=new_connection)

    asyncio.run(_run())


@connection_app.command()
def list(
    ctx: typer.Context,
    fields: Annotated[
        Optional[str],
        typer.Option(help="Comma-separated list of fields to include (e.g., 'id,connectionStatus,uri')"),
    ] = None,
) -> None:
    """List connections from Ditto."""

    client = cast(DittoClient, ctx.obj)
    use_table = _get_table_flag(ctx)

    async def _run() -> None:
        # Build query parameters if provided
        request_config = None
        if fields:
            query_params = ConnectionsRequestBuilder.ConnectionsRequestBuilderGetQueryParameters()
            if fields:
                query_params.fields = fields

            request_config = RequestConfiguration(query_parameters=query_params)

        response = await client.api.two.connections.get(request_configuration=request_config)

        if not response:
            if use_table:
                rprint("[yellow]No connections found[/yellow]")
            else:
                _output_json([])
            return

        if use_table:
            # Create a table for better display
            table = Table(title="Ditto Connections")
            table.add_column("Connection ID", justify="left", style="cyan", no_wrap=True)
            table.add_column("Status", justify="center", style="green")
            table.add_column("Type", justify="center", style="yellow")
            table.add_column("URI", justify="left", style="blue")

            for connection in response:
                connection_id = connection.id
                connection_status = connection.connection_status
                connection_type = connection.connection_type
                connection_uri = connection.uri if connection.uri else "N/A"

                table.add_row(
                    connection_id, connection_status, connection_type, connection_uri if connection_uri else "N/A"
                )

            console = Console()
            console.print(table)
        else:
            output_data = []
            for connection in response:
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
                output_data.append(connection_dict)
            _output_json(output_data)

    asyncio.run(_run())


@connection_app.command()
def get(
    ctx: typer.Context,
    connection_id: Annotated[str, typer.Argument(help="The ID of the connection to retrieve")],
    fields: Annotated[Optional[str], typer.Option(help="Comma-separated list of fields to include")] = None,
) -> None:
    """Get a specific connection by ID."""

    client = cast(DittoClient, ctx.obj)

    async def _run() -> None:
        # Build query parameters if provided
        request_config = None
        if fields:
            query_params = WithConnectionItemRequestBuilder.WithConnectionItemRequestBuilderGetQueryParameters()
            query_params.fields = fields
            request_config = RequestConfiguration(query_parameters=query_params)

        response = await client.api.two.connections.by_connection_id(connection_id).get(
            request_configuration=request_config
        )

        if not response:
            rprint(f"[red]Connection '{connection_id}' not found[/red]")
            return

        connection_dict: dict[str, Any] = {}
        if response.id:
            connection_dict["id"] = response.id
        if response.connection_status:
            connection_dict["connectionStatus"] = response.connection_status
        if response.connection_type:
            connection_dict["connectionType"] = response.connection_type
        if response.uri:
            connection_dict["uri"] = response.uri
        if hasattr(response, "additional_data") and response.additional_data:
            connection_dict.update(response.additional_data)
        _output_json(connection_dict)

    asyncio.run(_run())


@connection_app.command()
def delete(
    ctx: typer.Context,
    connection_id: Annotated[str, typer.Argument(help="The ID of the connection to delete")],
    confirm: Annotated[bool, typer.Option(help="Skip confirmation prompt")] = False,
) -> None:
    """Delete a connection."""

    if not confirm:
        if not typer.confirm(f"Are you sure you want to delete connection '{connection_id}'?"):
            rprint("[yellow]Operation cancelled[/yellow]")
            return

    client = cast(DittoClient, ctx.obj)

    async def _run() -> None:
        await client.api.two.connections.by_connection_id(connection_id).delete()
        rprint(f"[green]Successfully deleted connection '{connection_id}'[/green]")

    asyncio.run(_run())
