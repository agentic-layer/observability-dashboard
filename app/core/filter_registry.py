"""Registry for tracking unique filter values seen in events."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict

logger = logging.getLogger(__name__)


class FilterRegistry:
    """
    Track unique filter values seen in events with TTL-based expiry.

    This registry maintains an in-memory cache of conversation IDs and workforce names
    that have been seen in recent events. Values automatically expire after the TTL period.
    """

    def __init__(self, ttl_hours: int = 24):
        """
        Initialize the filter registry.

        Args:
            ttl_hours: Time-to-live in hours for tracked values (default: 24)
        """
        self.conversation_ids: Dict[str, datetime] = {}
        self.workforce_names: Dict[str, datetime] = {}
        self.ttl = timedelta(hours=ttl_hours)
        logger.info(f"FilterRegistry initialized with TTL of {ttl_hours} hours")

    def register_event(self, conversation_id: str, workforce_name: str | None) -> None:
        """
        Register filter values from an event.

        Args:
            conversation_id: The conversation ID from the event
            workforce_name: The workforce name from the event (can be None)
        """
        now = datetime.now(timezone.utc)

        # Track conversation_id
        if conversation_id not in self.conversation_ids:
            logger.debug(f"Registered new conversation_id: {conversation_id}")
        self.conversation_ids[conversation_id] = now

        # Track workforce_name if present
        if workforce_name:
            if workforce_name not in self.workforce_names:
                logger.debug(f"Registered new workforce_name: {workforce_name}")
            self.workforce_names[workforce_name] = now

    def get_conversation_ids(self) -> list[str]:
        """
        Get all active conversation IDs.

        Returns:
            Sorted list of conversation IDs seen within the TTL window
        """
        self._cleanup()
        return sorted(self.conversation_ids.keys())

    def get_workforce_names(self) -> list[str]:
        """
        Get all active workforce names.

        Returns:
            Sorted list of workforce names seen within the TTL window
        """
        self._cleanup()
        return sorted(self.workforce_names.keys())

    def _cleanup(self) -> None:
        """Remove expired entries based on TTL."""
        now = datetime.now(timezone.utc)
        cutoff = now - self.ttl

        # Clean up expired conversation IDs
        expired_conversations = [k for k, v in self.conversation_ids.items() if v <= cutoff]
        for k in expired_conversations:
            del self.conversation_ids[k]

        # Clean up expired workforce names
        expired_workforces = [k for k, v in self.workforce_names.items() if v <= cutoff]
        for k in expired_workforces:
            del self.workforce_names[k]

        if expired_conversations or expired_workforces:
            logger.debug(
                f"Cleaned up {len(expired_conversations)} conversation_ids and "
                f"{len(expired_workforces)} workforce_names (expired after {self.ttl})"
            )

    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about tracked filter values.

        Returns:
            Dictionary with counts of tracked values
        """
        self._cleanup()
        return {
            "conversation_ids_count": len(self.conversation_ids),
            "workforce_names_count": len(self.workforce_names),
        }
