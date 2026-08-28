def _sift_up(h, i):
    while i > 0:
        parent = (i - 1) // 2
        if h[i] >= h[parent]:
            break
        h[i], h[parent] = h[parent], h[i]
        i = parent

def _sift_down(h, i):
    n = len(h)
    while True:
        smallest = i
        l, r = 2 * i + 1, 2 * i + 2
        if l < n and h[l] < h[smallest]:
            smallest = l
        if r < n and h[r] < h[smallest]:
            smallest = r
        if smallest == i:
            break
        h[i], h[smallest] = h[smallest], h[i]
        i = smallest

def push(h, x):
    h.append(x)
    _sift_up(h, len(h) - 1)

def pop_min(h):
    top = h[0]
    last = h.pop()
    if h:                 # якщо ще лишилися елементи
        h[0] = last
        _sift_down(h, 0)
    return top
