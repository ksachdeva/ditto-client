import asyncio
import logging
import os
from typing import Annotated, cast

import typer
from dotenv import load_dotenv
from kiota_http.httpx_request_adapter import HttpxRequestAdapter
from typer import Context, Typer

from ditto_client import __version__
from ditto_client._basic_auth import BasicAuthProvider
from ditto_client._jwt import JWTAuthProvider
from ditto_client._pre_auth import PreAuthProvider
from ditto_client._types import CmdState, DittoAuthType
from ditto_client.cli._devops import devops_app
from ditto_client.cli._output import output_json, output_message, output_table
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


def _create_jwt_client(jwt_token: str) -> DittoClient:
    base_url = os.getenv("DITTO_BASE_URL", "http://host.docker.internal:8080")

    auth_provider = JWTAuthProvider(token=jwt_token)
    request_adapter = HttpxRequestAdapter(auth_provider)
    request_adapter.base_url = base_url

    return DittoClient(request_adapter)


def _create_ba_client(user_name: str, password: str) -> DittoClient:
    base_url = os.getenv("DITTO_BASE_URL", "http://host.docker.internal:8080")

    auth_provider = BasicAuthProvider(user_name=user_name, password=password)
    request_adapter = HttpxRequestAdapter(auth_provider)
    request_adapter.base_url = base_url

    return DittoClient(request_adapter)


def _create_pre_auth_client(auth_subject: str) -> DittoClient:
    base_url = os.getenv("DITTO_BASE_URL", "http://host.docker.internal:8080")

    auth_provider = PreAuthProvider(auth_subject=auth_subject)
    request_adapter = HttpxRequestAdapter(auth_provider)
    request_adapter.base_url = base_url

    return DittoClient(request_adapter)


def _create_devops_client(auth_type: DittoAuthType) -> DittoClient:
    if auth_type == DittoAuthType.BASIC:
        user_name = os.getenv("DITTO_DEVOPS_USERNAME")
        password = os.getenv("DITTO_DEVOPS_PASSWORD")

        if not user_name or not password:
            raise ValueError("Environment variables DITTO_DEVOPS_USERNAME and DITTO_DEVOPS_PASSWORD must be set.")

        return _create_ba_client(user_name, password)

    elif auth_type == DittoAuthType.PRE_AUTH:
        auth_subject = os.getenv("DITTO_DEVOPS_AUTH_SUBJECT")

        if not auth_subject:
            raise ValueError("Environment variable DITTO_DEVOPS_AUTH_SUBJECT must be set.")

        return _create_pre_auth_client(auth_subject)

    elif auth_type == DittoAuthType.JWT:
        jwt_token = os.getenv("DITTO_DEVOPS_JWT_TOKEN")

        if not jwt_token:
            raise ValueError("Environment variable DITTO_DEVOPS_JWT_TOKEN must be set.")

        return _create_jwt_client(jwt_token)


def _create_ditto_client(auth_type: DittoAuthType) -> DittoClient:
    if auth_type == DittoAuthType.BASIC:
        user_name = os.getenv("DITTO_USERNAME")
        password = os.getenv("DITTO_PASSWORD")

        if not user_name or not password:
            raise ValueError("Environment variables DITTO_USERNAME and DITTO_PASSWORD must be set.")

        return _create_ba_client(user_name, password)

    elif auth_type == DittoAuthType.PRE_AUTH:
        auth_subject = os.getenv("DITTO_AUTH_SUBJECT")

        if not auth_subject:
            raise ValueError("Environment variable DITTO_AUTH_SUBJECT must be set.")

        return _create_pre_auth_client(auth_subject)

    elif auth_type == DittoAuthType.JWT:
        jwt_token = os.getenv("DITTO_JWT_TOKEN")

        if not jwt_token:
            raise ValueError("Environment variable DITTO_JWT_TOKEN must be set.")

        return _create_jwt_client(jwt_token)


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
    auth_type: Annotated[
        DittoAuthType,
        typer.Option(
            "--auth-type",
            help="Set the authentication type (basic, pre-auth)",
        ),
    ] = DittoAuthType.BASIC,
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
    ctx.obj._auth_type = auth_type
    # create Ditto Clients based on the command types
    if ctx.invoked_subcommand == "devops":
        ctx.obj.client = _create_devops_client(auth_type)
    else:
        ctx.obj.client = _create_ditto_client(auth_type)
