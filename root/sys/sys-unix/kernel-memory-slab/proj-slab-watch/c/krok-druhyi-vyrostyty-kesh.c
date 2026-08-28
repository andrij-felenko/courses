static int cmd_grow(const char *dir, unsigned long n)
{
    int dfd = open(dir, O_RDONLY | O_DIRECTORY);
    if (dfd < 0) { fprintf(stderr, "%s: %s\n", dir, strerror(errno)); return 1; }

    struct cache a = snapshot("до", "dentry");

    char nm[64];
    struct stat st;
    unsigned long miss = 0;
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (unsigned long i = 0; i < n; i++) {
        snprintf(nm, sizeof nm, "nx-%ld-%lu", (long)getpid(), i);
        if (fstatat(dfd, nm, &st, AT_SYMLINK_NOFOLLOW) < 0 && errno == ENOENT)
            miss++;
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double dt = (t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec) / 1e9;
    printf("%lu невдалих пошуків за %.2f с (%.0f тис./с)\n",
           miss, dt, miss / dt / 1000.0);

    struct cache b = snapshot("після", "dentry");
    close(dfd);

    unsigned long dobj = sub(b.active_objs, a.active_objs);
    unsigned long dpg  = sub(b.num_slabs * b.pagesperslab,
                             a.num_slabs * a.pagesperslab);
    printf("\nприріст: об'єктів +%lu, сторінок +%lu = %.1f МіБ\n",
           dobj, dpg, mib(dpg * PAGE));
    printf("на один запис вийшло %.1f Б при розмірі об'єкта %lu Б\n",
           dobj ? (double)dpg * PAGE / dobj : 0.0, b.objsize);
    return 0;
}
