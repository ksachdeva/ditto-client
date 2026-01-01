import binascii
from typing import Any

from kiota_abstractions.authentication.authentication_provider import AuthenticationProvider
from kiota_abstractions.headers_collection import HeadersCollection
from kiota_abstractions.request_information import RequestInformation


def to_bytes(value: str | bytes, encoding: str = "utf-8") -> bytes:
    return value.encode(encoding) if isinstance(value, str) else value


def to_str(value: str | bytes, encoding: str = "utf-8") -> str:
    return value if isinstance(value, str) else value.decode(encoding)


def b64encode(s: Any, altchars: Any = None) -> bytes:
    encoded = binascii.b2a_base64(s, newline=False)
    if altchars is not None:
        assert len(altchars) == 2, repr(altchars)
        return encoded.translate(bytes.maketrans(b"+/", altchars))
    return encoded


def _build_auth_header(username: str | bytes, password: str | bytes) -> str:
    userpass = b":".join((to_bytes(username), to_bytes(password)))
    token = b64encode(userpass).decode()
    return f"Basic {token}"


class BasicAuthProvider(AuthenticationProvider):
    def __init__(
        self,
        user_name: str,
        password: str,
    ) -> None:
        self._user_name = user_name
        self._password = password

    async def authenticate_request(
        self,
        request: RequestInformation,
        additional_authentication_context: dict[str, Any] | None = None,
    ) -> None:
        if additional_authentication_context is None:
            additional_authentication_context = {}

        if not request.request_headers:
            request.headers = HeadersCollection()

        request.headers.add("Authorization", _build_auth_header(self._user_name, self._password))
