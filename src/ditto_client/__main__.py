import logging
from typing import Annotated

import typer
from dotenv import load_dotenv
from typer import Typer

from ditto_client import __version__
from ditto_client.cli._config import config_app
from ditto_client.cli._connection import connection_app
from ditto_client.cli._devops import devops_app
from ditto_client.cli._logging import logging_app
from ditto_client.cli._permission import permission_app
from ditto_client.cli._policy import policy_app
from ditto_client.cli._search import search_app
from ditto_client.cli._thing import thing_app

load_dotenv()
cli_app = Typer(name=f"Ditto Client [{__version__}]")
cli_app.add_typer(policy_app, name="policy", help="Policy management")
cli_app.add_typer(thing_app, name="thing", help="Thing management")
cli_app.add_typer(search_app, name="search", help="Thing search")
cli_app.add_typer(connection_app, name="connection", help="Connection management")
cli_app.add_typer(devops_app, name="devops", help="DevOps")
cli_app.add_typer(permission_app, name="permission", help="Permission check")
cli_app.add_typer(config_app, name="config", help="Configuration management")
cli_app.add_typer(logging_app, name="logging", help="Logging configuration management")

LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


@cli_app.callback()
def main(
    loglevel: Annotated[
        str,
        typer.Option(
            "--loglevel",
            "-l",
            help="Set the logging level (debug, info, warning, error, critical)",
        ),
    ] = "warning",
) -> None:
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("ditto_client").setLevel(LOG_LEVELS.get(loglevel, logging.WARNING))
