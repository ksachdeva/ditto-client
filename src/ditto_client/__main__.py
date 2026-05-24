import asyncio
import logging
from enum import StrEnum
from typing import Annotated, cast

import typer
from dotenv import load_dotenv
from kiota_http.httpx_request_adapter import HttpxRequestAdapter
from typer import Context, Typer

from ditto_client import __version__
from ditto_client._basic_auth import BasicAuthProvider
from ditto_client._jwt import JWTAuthProvider
from ditto_client._pre_auth import PreAuthProvider
from ditto_client._types import CmdState
from ditto_client.cli._devops import devops_app
from ditto_client.cli._output import output_json, output_message, output_table
from ditto_client.cli._permission import permission_app
from ditto_client.cli._policy import policy_app
from ditto_client.cli._search import search_app
from ditto_client.cli._thing import thing_app
from ditto_client.generated.ditto_client import DittoClient

load_dotenv()  # Load environment variables from .env file if it exists

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


class DittoAuthType(StrEnum):
    """Authentication types supported by Ditto client."""

    BASIC = "basic"
    PRE_AUTH = "pre-auth"
    JWT = "jwt"


def _create_jwt_client(base_url: str, jwt_token: str) -> DittoClient:
    auth_provider = JWTAuthProvider(token=jwt_token)
    request_adapter = HttpxRequestAdapter(auth_provider)
    request_adapter.base_url = base_url

    return DittoClient(request_adapter)


def _create_ba_client(base_url: str, user_name: str, password: str) -> DittoClient:
    auth_provider = BasicAuthProvider(user_name=user_name, password=password)
    request_adapter = HttpxRequestAdapter(auth_provider)
    request_adapter.base_url = base_url

    return DittoClient(request_adapter)


def _create_pre_auth_client(base_url: str, auth_subject: str) -> DittoClient:
    auth_provider = PreAuthProvider(auth_subject=auth_subject)
    request_adapter = HttpxRequestAdapter(auth_provider)
    request_adapter.base_url = base_url

    return DittoClient(request_adapter)


@cli_app.command()
def whoami(
    ctx: Context,
) -> None:
    """Get current user information."""
    state = cast(CmdState, ctx.obj)
    use_table = state.table

    async def _run() -> None:
        response = await state.client.api.two.whoami.get()

        if not response:
            output_message("Failed to get user information", level="error")
            return

        if use_table:
            output_table(
                title="Current User Information",
                columns=[
                    ("Property", "right", "cyan"),
                    ("Value", "left", "green"),
                ],
                rows=[
                    ["Default Subject", response.default_subject or "N/A"],
                    ["Subjects", ", ".join(response.subjects) if response.subjects else "None"],
                ],
            )
        else:
            output_json(
                {
                    "default_subject": response.default_subject,
                    "subjects": response.subjects or [],
                },
            )

    asyncio.run(_run())


@cli_app.callback()
def main(
    ctx: Context,
    loglevel: Annotated[
        str,
        typer.Option(
            "--loglevel",
            "-l",
            help="Set the logging level (debug, info, warning, error, critical)",
        ),
    ] = "warning",
    base_url: Annotated[
        str,
        typer.Option(
            "--base-url",
            help="Base URL for the Ditto API (can also be set via DITTO_BASE_URL environment variable)",
            envvar="DITTO_BASE_URL",
        ),
    ] = "http://host.docker.internal:8080",
    auth_type: Annotated[
        DittoAuthType,
        typer.Option(
            "--auth-type",
            help="Set the authentication type (basic, pre-auth)",
        ),
    ] = DittoAuthType.BASIC,
    username: Annotated[
        str | None,
        typer.Option(
            "--username",
            help="Username for basic authentication (can also be set via DITTO_USERNAME environment variable)",
            envvar="DITTO_USERNAME",
        ),
    ] = None,
    password: Annotated[
        str | None,
        typer.Option(
            "--password",
            help="Password for basic authentication (can also be set via DITTO_PASSWORD environment variable)",
            envvar="DITTO_PASSWORD",
        ),
    ] = None,
    preauth_subject: Annotated[
        str | None,
        typer.Option(
            "--preauth-subject",
            help="Auth subject for pre-authentication (can also be set via DITTO_PREAUTH_SUBJECT environment variable)",
            envvar="DITTO_PREAUTH_SUBJECT",
        ),
    ] = None,
    jwt_token: Annotated[
        str | None,
        typer.Option(
            "--jwt-token",
            help="JWT token for authentication (can also be set via DITTO_JWT_TOKEN environment variable)",
            envvar="DITTO_JWT_TOKEN",
        ),
    ] = None,
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

    ctx.ensure_object(CmdState)
    ctx.obj = CmdState()
    ctx.obj.table = table

    if auth_type == DittoAuthType.JWT:
        if not jwt_token:
            output_message("JWT token is required for JWT authentication", level="error")
            raise typer.Exit(code=1)
        ctx.obj.client = _create_jwt_client(base_url, jwt_token)
    elif auth_type == DittoAuthType.PRE_AUTH:
        if not preauth_subject:
            output_message("Auth subject is required for pre-authentication", level="error")
            raise typer.Exit(code=1)
        ctx.obj.client = _create_pre_auth_client(base_url, preauth_subject)
    else:
        if not username or not password:
            output_message("Username and password are required for basic authentication", level="error")
            raise typer.Exit(code=1)
        ctx.obj.client = _create_ba_client(base_url, username, password)
