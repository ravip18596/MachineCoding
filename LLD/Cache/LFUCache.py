'''
Below is a self-contained, single-file implementation of an LFU (Least-Frequently-Used) Cache that also keeps an LRU tie-breaker inside each frequency bucket.
All operations are O(1) and the code is thread-safe.
'''

from __future__ import annotations
import threading
from collections import defaultdict, OrderedDict
from typing import Any, Optional, Dict

class LFUCache:
    """
    O(1) LFU cache with LRU eviction within the same frequency.
    Thread-safe.
    """

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self._lock = threading.RLock()

        # key -> (value, freq)
        self._kv: Dict[Any, tuple[Any, int]] = {}

        # freq -> OrderedDict[key, None]  (insertion order == LRU)
        self._freq_map: Dict[int, OrderedDict[Any, None]] = defaultdict(OrderedDict)

        self._min_freq = 0   # smallest frequency currently in the cache

    # ---------------- Public API ---------------- #
    def get(self, key: Any) -> Optional[Any]:
        with self._lock:
            if key not in self._kv:
                return None
            value, freq = self._kv[key]
            self._increment_freq(key, freq)
            return value

    def set(self, key: Any, value: Any) -> None:
        with self._lock:
            if key in self._kv:
                # Update existing key
                old_val, freq = self._kv[key]
                self._kv[key] = (value, freq)
                self._increment_freq(key, freq)
                return

            if len(self._kv) >= self.capacity:
                # Evict LFU (and LRU among that frequency)
                lfu_bucket = self._freq_map[self._min_freq]
                lru_key, _ = lfu_bucket.popitem(last=False)  # first = oldest
                if not lfu_bucket:
                    del self._freq_map[self._min_freq]
                del self._kv[lru_key]

            # Insert new key with frequency 1
            self._kv[key] = (value, 1)
            self._freq_map[1][key] = None
            self._min_freq = 1

    # ---------------- Internal helpers ---------------- #
    def _increment_freq(self, key: Any, old_freq: int) -> None:
        # Remove from old bucket
        bucket = self._freq_map[old_freq]
        del bucket[key]
        if not bucket:
            del self._freq_map[old_freq]
            if self._min_freq == old_freq:
                self._min_freq += 1

        # Add to new bucket
        new_freq = old_freq + 1
        self._kv[key] = (self._kv[key][0], new_freq)
        self._freq_map[new_freq][key] = None

    # ---------------- Diagnostics ---------------- #
    def debug(self) -> None:
        with self._lock:
            print("KV:", self._kv)
            print("Freq map:", {k: list(v.keys()) for k, v in self._freq_map.items()})
            print("min_freq:", self._min_freq)


cache = LFUCache(3)
cache.set("a", 1)
cache.set("b", 2)
cache.set("c", 3)
cache.get("a")      # a.freq becomes 2
cache.set("d", 4)   # evicts b (freq=1)
print(cache.get("b"))  # None
print(cache.get("a"))  # 1
cache.debug()
