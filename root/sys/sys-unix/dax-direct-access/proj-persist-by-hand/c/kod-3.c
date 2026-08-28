static uint64_t seq;                /* номер наступного запису; ставить recover() */

static int append(struct slot *ring, const void *rec, uint32_t n)
{
    struct slot *s = &ring[seq % SLOTS];
    if (n > sizeof s->body) { errno = EMSGSIZE; return -1; }

    if (s->commit != 0) {                       /* слот іде на друге коло: */
        __atomic_store_n(&s->commit, (uint64_t)0, __ATOMIC_RELAXED);
        flush(&s->commit, 8); fence();          /* спершу зняти стару ознаку */
    }

    memcpy(s->body, rec, n);                    /* 1 */
    s->len = n;
    s->crc = crc32_bitwise(rec, n);
    flush(&s->len, 8 + n);                      /* 2 */
    fence();                                    /* 3 */

    __atomic_store_n(&s->commit, seq + 1, __ATOMIC_RELAXED);   /* 4 */
    flush(&s->commit, 8);                       /* 5 */
    fence();                                    /* 6 */

    seq++;
    return 0;
}
