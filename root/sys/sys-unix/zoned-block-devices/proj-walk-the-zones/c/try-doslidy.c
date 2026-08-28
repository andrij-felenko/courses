static void try_write(int fd, const void *buf, size_t len, off_t off,
                      const char *what)
{
    ssize_t n = pwrite(fd, buf, len, off);

    if (n < 0)
        printf("  %s: помилка, errno %d (%s)\n", what, errno, strerror(errno));
    else if ((size_t)n != len)
        printf("  %s: коротко — %zd із %zu Б\n", what, n, len);
    else
        printf("  %s: записано %zu Б\n", what, len);
}

static void experiments(int fd, uint32_t zsect, unsigned lbs, uint32_t nr)
{
    struct blk_zone z;
    struct blk_zone_range rg;
    void *buf;

    if (!find_target(fd, nr, &z)) {
        fprintf(stderr, "порожньої послідовної зони немає\n");
        return;
    }
    /* прямий ввід-вивід вимагає вирівняної АДРЕСИ буфера, не лише довжини */
    if (posix_memalign(&buf, lbs, lbs) != 0) {
        fprintf(stderr, "вирівняного буфера не вийшло\n");
        return;
    }
    memset(buf, 0xA5, lbs);

    printf("\nпіддослідна зона: сектор %llu, ємність %llu секторів\n",
           (unsigned long long)z.start,
           (unsigned long long)(z.capacity ? z.capacity : z.len));

    try_write(fd, buf, lbs, (off_t)z.wp * SECT, "запис у вказівник");
    z = zone_at(fd, z.start);
    printf("     вказівник +%llu, стан «%s»\n",
           (unsigned long long)(z.wp - z.start), cond_name(z.cond));

    try_write(fd, buf, lbs, (off_t)z.wp * SECT + lbs, "запис повз вказівник");
    z = zone_at(fd, z.start);
    printf("     вказівник +%llu, стан «%s»\n",
           (unsigned long long)(z.wp - z.start), cond_name(z.cond));

    rg.sector = z.start + 8;          /* навмисно не з межі зони */
    rg.nr_sectors = zsect;
    if (ioctl(fd, BLKRESETZONE, &rg) < 0)
        printf("  скидання з середини зони: errno %d (%s)\n",
               errno, strerror(errno));

    rg.sector = z.start;              /* а тепер рівно на зону */
    rg.nr_sectors = zsect;
    if (ioctl(fd, BLKRESETZONE, &rg) < 0) {
        perror("BLKRESETZONE");
    } else {
        z = zone_at(fd, z.start);
        printf("  скидання зони: вказівник +%llu, стан «%s»\n",
               (unsigned long long)(z.wp - z.start), cond_name(z.cond));
    }
    free(buf);
}

int main(int argc, char **argv)
{
    uint32_t zsect = 0, nr = 0;
    int lbs = 0, fd, do_write;
    const char *path;

    if (argc < 2) {
        fprintf(stderr, "вжиток: %s <вузол> [--write]\n", argv[0]);
        return 2;
    }
    path = argv[1];
    do_write = (argc > 2 && strcmp(argv[2], "--write") == 0);

    /* O_DIRECT тут не оптимізація, а умова задачі: кеш сторінок віддає
       брудні сторінки носієві в зручному собі порядку, а послідовна
       зона такого не пробачає */
    fd = open(path, O_RDWR | O_DIRECT);
    if (fd < 0) { perror(path); return 1; }

    if (ioctl(fd, BLKGETZONESZ, &zsect) < 0) { perror("BLKGETZONESZ"); return 1; }
    if (ioctl(fd, BLKGETNRZONES, &nr) < 0)   { perror("BLKGETNRZONES"); return 1; }
    if (ioctl(fd, BLKSSZGET, &lbs) < 0)      { perror("BLKSSZGET"); return 1; }

    /* нуль у будь-якому з двох означає «пристрій не зонований»: BLKGETZONESZ
       віддає chunk_sectors, а це поле буває ненульовим і в масивів */
    if (zsect == 0 || nr == 0) {
        fprintf(stderr, "%s: пристрій не зонований\n", path);
        return 1;
    }
    printf("зона %u секторів (%.1f МіБ), зон %u, логічний блок %d Б\n\n",
           zsect, zsect * (double)SECT / (1024 * 1024), nr, lbs);

    print_table(fd, nr);
    if (do_write)
        experiments(fd, zsect, (unsigned)lbs, nr);

    close(fd);
    return 0;
}
