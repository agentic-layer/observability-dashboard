"""API endpoints for retrieving available filter options."""

import logging
from typing import Dict, List

from fastapi import APIRouter

router = APIRouter(tags=["filters"])
logger = logging.getLogger(__name__)


@router.get("/api/filters")
async def get_filter_options() -> Dict[str, List[str]]:
    """
    Get available filter options for the frontend.

    Returns currently active conversation IDs and workforce names
    that have been seen in recent events (last 24 hours by default).

    The values are tracked in-memory as events flow through the system
    and automatically expire after the configured TTL period.

    Returns:
        Dictionary with two keys:
        - conversation_ids: List of unique conversation IDs
        - workforce_names: List of unique workforce names

    Example response:
        {
            "conversation_ids": [
                "1d1046f4-20da-4bed-9cc3-285d32292851",
                "abc123def-4567-890a-bcde-f0123456789a"
            ],
            "workforce_names": [
                "customer-support",
                "sales-automation"
            ]
        }
    """
    from ...core.state import filter_registry

    conversation_ids = filter_registry.get_conversation_ids()
    workforce_names = filter_registry.get_workforce_names()

    logger.debug(
        f"Returning filter options: {len(conversation_ids)} conversation_ids, {len(workforce_names)} workforce_names"
    )

    return {
        "conversation_ids": conversation_ids,
        "workforce_names": workforce_names,
    }


@router.get("/api/filters/stats")
async def get_filter_stats() -> Dict[str, int]:
    """
    Get statistics about tracked filter values.

    Returns:
        Dictionary with counts of currently tracked values
    """
    from ...core.state import filter_registry

    return filter_registry.get_stats()
