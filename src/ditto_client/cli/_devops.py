from typer import Typer

from .devops._config import config_app
from .devops._connection import connection_app
from .devops._logging import logging_app

devops_app = Typer()
devops_app.add_typer(connection_app, name="connection", help="Manageconnections")
devops_app.add_typer(config_app, name="config", help="Manage configuration")
devops_app.add_typer(logging_app, name="logging", help="Manage logging")
