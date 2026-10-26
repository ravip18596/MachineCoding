# Data Structure Design
# 1. Hash Map -> to store all the key and Node obj reference.
#    Used in get operation to provide O(1) lookup
# 2. Double linked list -> to store key value pairs.
#    Maintain separate dummy header and tail nodes.
#    Help in providing O(1) update, add operations

from typing import Optional, List, Dict
from threading import RLock

class Node:
    def __init__(self, key: int, val: str):
        self.key = key
        self.value = val
        self.prev: Optional['Node'] = None
        self.next: Optional['Node'] = None


class LRUCache:
    def __init__(self, cap):
        self.cap = cap
        self._head = Node(0, 0)
        self._tail = Node(0, 0)
        self._hashmap = {}
        self._head.next = self._tail.prev
        self._rlock = RLock()

    def put(self, key: int, val: str) -> None:
        with self._rlock:
            if len(self._hashmap) >= self.cap:
                # start evict procedure -> remove node left of tail
                # remove node from hashmap
                node_to_be_deleted = self._tail.prev
                self._hashmap.pop(node_to_be_deleted.key)
                node_to_be_deleted._next = None
                node_to_be_deleted._prev = None


            node = Node(key=key, val=val)
            # append node to head's right
            self._head.next = node
            node.prev = self._head
            node.next = self._tail.prev

            # store node in hashmap
            self._hashmap[key] = node


    def get(self, key: int) -> str:
        with self._rlock:
            # check in hashmap if key exists
            if key in self._hashmap:
                node = self._hashmap[key]
            else:
                raise ValueError(f"Key: {key} does not exist")

            # make the node with key as new head
            node = self._hashmap[key]
            tmp = self._head.next
            self._head.next = node.prev
            node.next = tmp.prev

            return node.value


if __name__ == '__main__':
    lru_cache = LRUCache(cap=3)
    lru_cache.put(1, 'A')
    print(lru_cache)
    lru_cache.put(2, 'B')
    print(lru_cache)
    lru_cache.get(1)
    print(lru_cache)
    lru_cache.put(3, 'C')
    print(lru_cache)
    lru_cache.put(4, 'D')
    print(lru_cache)
    lru_cache.get(2)
    print(lru_cache)
    lru_cache.put(1, 'A+')
    print(lru_cache)
