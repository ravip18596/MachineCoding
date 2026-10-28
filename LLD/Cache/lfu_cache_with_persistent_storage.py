import threading
from abc import ABC, abstractmethod
from collections import OrderedDict, defaultdict
from typing import Dict, Tuple

# defining interface using strategy pattern
class PersistentStorage(ABC):
    @abstractmethod
    def save(self, key: int, val: str): pass

    @abstractmethod
    def load(self, key: int): pass

    @abstractmethod
    def delete(self, key: int): pass

class LFUCache:
    def __init__(self, cap:int, db: PersistentStorage):
        self.cap = cap
        self._db = db
        self._min_freq = 0

        self._lock = threading.RLock
        # key -> (value, freq)
        self._key_map: Dict[int, Tuple[str, int]] = {}
        self._freq_map: Dict[int, OrderedDict] = defaultdict(OrderedDict)

    def get(self, key:int) -> str:
        with self._lock:
            # cache miss
            if key not in self._key_map:
                # load from disk
                val = self._db.load(key)
                self._put_internal(key, val, save_to_db=False)
                return val

            # cache hit: Retrieve data and promote frequency
            val, freq = self._key_map[key]

            # Remove key from its frequency bucket
            self._freq_map[freq].pop(key)

            # Update min_freq if lowest bucket is empty
            if self._min_freq == freq and self._freq_map[key] is None:
                self._min_freq += 1

            self._key_map[key] = (val, freq+1)
            # update key to new freq bucket
            self._freq_map[freq+1][key] = None
            return val

    def _put_internal(self, key:int, val: str, save_to_db: bool):
        if self.cap == 0:
            return
        with self._lock:
            if save_to_db:
                self._db.save(key, val)

    def put(self, key:int, val: str):
        self._put_internal(key, val, save_to_db=True)

if __name__ == '__main__':
    class MockPersistentDB(PersistentStorage):
        def __init__(self):
            self.file = {}

        def save(self, key: int, val: str):
            print(f"saving {key}:{val} in disk")
            self.file[key] = val

        def load(self, key: int) -> str:
            return self.file.get(key)

        def delete(self, key: int):
            if key in self.file:
                del self.file[key]

    db = MockPersistentDB()

