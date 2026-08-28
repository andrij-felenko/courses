int p[2];
pipe(p);
for (;;) {
    ssize_t n = splice(in, NULL, p[1], NULL, 64 << 10,
                       SPLICE_F_MOVE | SPLICE_F_MORE);
    if (n <= 0)
        break;                       /* 0 — кінець потоку, −1 — помилка */
    while (n > 0) {
        ssize_t m = splice(p[0], NULL, out, NULL, n,
                           SPLICE_F_MOVE | SPLICE_F_MORE);
        if (m <= 0)
            return -1;
        n -= m;
    }
}
