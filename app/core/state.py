"""Global state management for the observability dashboard."""

from .connection_manager import ConnectionManager
from .filter_registry import FilterRegistry

# Single global connection manager for all WebSocket connections
# Each connection within this manager has its own FilterCriteria
connection_manager = ConnectionManager()

# Global filter registry for tracking unique conversation IDs and workforce names
# Values are tracked as events flow through the system with TTL-based expiry
filter_registry = FilterRegistry()
