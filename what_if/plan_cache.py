"""
Aexyron - Layer 4: Redis Pre-Computed Recovery Plan Cache.
"""

from typing import Dict, Any, Optional
import json


class PlanCache:
    """
    High-speed key-value cache for pre-computed recovery recipes.
    Supports Redis or in-memory dictionary fallback.
    Target retrieval latency: < 2ms.
    """

    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self._in_memory_store: Dict[str, str] = {}

    def store_plan(self, scenario_key: str, plan_data: Dict[str, Any], ttl_seconds: int = 60):
        serialized = json.dumps(plan_data)
        if self.redis_client:
            try:
                self.redis_client.setex(scenario_key, ttl_seconds, serialized)
                return
            except Exception:
                pass
        self._in_memory_store[scenario_key] = serialized

    def get_plan(self, scenario_key: str) -> Optional[Dict[str, Any]]:
        serialized = None
        if self.redis_client:
            try:
                serialized = self.redis_client.get(scenario_key)
            except Exception:
                pass
        if not serialized:
            serialized = self._in_memory_store.get(scenario_key)

        if serialized:
            if isinstance(serialized, bytes):
                serialized = serialized.decode("utf-8")
            return json.loads(serialized)
        return None
