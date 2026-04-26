from typing import TypeVar, Protocol, List

T = TypeVar("T")

class BaseParser(Protocol[T]):
    """Generic protocol for UI hierarchy parsers."""

    def parse(self, raw: str) -> List[T]:
        """Parses the raw hierarchy string into a list of parsed models.

        Args:
            raw: The raw string representation of the UI hierarchy (e.g. XML or JSON).

        Returns:
            A list of parsed objects.
        """
        ...
