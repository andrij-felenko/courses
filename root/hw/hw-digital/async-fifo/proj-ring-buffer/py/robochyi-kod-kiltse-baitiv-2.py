# Продюсер (виклик з ISR). Повертає True, якщо поклали; False, якщо повно.
def fifo_put(q, byte):
    h = q.head
    n = Fifo._next(h)
    if n == q.tail:            # повно → політика «відкинути новий»
        return False
    q.buf[h] = byte            # 1) СПЕРШУ дані у слот
    q.head = n                 # 2) ПОТІМ опублікувати нову голову
    return True


# Споживач (виклик з main/loop). Повертає (True, байт); (False, 0), якщо порожньо.
def fifo_get(q):
    t = q.tail
    if t == q.head:            # порожньо
        return False, 0
    out = q.buf[t]             # 1) СПЕРШУ прочитати дані
    q.tail = Fifo._next(t)     # 2) ПОТІМ звільнити слот
    return True, out
