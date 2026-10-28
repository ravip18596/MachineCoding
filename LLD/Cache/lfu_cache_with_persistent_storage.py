"""
 Here is how the data structures interact:
 1. key_map (Hashmap): Maps key -> Node.
 2. This gives us $O(1)$ access to any node.freq_map (Hashmap): Maps frequency -> Doubly Linked List.
 3. Every time a node's frequency increases, we move it from the DLL at freq to the DLL at freq + 1.min_freq (Integer):

Tracks the lowest frequency currently in the cache so we can find the eviction candidate in O(1) time without scanning freq_map.

LFU Internal Structure

When multiple items have the same frequency, the DLL at that frequency acts as an LRU cache to break the tie.

key_map                 freq_map
[Key: 1] -> Node(1)     [Freq: 1] -> [Head] <-> Node(3) <-> [Tail]
[Key: 2] -> Node(2)     
[Key: 3] -> Node(3)     [Freq: 2] -> [Head] <-> Node(1) <-> [Tail]
                        
min_freq = 1            [Freq: 3] -> [Head] <-> Node(2) <-> [Tail]
"""

from collections import defaultdict, OrderedDict
import threading
from abc import abstractmethod, ABC
from typing import Dict, Tuple


class PersistentStorage(ABC):
    """ implements strategy pattern based interface"""
    @abstractmethod
    def save(self, key:int, val: str): pass

    @abstractmethod
    def load(self, key:int): pass

    @abstractmethod
    def delete(self, key:int): pass


class MockPersistentStore(PersistentStorage):
    def __init__(self):
        self.file = {}

    def save(self, key:int, val: str):
        self.file[key] = val

    def load(self, key:int) -> str:
        return self.file.get(key, '')

    def delete(self, key:int):
        if key in self.file:
            del self.file[key]


class LFUCache:
    def __init__(self, cap:int, db: PersistentStorage):
        self.cap = cap
        self._db = db
        self._lock = threading.RLock()
        self._min_freq = 0
        # key -> (value, freq)
        self.key_map: Dict[int, Tuple[str, int]] = {}
        self.freq_map: Dict[int, OrderedDict] = defaultdict(OrderedDict)

## Always update key_map and freq_map simultaneously
    def _put_internal(self, key: int, val: str, save_to_db: bool):
        with self._lock:
            if key in self.key_map:
                # update cache for its key
                _, freq = self.key_map[key]
                self.freq_map[freq].pop(key)

                # incase of empty freq bucket
                if self._min_freq == freq and self.freq_map[key] is None:
                    self._min_freq += 1

                self.key_map[key] = (val, freq+1)
                self.freq_map[freq+1][key] = None

                if save_to_db:
                    self._db.save(key, val)

                return


            # create new value
            if len(self.key_map) == self.cap:
                # remove LFU key which is LRU in min_freq bucket
                # time complexity of this operation is O(1)
                key, _ = self.freq_map[self._min_freq].popitem(last=False)
                del self.key_map[key]

            # orderedMap insert values at the end. LRU key is at front
            self.key_map[key] = (val, 1)
            self.freq_map[1][key] = None
            self._min_freq = 1

            if save_to_db:
                self._db.save(key, val)


    def put(self, key: int, val: str):
        self._put_internal(key, val, save_to_db=True)

    def get(self, key: int) -> str:
        # cache miss
        with self._lock:
            if key not in self.key_map:
                # load from disk
                val = self._db.load(key)
                if val != '':
                    # update frequency and insert again
                    self._put_internal(key, val, save_to_db=False)
                return val

            # cache hit
            val, freq = self.key_map[key]
            # 1. Remove key from its curr freq bucket
            self.freq_map[freq].pop(key)

            # 2. Update min_freq if lowest bucket is now empty
            if self._min_freq == freq and self.freq_map[freq] is None:
                self._min_freq += 1

            # 3. Update the key map with incremental freq
            self.key_map[key] = (val, freq+1)

            # 4. Add key to the new frequency bucket
            self.freq_map[freq+1][key] = None

            return val


if __name__ == '__main__':
    db = MockPersistentStore()
    cache = LFUCache(cap=3, db=db)
    cache.put(1, "a")
    cache.put(2, "b")
    val = cache.get(1)
    print(val)
    cache.put(3, "c")
    # Trigger eviction
    cache.put(4, "d")

