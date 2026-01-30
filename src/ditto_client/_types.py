from ditto_client.generated.ditto_client import DittoClient


class CmdState:
    """Holds state shared across all CLI commands."""

    def __init__(self) -> None:
        self._client: DittoClient | None = None

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
