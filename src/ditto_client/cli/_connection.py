import asyncio
import json
from pathlib import Path
from typing import Annotated, Optional

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
from ditto_client.generated.models.new_connection import NewConnection

from ._utils import create_devops_client

connection_app = Typer()


@connection_app.command()
def create(
    connection_id: Annotated[str, typer.Argument(help="The ID of the connection to create")],
    connection_file: Annotated[Path, typer.Argument(help="Path to connection definition")],
) -> None:
    """Create a new connection."""

    async def _run() -> None:
        client = create_devops_client()

        # Read the connection data
        connection_data = json.loads(connection_file.read_text())

        # Create the new connection
        new_connection = NewConnection(additional_data=connection_data)

        await client.api.two.connections.by_connection_id(connection_id).put(body=new_connection)

    asyncio.run(_run())


@connection_app.command()
def list(
    fields: Annotated[
        Optional[str],
        typer.Option(help="Comma-separated list of fields to include (e.g., 'id,connectionStatus,uri')"),
    ] = None,
) -> None:
    """List connections from Ditto."""

    async def _run() -> None:
        client = create_devops_client()

        # Build query parameters if provided
        request_config = None
        if fields:
            query_params = ConnectionsRequestBuilder.ConnectionsRequestBuilderGetQueryParameters()
            if fields:
                query_params.fields = fields

            request_config = RequestConfiguration(query_parameters=query_params)

        response = await client.api.two.connections.get(request_configuration=request_config)

        if not response:
            rprint("[yellow]No connections found[/yellow]")
            return

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

    asyncio.run(_run())


@connection_app.command()
def get(
    connection_id: Annotated[str, typer.Argument(help="The ID of the connection to retrieve")],
    fields: Annotated[Optional[str], typer.Option(help="Comma-separated list of fields to include")] = None,
) -> None:
    """Get a specific connection by ID."""

    async def _run() -> None:
        client = create_devops_client()

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
            rprint(f"[red]Thing '{connection_id}' not found[/red]")
            return

        rprint(response)

    asyncio.run(_run())


@connection_app.command()
def delete(
    connection_id: Annotated[str, typer.Argument(help="The ID of the connection to delete")],
    confirm: Annotated[bool, typer.Option(help="Skip confirmation prompt")] = False,
) -> None:
    """Delete a connection."""

    if not confirm:
        if not typer.confirm(f"Are you sure you want to delete connection '{connection_id}'?"):
            rprint("[yellow]Operation cancelled[/yellow]")
            return

    async def _run() -> None:
        client = create_devops_client()

        await client.api.two.connections.by_connection_id(connection_id).delete()
        rprint(f"[green]Successfully deleted connection '{connection_id}'[/green]")

    asyncio.run(_run())
