from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from .events import CommunicationEvent


@dataclass
class FilterCriteria:
    """
    Filter criteria for WebSocket connections.

    Each field can be:
    - None: Match all values (no filtering on this field)
    - Specific value: Only match events with this exact value
    """

    conversation_id: Optional[str] = None
    workforce: Optional[str] = None
    # Easy to extend with more fields later:
    # environment: Optional[str] = None
    # agent_name: Optional[str] = None

    def matches(self, event: "CommunicationEvent") -> bool:
        """
        Check if an event matches this filter criteria.

        Args:
            event: The communication event to check

        Returns:
            True if the event matches all non-None filter criteria
        """
        # Check conversation_id filter
        if self.conversation_id is not None and event.conversation_id != self.conversation_id:
            return False

        # Check workforce filter
        if self.workforce is not None and event.workforce_name != self.workforce:
            return False

        # Add more filter checks here as needed

        return True

    @classmethod
    def from_query_params(cls, params: Dict[str, str]) -> "FilterCriteria":
        """
        Parse filter criteria from WebSocket query parameters.

        Example: /ws?conversation_id=abc-123&workforce=foo
        """
        return cls(
            conversation_id=params.get("conversation_id"),
            workforce=params.get("workforce"),
        )

    def is_empty(self) -> bool:
        """Check if this filter matches everything (all fields are None)"""
        return all(
            [
                self.conversation_id is None,
                self.workforce is None,
            ]
        )
