"""
 Here is how the data structures interact:
 1. key_map (Hashmap): Maps key -> Node.
 2. This gives us $O(1)$ access to any node.freq_map (Hashmap): Maps frequency -> Doubly Linked List.
 3. Every time a node's frequency increases, we move it from the DLL at freq to the DLL at freq + 1.min_freq (Integer):

Tracks the lowest frequency currently in the cache so we can find the eviction candidate in O(1) time without scanning freq_map.
"""

"""
LFU Internal Structure

When multiple items have the same frequency, the DLL at that frequency acts as an LRU cache to break the tie.

key_map                 freq_map
[Key: 1] -> Node(1)     [Freq: 1] -> [Head] <-> Node(3) <-> [Tail]
[Key: 2] -> Node(2)     
[Key: 3] -> Node(3)     [Freq: 2] -> [Head] <-> Node(1) <-> [Tail]
                        
min_freq = 1            [Freq: 3] -> [Head] <-> Node(2) <-> [Tail]
"""

