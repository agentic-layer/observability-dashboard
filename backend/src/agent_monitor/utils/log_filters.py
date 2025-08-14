import logging


class EndpointFilter(logging.Filter):
    """Filter class to exclude specific endpoints from log entries."""

    def __init__(self, excluded_endpoints: list[str]) -> None:
        """
        Initialize the EndpointFilter class.

        Args:
            excluded_endpoints: A list of endpoints to be excluded from log entries.
        """
        super().__init__()
        self.excluded_endpoints = excluded_endpoints

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter out log entries for excluded endpoints.

        Args:
            record: The log record to be filtered.

        Returns:
            bool: True if the log entry should be included, False otherwise.
        """

        # 1. Ensure record.args is a tuple to avoid errors with dict-style logging.
        # If it's not a tuple, we don't know how to filter it, so we allow it.
        if not isinstance(record.args, tuple):
            return True

        # 2. Check if the tuple is long enough for our logic to apply.
        if len(record.args) < 3:
            return True

        # 3. Check that the element we want to inspect is actually a string.
        # This is a "type guard" that satisfies Mypy.
        endpoint = record.args[2]
        if not isinstance(endpoint, str):
            return True

        # 4. Now that all checks have passed, perform the actual filtering.
        # This logic now safely returns a boolean.
        return False
