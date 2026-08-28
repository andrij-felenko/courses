static ssize_t copy_plain(int in, int out, size_t len)
{
    char buf[32768];
    size_t done = 0;
    while (done < len) {
        size_t want = len - done;
        if (want > sizeof buf) want = sizeof buf;
        ssize_t got = read(in, buf, want);
        if (got < 0) { if (errno == EINTR) continue; return -1; }
        if (got == 0) break;                        /* кінець файлу */
        for (ssize_t off = 0; off < got; ) {
            ssize_t put = write(out, buf + off, (size_t) (got - off));
            if (put < 0) { if (errno == EINTR) continue; return -1; }
            off += put;
        }
        done += (size_t) got;
    }
    return (ssize_t) done;
}

static ssize_t copy_chunk(int in, int out, size_t len)
{
    static int worth_trying = 1;    /* кешуємо ЛИШЕ «виклик є в цьому ядрі» */

    if (__atomic_load_n(&worth_trying, __ATOMIC_RELAXED)) {
        ssize_t n = copy_file_range(in, NULL, out, NULL, len, 0);
        if (n >= 0)
            return n;
        switch (errno) {
        case ENOSYS:                /* цього ядра виклик не має — назавжди */
            __atomic_store_n(&worth_trying, 0, __ATOMIC_RELAXED);
            break;
        case EXDEV:                 /* різні файлові системи */
        case EOPNOTSUPP:            /* саме ця система так не вміє */
        case EINVAL:                /* напр. вихідний дескриптор із O_APPEND */
            break;                  /* ця пара не вміє — наступна може вміти */
        default:
            return -1;              /* справжня помилка: ховати її не можна */
        }
    }
    return copy_plain(in, out, len);
}
