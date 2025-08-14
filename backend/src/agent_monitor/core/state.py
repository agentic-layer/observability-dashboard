"""Global state management for the agent communications dashboard."""

from typing import Dict

from .connection_manager import ConnectionManager

# Dictionary to store managers for each conversation_id
conversation_managers: Dict[str, ConnectionManager] = {}

# Global manager for all conversations
global_manager = ConnectionManager("global")
