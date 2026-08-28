/* c */
void io_uring_buf_ring_add(struct io_uring_buf_ring *br, 
                           void *addr, 
                           unsigned int len, 
                           unsigned short bid, 
                           int mask, 
                           int buf_offset) {
    struct io_uring_buf *buf = &br->bufs[(br->tail + buf_offset) & mask];
    buf->addr = (unsigned long)addr;
    buf->len = len;
    buf->bid = bid;
}

void io_uring_buf_ring_advance(struct io_uring_buf_ring *br, int count) {
    /* Атомарний бар'єр пам'яті гарантує видимість записів для ядра */
    __atomic_store_n(&br->tail, br->tail + count, __ATOMIC_RELEASE);
}
