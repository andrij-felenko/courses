static int make_file(const char *path)
{
    int fd = open(path, O_RDWR | O_CREAT, 0644);
    struct stat st;
    fstat(fd, &st);
    if ((size_t)st.st_size < FSIZE) {
        char *chunk = malloc(1 << 20);
        memset(chunk, 0xA5, 1 << 20);
        for (size_t off = 0; off < FSIZE; off += (1 << 20))
            write(fd, chunk, 1 << 20);
        free(chunk);
    }
    fsync(fd);
    return fd;
}

/* Викинути сторінки файлу з кеша. Викидаються ЛИШЕ чисті — звідси fsync. */
static void chill(int fd)
{
    fsync(fd);
    posix_fadvise(fd, 0, 0, POSIX_FADV_DONTNEED);   /* 0 = до кінця файлу */
}

static void exp_file(int fd, const char *label, int cold, int advice, int randomly)
{
    struct mark m;
    size_t n = FSIZE / PGSZ;
    if (cold) chill(fd);

    /* Відображення ЩОРАЗУ нове: інакше таблиця сторінок лишиться від
       минулого проходу й збоїв не буде взагалі, хоч кеш і холодний. */
    char *p = mmap(NULL, FSIZE, PROT_READ, MAP_PRIVATE, fd, 0);
    if (advice) madvise(p, FSIZE, advice);
    printf("  %-32s резидентних до обходу: %lu з %zu\n",
           label, resident(p, FSIZE), n);

    size_t *idx = randomly ? permutation(n) : NULL;
    mark_begin(&m);
    if (idx) touch_perm(p, idx, n);
    else     touch_seq(p, FSIZE, 0);
    mark_end(&m, "  обхід");
    free(idx);
    munmap(p, FSIZE);
}
