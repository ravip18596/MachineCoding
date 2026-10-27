# LRU with persistant storage
"""
To integrate pluggable persistence, we will define an interface (PersistenceStorage) that any database,
file system, or API can implement.

We will use a Write-Through strategy (saving to storage immediately on put) and
a Read-Through strategy (fetching from storage if a get results in an in-memory miss).
The RLock you used earlier is perfect here, as it allows get() to safely call put() when bringing an item back from storage without deadlocking.
"""

from abc import ABC, abstractmethod
from threading import RLock
from typing import Dict, Optional

# using strategy pattern. We can plug in API, database, etc with this interface
class PersistentStorage:
    @abstractmethod
    def save(self, key: int, val:str) -> None:
        pass

    def load(self, key: int) -> str:
        pass

    def delete(self, key: int) -> None:
        pass


class Node:
    def __init__(self, key: int, val: str):
        self.key = key
        self.value = val
        self.prev: Optional['Node'] = None
        self.next: Optional['Node'] = None


class LRUCache:
    def __init__(self, cap, db: PersistentStorage):
        self.cap = cap
        self._head = Node(0, "")
        self._tail = Node(0, "")
        self._hashmap: Dict[int, Node] = {}
        self._head.next = self._tail
        self._tail.prev = self._head
        self._rlock = RLock()
        self._db = db

    def __str__(self):
        tmp = self._head
        res = []
        while tmp and tmp!=self._tail:
            res.append(f'({tmp.key}, {tmp.value}) ')
            tmp = tmp.next
        return " -> ".join(res)

    def _remove_node(self, node: Node):
        prev = node.prev
        next = node.next
        prev.next = next
        next.prev = prev

    def _add_to_head(self, node: Node):
        """ Insert node strictly right of dummy head node"""
        tmp = self._head.next
        self._head.next = node
        node.prev = self._head
        node.next = tmp
        tmp.prev = node

    def put(self, key: int, val: str) -> None:
        with self._rlock:
            # check in hashmap if key exists
            if key in self._hashmap:
                node = self._hashmap[key]
                node.value = val
                # persist in storage as well
                val = self._db.load(key)
                print(f"Retrieved value from db storage: {val}")

                self._remove_node(node)
                self._add_to_head(node)
            else:
                # create new node
                node = Node(key=key, val=val)
                # store node in hashmap and storage
                self._hashmap[key] = node
                self._db.save(key, val)
                # append node to head's right
                self._add_to_head(node)


            # check capacity after adding new item
            if len(self._hashmap) > self.cap:
                # start evict procedure -> remove node left of tail
                # remove node from hashmap
                node_to_be_deleted = self._tail.prev
                self._remove_node(node_to_be_deleted)
                self._hashmap.pop(node_to_be_deleted.key)


    def get(self, key: int) -> str:
        with self._rlock:
            # check in hashmap if key exists
            if key not in self._hashmap:
                # check in storage
                val = self._db.load(key)
                self.put(key, val)
                return val

            # make the node with key as new head
            node = self._hashmap[key]

            self._remove_node(node)
            self._add_to_head(node)

            return node.value


if __name__ == '__main__':
    class MockPersistentDB(PersistentStorage):
        def __init__(self):
            self.file = {}

        def save(self, key: int, val:str) -> None:
            print(f"[DB] Saving {key}:{val} in disk")
            self.file[key] = val

        def load(self, key: int) -> str:
            return self.file.get(key)

        def delete(self, key: int) -> None:
            return self.file.pop(key, None)

    db = MockPersistentDB()
    print("Init DB")
    print("DB init")
    cache = LRUCache(2, db=db)
    cache.put(1, "a")
    cache.put(2, "b")
    print(f"Memory: {cache}")

    print("\n Start eviction")
    cache.put(3,"c") # Remove 1 from memory but persist in storage
    print(f"Memory: {cache}")

    print("Retrieving 1 from db and stores it back in memory and evict 2")
    val = cache.get(1)
    print(f"Retrieved val: {val}")
    print(f"Memory: {cache}")
