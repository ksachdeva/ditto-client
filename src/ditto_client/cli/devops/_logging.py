import asyncio
import json
from pathlib import Path
from typing import Annotated

import typer
from kiota_abstractions.base_request_configuration import RequestConfiguration
from typer import Context, Typer

from ditto_client.cli._output import model_to_dict, output_json, output_message
from ditto_client.generated.devops.logging.logging_request_builder import LoggingRequestBuilder
from ditto_client.generated.models.logging_update_fields import LoggingUpdateFields
from ditto_client.generated.models.module import Module
from ditto_client.generated.models.module_updated_log_level import ModuleUpdatedLogLevel
from ditto_client.generated.models.result_update_request import ResultUpdateRequest
from ditto_client.generated.models.retrieve_logging_config import RetrieveLoggingConfig

logging_app = Typer()


@logging_app.command()
def get(
    ctx: Context,
    module_name: Annotated[str | None, typer.Option(help="Module name to get logging config for")] = None,
) -> None:
    """Get logging configuration from Ditto services."""
    state = ctx.obj

    async def _run() -> None:
        response: Module | RetrieveLoggingConfig | None

        if module_name:
            # Get module-specific logging config
            response = await state.client.devops.logging.by_module_name(module_name).get()
        else:
            # Get general logging config
            query_params = LoggingRequestBuilder.LoggingRequestBuilderGetQueryParameters()
            request_config = RequestConfiguration(query_parameters=query_params)
            response = await state.client.devops.logging.get(request_configuration=request_config)

        if not response:
            output_message("No logging configuration found", level="warning")
            return

        output_json(model_to_dict(response))

    asyncio.run(_run())


@logging_app.command()
def update(
    ctx: Context,
    update_file: Annotated[Path, typer.Argument(help="Path to JSON file containing logging updates")],
    module_name: Annotated[str | None, typer.Option(help="Module name to update logging config for")] = None,
) -> None:
    """Update logging configuration for Ditto services."""
    state = ctx.obj

    async def _run() -> None:
        # Read the logging update data
        update_data = json.loads(update_file.read_text())

        # Create the logging update
        logging_update = LoggingUpdateFields(additional_data=update_data)

        response: ModuleUpdatedLogLevel | list[ResultUpdateRequest] | None

        if module_name:
            response = await state.client.devops.logging.by_module_name(module_name).put(body=logging_update)
        else:
            response = await state.client.devops.logging.put(body=logging_update)

        output_json(model_to_dict(response))

    asyncio.run(_run())
