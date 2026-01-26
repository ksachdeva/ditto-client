import asyncio
import json
import logging
import os
from typing import Annotated, Any

import typer
from dotenv import load_dotenv
from kiota_http.httpx_request_adapter import HttpxRequestAdapter
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from typer import Typer

from ditto_client import __version__
from ditto_client._basic_auth import BasicAuthProvider
from ditto_client.cli._devops import devops_app
from ditto_client.cli._permission import permission_app
from ditto_client.cli._policy import policy_app
from ditto_client.cli._search import search_app
from ditto_client.cli._thing import thing_app
from ditto_client.generated.ditto_client import DittoClient

load_dotenv()
cli_app = Typer(name=f"Ditto Client [{__version__}]")
cli_app.add_typer(policy_app, name="policy", help="Policy management")
cli_app.add_typer(thing_app, name="thing", help="Thing management")
cli_app.add_typer(search_app, name="search", help="Thing search")
cli_app.add_typer(permission_app, name="permission", help="Permission check")
cli_app.add_typer(devops_app, name="devops", help="DevOps")


LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def _create_client(user_name: str, password: str) -> DittoClient:
    base_url = os.getenv("DITTO_BASE_URL", "http://host.docker.internal:8080")

    auth_provider = BasicAuthProvider(user_name=user_name, password=password)
    request_adapter = HttpxRequestAdapter(auth_provider)
    request_adapter.base_url = base_url

    return DittoClient(request_adapter)


def _create_ba_devops_client() -> DittoClient:
    user_name = os.getenv("DITTO_DEVOPS_USERNAME")
    password = os.getenv("DITTO_DEVOPS_PASSWORD")

    if not user_name or not password:
        raise ValueError("Environment variables DITTO_DEVOPS_USERNAME and DITTO_DEVOPS_PASSWORD must be set.")

    return _create_client(user_name, password)


def _create_ba_ditto_client() -> DittoClient:
    user_name = os.getenv("DITTO_USERNAME")
    password = os.getenv("DITTO_PASSWORD")

    if not user_name or not password:
        raise ValueError("Environment variables DITTO_USERNAME and DITTO_PASSWORD must be set.")

    return _create_client(user_name, password)


def _output_json(data: Any) -> None:
    """Output data as JSON."""
    json_str = json.dumps(data, indent=2, default=str)
    print(json_str)


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


@cli_app.command()
def whoami(
    ctx: typer.Context,
) -> None:
    """Get current user information."""

    client = _create_ba_ditto_client()
    use_table = _get_table_flag(ctx)

    async def _run() -> None:
        response = await client.api.two.whoami.get()

        if not response:
            rprint("[red]Failed to get user information[/red]")
            return

        if use_table:
            table = Table(title="Current User Information")
            table.add_column("Property", justify="right", style="cyan", no_wrap=True)
            table.add_column("Value", justify="left", style="green")

            table.add_row("Default Subject", response.default_subject or "N/A")
            table.add_row("Subjects", ", ".join(response.subjects) if response.subjects else "None")

            console = Console()
            console.print(table)
        else:
            output_data = {
                "default_subject": response.default_subject,
                "subjects": response.subjects or [],
            }
            _output_json(output_data)

    asyncio.run(_run())


@cli_app.callback()
def main(
    ctx: typer.Context,
    loglevel: Annotated[
        str,
        typer.Option(
            "--loglevel",
            "-l",
            help="Set the logging level (debug, info, warning, error, critical)",
        ),
    ] = "warning",
    table: Annotated[
        bool,
        typer.Option(
            "--table",
            help="Output results as a rich table instead of JSON",
        ),
    ] = False,
) -> None:
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("ditto_client").setLevel(LOG_LEVELS.get(loglevel, logging.WARNING))
    if not hasattr(ctx, "meta") or ctx.meta is None:
        ctx.meta = {}
    ctx.meta["table"] = table

    # create Ditto Clients based on the command types
    if ctx.invoked_subcommand == "devops":
        ctx.obj = _create_ba_devops_client()
    else:
        ctx.obj = _create_ba_ditto_client()
