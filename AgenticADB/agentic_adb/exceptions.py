class AgenticADBError(Exception):
    """Base exception for all AgenticADB errors."""
    pass

class CommandError(AgenticADBError):
    """Raised when an ADB or IDB command fails."""
    pass

class ParseError(AgenticADBError):
    """Raised when parsing UI hierarchy output fails."""
    pass

class DeviceNotFoundError(AgenticADBError):
    """Raised when a specific device cannot be found or connected."""
    pass
