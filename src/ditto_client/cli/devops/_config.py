import asyncio

from typer import Context, Typer

from ditto_client.cli._output import model_to_dict, output_json, output_message

config_app = Typer()


@config_app.command()
def get(ctx: Context) -> None:
    """Get configuration from Ditto services."""
    state = ctx.obj

    async def _run() -> None:
        response = await state.client.devops.config.get()

        if not response:
            output_message("No configuration found", level="warning")
            return

        output_json(model_to_dict(response))

    asyncio.run(_run())
