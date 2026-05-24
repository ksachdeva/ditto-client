import asyncio

import httpx
from kiota_http.httpx_request_adapter import HttpxRequestAdapter
from rich import print as rprint

from ditto_client import JWTAuthProvider
from ditto_client.generated.ditto_client import DittoClient


async def main() -> None:
    subject = "ditto"
    url = f"http://host.docker.internal:9900/{subject}/token"

    data = {
        "grant_type": "client_credentials",
        "client_id": subject,
        "client_secret": "secret",
        "scope": "openid",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            data=data,
            timeout=10.0,
        )

    response.raise_for_status()
    token = response.json()["access_token"]

    # pass the token to the JWTAuthProvider
    # print(token)

    auth_provider = JWTAuthProvider(token=token)

    request_adapter = HttpxRequestAdapter(auth_provider)
    request_adapter.base_url = "http://host.docker.internal:8081"

    ditto_client = DittoClient(request_adapter)

    response = await ditto_client.api.two.things.get()

    rprint(response)


if __name__ == "__main__":
    asyncio.run(main())
