    # забрати до n байтів суцільним блоком; повертає bytes, реально відданий
    def pop_block(self, n):
        if n > self.count:                 # не більше, ніж є
            n = self.count
        first = RB_SIZE - self.tail        # до фізичного краю масиву
        if first > n:
            first = n
        out = bytes(self.buf[self.tail:self.tail + first])   # частина 1: tail..край
        out += bytes(self.buf[0:n - first])                   # частина 2: з початку
        self.tail = (self.tail + n) & RB_MASK
        self.count -= n
        return out
