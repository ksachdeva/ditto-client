import os

from kiota_http.httpx_request_adapter import HttpxRequestAdapter

from ditto_client.generated.ditto_client import DittoClient

from ._basic_auth import BasicAuthProvider


def _create_client(user_name: str, password: str) -> DittoClient:
    base_url = os.getenv("DITTO_BASE_URL", "http://host.docker.internal:8080")

    auth_provider = BasicAuthProvider(user_name=user_name, password=password)
    request_adapter = HttpxRequestAdapter(auth_provider)
    request_adapter.base_url = base_url

    return DittoClient(request_adapter)


def create_devops_client() -> DittoClient:
    user_name = os.getenv("DITTO_DEVOPS_USERNAME")
    password = os.getenv("DITTO_DEVOPS_PASSWORD")

    if not user_name or not password:
        raise ValueError("Environment variables DITTO_DEVOPS_USERNAME and DITTO_DEVOPS_PASSWORD must be set.")

    return _create_client(user_name, password)


def create_ditto_client() -> DittoClient:
    user_name = os.getenv("DITTO_USERNAME")
    password = os.getenv("DITTO_PASSWORD")

    if not user_name or not password:
        raise ValueError("Environment variables DITTO_USERNAME and DITTO_PASSWORD must be set.")

    return _create_client(user_name, password)
