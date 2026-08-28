static void hash_file(uint32_t idx)
{
    struct filerec *f = &fr[idx];
    int fd = open(f->path, O_RDONLY);
    if (fd < 0) { perror(f->path); f->nwin = 0; return; }
    posix_fadvise(fd, 0, 0, POSIX_FADV_SEQUENTIAL);

    unsigned char *buf = malloc(win);
    f->h      = calloc(f->nwin, sizeof *f->h);
    f->merged = calloc(f->nwin, 1);
    if (!buf || !f->h || !f->merged) { fprintf(stderr, "бракує пам'яті\n"); exit(1); }

    for (uint32_t i = 0; i < f->nwin; i++) {
        off_t  off = (off_t)i * win;
        size_t got = 0;
        while (got < win) {
            ssize_t k = pread(fd, buf + got, win - got, off + (off_t)got);
            if (k <= 0) break;
            got += (size_t)k;
        }
        if (got < win) { f->nwin = i; break; }   /* файл укоротився під нами */

        int zero;
        uint64_t h = blockhash(buf, win, &zero);
        if (zero || h == 0)                      /* суцільні нулі — майже завжди діра; */
            continue;                            /* нуль лишається ознакою «не чіпати» */
        f->h[i] = h;

        keys = grow(keys, &ckeys, nkeys + 1, sizeof *keys);
        keys[nkeys].h = h; keys[nkeys].f = idx; keys[nkeys].w = i;
        nkeys++;
    }

    posix_fadvise(fd, 0, 0, POSIX_FADV_DONTNEED);
    close(fd);
    free(buf);
}
