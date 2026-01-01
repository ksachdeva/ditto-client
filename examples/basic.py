import asyncio

from kiota_http.httpx_request_adapter import HttpxRequestAdapter
from rich import print as rprint

from ditto_client import BasicAuthProvider
from ditto_client.generated.ditto_client import DittoClient

_USERNAME = "ditto"
_PASSWORD = "ditto"


async def main() -> None:
    auth_provider = BasicAuthProvider(user_name=_USERNAME, password=_PASSWORD)

    request_adapter = HttpxRequestAdapter(auth_provider)
    request_adapter.base_url = "http://host.docker.internal:8080"

    ditto_client = DittoClient(request_adapter)

    response = await ditto_client.api.two.things.get()

    rprint(response)


if __name__ == "__main__":
    asyncio.run(main())
