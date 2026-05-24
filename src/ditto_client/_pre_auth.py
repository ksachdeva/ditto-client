from typing import Any

from kiota_abstractions.authentication.authentication_provider import AuthenticationProvider
from kiota_abstractions.headers_collection import HeadersCollection
from kiota_abstractions.request_information import RequestInformation


class PreAuthProvider(AuthenticationProvider):
    def __init__(self, auth_subject: str) -> None:
        self._auth_subject = auth_subject

    async def authenticate_request(
        self,
        request: RequestInformation,
        additional_authentication_context: dict[str, Any] | None = None,
    ) -> None:
        if additional_authentication_context is None:
            additional_authentication_context = {}

        if not request.request_headers:
            request.headers = HeadersCollection()

        request.headers.add("x-ditto-pre-authenticated", self._auth_subject)
