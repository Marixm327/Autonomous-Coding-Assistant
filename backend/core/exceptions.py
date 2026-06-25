class AISEError(Exception):
    """Base exception for all AI Software Engineer errors."""


class IngestionError(AISEError):
    pass


class ParsingError(AISEError):
    pass


class RetrievalError(AISEError):
    pass


class AgentError(AISEError):
    pass


class ToolError(AISEError):
    pass


class RepositoryNotFoundError(AISEError):
    pass


class ConnectorError(AISEError):
    pass
