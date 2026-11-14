"""
Design and implement a thread-safe Barrier for synchronizing a fixed number of threads.

Implement the SimpleBarrier class:
- SimpleBarrier(int parties): Initializes the barrier for the given number of threads (`parties`).
- void wait(): Blocks the calling thread until all `parties` threads have called `wait()`.
  When the last (`parties`-th) thread calls `wait()`, all waiting threads are unblocked and proceed.
- int waiting(): Returns the number of threads currently blocked at the barrier in a thread-safe manner.

Constraints:
- 1 <= parties <= 100
- Multiple threads will call `wait()` and `waiting()` concurrently.
- Do NOT use Python's built-in `threading.Barrier` (implement using lower-level synchronization primitives).
"""
import random
import threading
import time


class SimpleBarrier:
    def __init__(self, parties: int):
        """
        Barrier Pattern contains a lock and a counter
        :param parties:
        """
        self._lock = threading.Lock() # Job 1: mutex for self.counter
        self._sem = threading.Semaphore(0) # by default it is one, we need to set it zero for it to function as closed gate for threads
        self.parties = parties
        self.counter = 0

    def wait(self) -> None:
        with self._lock:
            self.counter += 1
            if self.counter == self.parties:
                # reset counter
                self.counter = 0
                # n-1 threads are sleeping
                for _ in range(self.parties - 1):
                    self._sem.release()
                return

        self._sem.acquire()

    def waiting(self) -> int:
        # external system can check if barrier is in use or not
        with self._lock:
            return self.counter

def worker(i: int, barrier: SimpleBarrier):
    print(f"worker: {i} started work")
    time.sleep(random.uniform(1,3))
    print(f"worker: {i} is at the barrier")
    barrier.wait()
    print(f"worked passed the barrier.\n")


if __name__ == '__main__':
    parties = 3
    barrier = SimpleBarrier(parties)
    threads = []
    for party_id in range(parties):
        threads.append(threading.Thread(target=worker, args=(party_id,barrier)))

    for thread in threads:
        thread.start()

