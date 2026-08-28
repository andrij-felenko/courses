static void submit(struct batch *b)
{
    long max = sysconf(_SC_AIO_LISTIO_MAX);       /* -1 — межі не оголошено */
    int chunk = (max > 0 && max < b->n) ? (int)max : b->n;

    for (int i = 0; i < b->n; i += chunk) {
        int k = (b->n - i < chunk) ? b->n - i : chunk;
        if (lio_listio(LIO_NOWAIT, &b->cb[i], k, NULL) == -1) {
            perror("lio_listio");       /* EAGAIN — уперлися в AIO_MAX */
            exit(1);
        }
    }
}
