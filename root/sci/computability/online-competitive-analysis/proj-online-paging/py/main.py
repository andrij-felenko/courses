import random
from collections import deque

class FIFOCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.queue = deque()
        self.in_cache = set()
        self.misses = 0

    def access(self, page: int):
        if page in self.in_cache:
            return  # Hit
        self.misses += 1
        if len(self.queue) == self.capacity:
            evicted = self.queue.popleft()
            self.in_cache.remove(evicted)
        self.queue.append(page)
        self.in_cache.add(page)

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # page -> None (зберігає порядок вставки в Python 3.7+)
        self.misses = 0

    def access(self, page: int):
        if page in self.cache:
            # Move to end (most recent)
            del self.cache[page]
            self.cache[page] = None
            return  # Hit
        self.misses += 1
        if len(self.cache) == self.capacity:
            # Evict first item (least recent)
            oldest = next(iter(self.cache))
            del self.cache[oldest]
        self.cache[page] = None

class MarkerCache:
    def __init__(self, capacity: int, seed: int = 42):
        self.capacity = capacity
        self.cache = set()
        self.marked = set()
        self.rng = random.Random(seed)
        self.misses = 0

    def access(self, page: int):
        if page in self.cache:
            self.marked.add(page)
            return  # Hit
        self.misses += 1
        if len(self.cache) == self.capacity:
            if len(self.marked) == self.capacity:
                self.marked.clear()  # Скидання фази
            unmarked = list(self.cache - self.marked)
            evicted = self.rng.choice(unmarked)
            self.cache.remove(evicted)
        self.cache.add(page)
        self.marked.add(page)

class BeladyOPT:
    def __init__(self, capacity: int):
        self.capacity = capacity

    def simulate(self, stream: list[int]) -> int:
        cache = set()
        misses = 0
        for i, page in enumerate(stream):
            if page in cache:
                continue
            misses += 1
            if len(cache) == self.capacity:
                # Знаходимо сторінку з найдальшим майбутнім використанням
                farthest_page = None
                farthest_idx = -1
                for cached_page in cache:
                    try:
                        next_idx = stream.index(cached_page, i + 1)
                    except ValueError:
                        next_idx = float('inf')
                    if next_idx > farthest_idx:
                        farthest_idx = next_idx
                        farthest_page = cached_page
                cache.remove(farthest_page)
            cache.insert = cache.add(page)
        return misses

if __name__ == "__main__":
    CACHE_SIZE = 4
    stream = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5, 3, 2, 1, 4, 5]

    fifo = FIFOCache(CACHE_SIZE)
    lru = LRUCache(CACHE_SIZE)
    marker = MarkerCache(CACHE_SIZE, 12345)
    opt = BeladyOPT(CACHE_SIZE)

    for p in stream:
        fifo.access(p)
        lru.access(p)
        marker.access(p)

    opt_misses = opt.simulate(stream)

    print(f"--- Результати симуляції (k = {CACHE_SIZE}) ---")
    print(f"{'Алгоритм':<18} | {'Промахи':<10} | {'Ratio (ALG/OPT)'}")
    print("-" * 45)
    print(f"{'OPT (Бєладі)':<18} | {opt_misses:<10} | 1.00")
    print(f"{'LRU':<18} | {lru.misses:<10} | {lru.misses / opt_misses:.2f}")
    print(f"{'FIFO':<18} | {fifo.misses:<10} | {fifo.misses / opt_misses:.2f}")
    print(f"{'Marker (Random)':<18} | {marker.misses:<10} | {marker.misses / opt_misses:.2f}")
