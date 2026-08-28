static size_t drain(struct batch *b)
{
    const struct aiocb *pend[NREQ];
    size_t got = 0;
    int left = b->n;

    while (left > 0) {
        int k = 0;
        for (int i = 0; i < b->n; i++)
            if (b->cb[i]) pend[k++] = b->cb[i];      /* лише ті, що в польоті */

        if (aio_suspend(pend, k, NULL) == -1) {
            if (errno == EINTR) continue;            /* сигнал — не біда */
            perror("aio_suspend");
            exit(1);
        }

        for (int i = 0; i < b->n; i++) {
            if (!b->cb[i]) continue;
            int e = aio_error(b->cb[i]);
            if (e == EINPROGRESS) continue;          /* цей ще працює */

            ssize_t r = aio_return(b->cb[i]);        /* рівно один раз на запит */
            if (e == 0) {
                got += (size_t)r;
                if (r != BLK) fprintf(stderr, "коротке читання: %zd\n", r);
            } else {
                fprintf(stderr, "запит %d: %s\n", i, strerror(e));
            }
            free(b->cb[i]);                          /* аж тепер aiocb нічий */
            b->cb[i] = NULL;
            left--;
        }
    }
    return got;
}
