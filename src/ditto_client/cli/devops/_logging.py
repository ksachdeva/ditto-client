import asyncio
import json
from pathlib import Path
from typing import Annotated, Any, Optional, cast

import typer
from kiota_abstractions.base_request_configuration import RequestConfiguration
from rich import print as rprint
from typer import Typer

from ditto_client.generated.devops.logging.logging_request_builder import LoggingRequestBuilder
from ditto_client.generated.ditto_client import DittoClient
from ditto_client.generated.models.logging_update_fields import LoggingUpdateFields
from ditto_client.generated.models.module import Module
from ditto_client.generated.models.module_updated_log_level import ModuleUpdatedLogLevel
from ditto_client.generated.models.result_update_request import ResultUpdateRequest
from ditto_client.generated.models.retrieve_logging_config import RetrieveLoggingConfig

logging_app = Typer()


def _output_json(data: Any) -> None:
    """Output data as JSON."""
    json_str = json.dumps(data, indent=2, default=str)
    print(json_str)


@logging_app.command()
def get(
    ctx: typer.Context,
    module_name: Annotated[Optional[str], typer.Option(help="Module name to get logging config for")] = None,
) -> None:
    """Get logging configuration from Ditto services."""

    client = cast(DittoClient, ctx.obj)

    async def _run() -> None:
        response: Module | RetrieveLoggingConfig | None

        if module_name:
            # Get module-specific logging config
            response = await client.devops.logging.by_module_name(module_name).get()
        else:
            # Get general logging config
            query_params = LoggingRequestBuilder.LoggingRequestBuilderGetQueryParameters()
            request_config = RequestConfiguration(query_parameters=query_params)
            response = await client.devops.logging.get(request_configuration=request_config)

        if not response:
            rprint("[yellow]No logging configuration found[/yellow]")
            return

        config_dict: dict[str, Any] = {}
        if hasattr(response, "additional_data") and response.additional_data:
            config_dict = response.additional_data
        _output_json(config_dict)

    asyncio.run(_run())


@logging_app.command()
def update(
    ctx: typer.Context,
    update_file: Annotated[Path, typer.Argument(help="Path to JSON file containing logging updates")],
    module_name: Annotated[Optional[str], typer.Option(help="Module name to update logging config for")] = None,
) -> None:
    """Update logging configuration for Ditto services."""
    client = cast(DittoClient, ctx.obj)

    async def _run() -> None:
        # Read the logging update data
        update_data = json.loads(update_file.read_text())

        # Create the logging update
        logging_update = LoggingUpdateFields(additional_data=update_data)

        response: ModuleUpdatedLogLevel | list[ResultUpdateRequest] | None

        if module_name:
            response = await client.devops.logging.by_module_name(module_name).put(body=logging_update)
        else:
            response = await client.devops.logging.put(body=logging_update)

        result_dict: dict[str, Any] = {}
        if hasattr(response, "additional_data") and response.additional_data:
            result_dict = response.additional_data
        _output_json(result_dict)

    asyncio.run(_run())
