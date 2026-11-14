"""
Design and implement a thread-safe Bounded Blocking Queue with a fixed capacity.

Implement the BoundedBlockingQueue class:
- BoundedBlockingQueue(int capacity): Initializes the queue with a maximum capacity.
- void enqueue(int element): Adds an element to the front/back of the queue.
  If the queue is full, the calling thread must block until space becomes available.
- int dequeue(): Removes and returns the oldest element from the queue.
  If the queue is empty, the calling thread must block until an element is available.
- int size(): Returns the current number of elements in the queue in a thread-safe manner.

Constraints:
- 1 <= capacity <= 1000
- Multiple producer threads may call enqueue() concurrently.
- Multiple consumer threads may call dequeue() concurrently.
- Do NOT use Python's built-in queue.Queue (implement synchronization primitives yourself).
"""
import threading
from collections import deque


class BoundedBlockingQueue:
    def __init__(self, capacity: int):
        self._sem = threading.BoundedSemaphore(capacity)
        self.cap = capacity
        self._queue = deque()

    def enqueue(self, element: int) -> None:
        try:
            with self._sem:
                if self.size() >= self.cap:
                    return None
                self._queue.append(element)
        except ValueError as e:
            print(f"Error: {e}")

    def dequeue(self) -> int:
        try:
            with self._sem:
                if self.size() <= 0:
                    raise ValueError("Queue is empty")
                val = self._queue.popleft()
                return val
        except ValueError as e:
            print(f"Error: {e}")

    def size(self) -> int:
        return len(self._queue)

if __name__ == '__main__':
    queue = BoundedBlockingQueue(2)
    queue.enqueue(1)
    queue.enqueue(2)
    queue.enqueue(3)
    print(queue.__dict__)
    print(queue.dequeue())
    print(queue.__dict__)
