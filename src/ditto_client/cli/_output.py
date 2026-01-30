"""Output utilities for CLI commands."""

import json
import sys
from typing import Any, cast

from kiota_serialization_json.json_serialization_writer_factory import JsonSerializationWriterFactory


def model_to_dict(model: Any) -> dict[str, Any]:
    """Convert any Kiota model to a dictionary using built-in serialization."""
    try:
        factory = JsonSerializationWriterFactory()
        writer = factory.get_serialization_writer("application/json")
        writer.write_object_value(None, model)
        content = writer.get_serialized_content()
        return cast(dict[str, Any], json.loads(content.decode("utf-8")))
    except TypeError:
        if hasattr(model, "additional_data") and model.additional_data:
            return cast(dict[str, Any], model.additional_data)
        return {}


def output_json(data: Any) -> None:
    """Output data as JSON."""
    json_str = json.dumps(data, indent=2, default=str)
    sys.stdout.write(f"{json_str}\n")


def output_message(message: str, level: str = "info") -> None:
    """Output a message with the specified level.

    Args:
        message: The message to output
        level: Message level - 'error', 'warning', 'success', or 'info'
    """
    level_upper = level.upper()
    formatted_message = f"[{level_upper}] {message}\n"

    if level == "error":
        sys.stderr.write(formatted_message)
    else:
        sys.stdout.write(formatted_message)
