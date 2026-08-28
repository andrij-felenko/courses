class MinHeap:
    """min-купа над щільним списком записів (key, ref); pos: ref -> індекс."""
    # ref — стабільний цілий дескриптор елемента (вершина, номер задачі).

    def __init__(self, cap):
        self.h = []                 # список пар (key, ref)
        self.pos = [-1] * cap       # ref -> індекс у h (-1 = не в черзі)

    def __len__(self):
        return len(self.h)

    def peek(self):                 # O(1)
        return self.h[0]

    def push(self, key, ref):       # O(log n)
        self.h.append((key, ref))
        self.pos[ref] = len(self.h) - 1
        self._sift_up(len(self.h) - 1)

    def pop_min(self):              # O(log n)
        self._swap(0, len(self.h) - 1)
        key, ref = self.h.pop()
        self.pos[ref] = -1
        if self.h:
            self._sift_down(0)
        return key, ref

    def decrease_key(self, ref, new_key):   # O(log n)
        i = self.pos[ref]
        self.h[i] = (new_key, ref)
        self._sift_up(i)

    @classmethod
    def build(cls, items, cap):     # O(n) — Флойдове heapify
        heap = cls(cap)
        heap.h = list(items)
        for i, (_key, ref) in enumerate(heap.h):
            heap.pos[ref] = i
        for i in range(len(heap.h) // 2 - 1, -1, -1):
            heap._sift_down(i)
        return heap

    def _swap(self, i, j):          # єдиний рух записів
        self.h[i], self.h[j] = self.h[j], self.h[i]
        self.pos[self.h[i][1]] = i
        self.pos[self.h[j][1]] = j

    def _sift_up(self, i):
        while i > 0:
            parent = (i - 1) // 2
            if self.h[parent][0] <= self.h[i][0]:
                break
            self._swap(i, parent)
            i = parent

    def _sift_down(self, i):
        n = len(self.h)
        while True:
            smallest, l, r = i, 2*i + 1, 2*i + 2
            if l < n and self.h[l][0] < self.h[smallest][0]:
                smallest = l
            if r < n and self.h[r][0] < self.h[smallest][0]:
                smallest = r
            if smallest == i:
                break
            self._swap(i, smallest)
            i = smallest
