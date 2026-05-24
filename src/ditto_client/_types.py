from enum import StrEnum

from ditto_client.generated.ditto_client import DittoClient


class DittoAuthType(StrEnum):
    """Authentication types supported by Ditto client."""

    BASIC = "basic"
    PRE_AUTH = "pre-auth"
    JWT = "jwt"


class CmdState:
    """Holds state shared across all CLI commands."""

    def __init__(self) -> None:
        self._client: DittoClient | None = None
        self._table: bool = False
        self._auth_type: DittoAuthType = DittoAuthType.BASIC

    @property
    def auth_type(self) -> DittoAuthType:
        """Get authentication type."""
        return self._auth_type

    @property
    def client(self) -> DittoClient:
        """Access Ditto client with validation."""
        if self._client is None:
            raise ValueError("Ditto client has not been initialized")
        return self._client

    @client.setter
    def client(self, value: DittoClient) -> None:
        """Set Ditto client."""
        self._client = value

    @property
    def table(self) -> bool:
        """Get table output flag."""
        return self._table

    @table.setter
    def table(self, value: bool) -> None:
        """Set table output flag."""
        self._table = value
