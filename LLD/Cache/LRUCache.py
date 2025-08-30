from __future__ import annotations
import threading
import pickle
import os
from typing import Optional, Any, Dict
from pathlib import Path

class _Node:
    """Doubly-linked list node used internally."""
    __slots__ = ("key", "val", "prev", "next")
    def __init__(self, key: Any, val: Any):
        self.key, self.val = key, val
        self.prev: Optional[_Node] = None
        self.next: Optional[_Node] = None

class LRUCache:
    """
    Thread-safe, O(1) LRU cache with pluggable persistence.
    """
    def __init__(self, capacity: int, persistence_dir: Optional[Path] = None):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self._lock = threading.RLock()          # Re-entrant for nested calls
        self._map: Dict[Any, _Node] = {}        # key -> node
        self._head = _Node(None, None)          # Dummy head
        self._tail = _Node(None, None)          # Dummy tail
        self._head.next = self._tail
        self._tail.prev = self._head

        # Persistence layer
        self._persistence_dir = persistence_dir
        if self._persistence_dir:
            self._persistence_dir.mkdir(parents=True, exist_ok=True)
            self._load_from_disk()

    # ------------------- Public API ------------------- #
    def get(self, key: Any) -> Optional[Any]:
        with self._lock:
            node = self._map.get(key)
            if node is None:
                return None
            self._move_to_front(node)
            return node.val

    def set(self, key: Any, value: Any) -> None:
        with self._lock:
            node = self._map.get(key)
            if node:
                node.val = value
                self._move_to_front(node)
            else:
                if len(self._map) >= self.capacity:
                    self._evict_lru()
                new_node = _Node(key, value)
                self._map[key] = new_node
                self._add_to_front(new_node)
                self._persist()

    # ------------------- Internals ------------------- #
    def _move_to_front(self, node: _Node) -> None:
        self._remove(node)
        self._add_to_front(node)

    def _add_to_front(self, node: _Node) -> None:
        node.prev = self._head
        node.next = self._head.next
        self._head.next.prev = node
        self._head.next = node

    def _remove(self, node: _Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def _evict_lru(self) -> None:
        lru = self._tail.prev
        self._remove(lru)
        del self._map[lru.key]
        self._persist()

    # ------------------- Persistence ------------------- #
    def _persist(self) -> None:
        if not self._persistence_dir:
            return
        snapshot = {node.key: node.val for node in self._map.values()}
        tmp = self._persistence_dir / "cache.tmp"
        final = self._persistence_dir / "cache.pkl"
        with tmp.open("wb") as f:
            pickle.dump(snapshot, f, protocol=pickle.HIGHEST_PROTOCOL)
        tmp.replace(final)  # Atomic on POSIX

    def _load_from_disk(self) -> None:
        final = self._persistence_dir / "cache.pkl"
        if not final.exists():
            return
        with final.open("rb") as f:
            snapshot: Dict[Any, Any] = pickle.load(f)
        for k, v in snapshot.items():
            self.set(k, v)  # Re-uses existing eviction logic
