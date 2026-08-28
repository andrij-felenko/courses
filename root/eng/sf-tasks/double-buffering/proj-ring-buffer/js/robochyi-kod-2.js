  // забрати до n байтів суцільним блоком; повертає скільки реально віддав
  popBlock(dst, n) {
    if (n > this.count) n = this.count;    // не більше, ніж є
    let first = RB_SIZE - this.tail;       // до фізичного краю масиву
    if (first > n) first = n;
    dst.set(this.buf.subarray(this.tail, this.tail + first), 0);   // частина 1: tail..край
    dst.set(this.buf.subarray(0, n - first), first);               // частина 2: з початку
    this.tail = (this.tail + n) & RB_MASK;
    this.count -= n;
    return n;
  }
