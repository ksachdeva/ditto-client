import asyncio

from kiota_http.httpx_request_adapter import HttpxRequestAdapter
from rich import print as rprint

from ditto_client import PreAuthProvider
from ditto_client.generated.ditto_client import DittoClient


async def main() -> None:
    auth_provider = PreAuthProvider(auth_subject="ditto:ditto")

    request_adapter = HttpxRequestAdapter(auth_provider)
    request_adapter.base_url = "http://host.docker.internal:8081"

    ditto_client = DittoClient(request_adapter)

    response = await ditto_client.api.two.things.get()

    rprint(response)


if __name__ == "__main__":
    asyncio.run(main())
