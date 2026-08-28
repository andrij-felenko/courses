static void exp_willneed(int fd)
{
    struct mark m;
    size_t n = FSIZE / PGSZ;
    chill(fd);
    char *p = mmap(NULL, FSIZE, PROT_READ, MAP_PRIVATE, fd, 0);

    mark_begin(&m);
    madvise(p, FSIZE, MADV_WILLNEED);
    mark_end(&m, "madvise(MADV_WILLNEED)");

    /* WILLNEED лише ЗАПУСКАЄ читання й одразу вертається. Якщо піти в обхід
       негайно, великі збої нікуди не подінуться — чекаємо резидентності. */
    double t0 = now();
    while (resident(p, FSIZE) < n && now() - t0 < 5.0)
        nanosleep(&(struct timespec){0, 1000000}, NULL);
    printf("  прогрівання: %.1f мс, резидентних %lu з %zu\n",
           (now() - t0) * 1e3, resident(p, FSIZE), n);

    mark_begin(&m); touch_seq(p, FSIZE, 0); mark_end(&m, "  обхід");
    munmap(p, FSIZE);
}
