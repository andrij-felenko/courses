static unsigned long raise_nofile(void)     /* м'яку межу піднімаємо до жорсткої */
{
    struct rlimit rl;
    if (getrlimit(RLIMIT_NOFILE, &rl) != 0) return 1024;
    rl.rlim_cur = rl.rlim_max;
    setrlimit(RLIMIT_NOFILE, &rl);
    if (getrlimit(RLIMIT_NOFILE, &rl) != 0) return 1024;
    if (rl.rlim_cur == RLIM_INFINITY || rl.rlim_cur > 262144) return 262144;
    return (unsigned long)rl.rlim_cur;
}

static int cmd_scatter(const char *dir, unsigned long neg, unsigned long pins)
{
    int dfd = open(dir, O_RDONLY | O_DIRECTORY);
    if (dfd < 0) { fprintf(stderr, "%s: %s\n", dir, strerror(errno)); return 1; }

    unsigned long cap = raise_nofile();
    if (pins + 64 > cap) pins = cap > 64 ? cap - 64 : 0;
    if (!pins || !neg) { fprintf(stderr, "обидва числа мають бути > 0\n"); return 1; }

    int *fds = calloc(pins, sizeof *fds);
    if (!fds) return 1;

    struct cache a = snapshot("до", "dentry");

    unsigned long step = neg / pins ? neg / pins : 1;   /* через скільки промахів */
    unsigned long got = 0;
    char nm[64];
    struct stat st;
    for (unsigned long i = 0; i < neg; i++) {
        snprintf(nm, sizeof nm, "nx-%ld-%lu", (long)getpid(), i);
        (void)fstatat(dfd, nm, &st, AT_SYMLINK_NOFOLLOW);      /* завжди ENOENT */
        if (i % step == 0 && got < pins) {
            snprintf(nm, sizeof nm, "pin-%ld-%lu", (long)getpid(), got);
            int fd = openat(dfd, nm, O_CREAT | O_RDONLY, 0600);
            if (fd >= 0) fds[got++] = fd;
            else pins = got;              /* дескрипторів більше не дадуть */
        }
    }

    struct cache b = snapshot("виросло", "dentry");
    unsigned long dobj  = sub(b.active_objs, a.active_objs);
    unsigned long dslab = sub(b.num_slabs, a.num_slabs);
    printf("\nстворено: %lu негативних записів + %lu відкритих файлів"
           " (закріп кожен %lu-й)\n", neg, got, step);
    printf("приріст dentry: об'єктів +%lu, слабів +%lu = %.1f МіБ\n",
           dobj, dslab, mib(dslab * b.pagesperslab * PAGE));

    if (drop_slab() == 0) {
        struct cache c = snapshot("після скидання", "dentry");
        unsigned long robj  = sub(c.active_objs, a.active_objs);
        unsigned long rslab = sub(c.num_slabs, a.num_slabs);
        printf("лишилось: об'єктів +%lu, слабів +%lu = %.1f МіБ\n",
               robj, rslab, mib(rslab * c.pagesperslab * PAGE));

        double pf = dobj ? (double)got / dobj : 0.0;
        double expect = dslab * (1.0 - pow(1.0 - pf, (double)b.objperslab));
        unsigned long ideal = (got + b.objperslab - 1) / b.objperslab;
        printf("\nочікувано за розсіянням: %.0f слабів"
               " (частка закріплених %.4f, слотів у слабі %lu)\n",
               expect, pf, b.objperslab);
        printf("щільно ті самі об'єкти зайняли б слабів: %lu"
               " — розсіяння коштує %.1f×\n",
               ideal, ideal ? (double)rslab / ideal : 0.0);
    }

    for (unsigned long k = 0; k < got; k++) close(fds[k]);
    for (unsigned long k = 0; k < got; k++) {
        snprintf(nm, sizeof nm, "pin-%ld-%lu", (long)getpid(), k);
        unlinkat(dfd, nm, 0);
    }
    free(fds);
    if (drop_slab() == 0) {
        struct cache d = snapshot("після прибирання", "dentry");
        printf("лишилось: об'єктів +%lu, слабів +%lu = %.1f МіБ\n",
               sub(d.active_objs, a.active_objs), sub(d.num_slabs, a.num_slabs),
               mib(sub(d.num_slabs, a.num_slabs) * d.pagesperslab * PAGE));
    }
    close(dfd);
    return 0;
}
