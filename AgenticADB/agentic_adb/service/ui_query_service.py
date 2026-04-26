from typing import TypeVar, Generic

from agentic_adb.client.base_client import BaseClient
from agentic_adb.parser.base_parser import BaseParser
from agentic_adb.models import UIElement

T = TypeVar("T")

class UIQueryService(Generic[T]):
    """Service for handling read-only UI actions.

    Orchestrates the retrieval of UI hierarchy from the client and
    delegates transformation to the parser.
    """

    def __init__(self, client: BaseClient, parser: BaseParser[T]):
        """Initializes the UIQueryService.

        Args:
            client: The mobile device client (IO).
            parser: The parser to transform raw data.
        """
        self._client = client
        self._parser = parser
        self._cache: list[T] | None = None

    def get_ui_elements(self) -> list[T]:
        """Retrieves and parses the current UI hierarchy. Uses cache if available.

        Returns:
            A list of parsed models (e.g. UIElements).
        """
        if self._cache is not None:
            return self._cache

        raw_output = self._client.dump_ui()
        if not raw_output:
            self._cache = []
        else:
            self._cache = self._parser.parse(raw_output)

        return self._cache

    def clear_cache(self) -> None:
        """Clears the cached UI elements."""
        self._cache = None

    def get_raw_ui(self) -> str:
        """Retrieves the raw UI hierarchy string without parsing.

        Returns:
            The raw string representation of the UI hierarchy (e.g. XML or JSON).
        """
        return self._client.dump_ui()

    def parse_raw(self, raw_output: str) -> list[T]:
        """Parses a provided raw string of UI hierarchy.

        Args:
            raw_output: The raw string representation.

        Returns:
            A list of parsed models.
        """
        if not raw_output:
            return []
        return self._parser.parse(raw_output)
