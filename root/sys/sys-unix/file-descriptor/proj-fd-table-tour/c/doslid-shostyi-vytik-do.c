static void demo_leak(void)
{
    banner("Витік до EMFILE");

    struct rlimit saved;
    if (getrlimit(RLIMIT_NOFILE, &saved) < 0) die("getrlimit");
    printf("RLIMIT_NOFILE: м'який %llu, жорсткий %llu\n",
           (unsigned long long)saved.rlim_cur,
           (unsigned long long)saved.rlim_max);

    struct rlimit low = saved;
    low.rlim_cur = (saved.rlim_max < 64) ? saved.rlim_max : 64;
    if (setrlimit(RLIMIT_NOFILE, &low) < 0) die("setrlimit");
    printf("тимчасово опустили м'яку межу до %llu\n",
           (unsigned long long)low.rlim_cur);

    int leaked[256];
    int n = 0, last = -1, err = 0;
    while (n < (int)(sizeof leaked / sizeof leaked[0])) {
        int fd = open("/dev/null", O_RDONLY);
        if (fd < 0) { err = errno; break; }
        last = fd;
        leaked[n++] = fd;
    }
    printf("успішних open: %d, останній номер: %d\n", n, last);
    if (err != 0)
        printf("наступний open: %s\n", strerror(err));

    /* Подивитися в /proc/self/fd теж треба чимось. А нічим. */
    printf("подивитися в /proc/self/fd: %d\n", count_fds());

    /* Ось навіщо серверові «запасний» номер: щоб на EMFILE було чим
     * зробити хоч щось — прийняти й одразу закрити з'єднання, написати в лог. */
    if (n > 0 && close(leaked[--n]) < 0) die("close");
    printf("звільнили один номер — записів у таблиці: %d\n", count_fds());

    while (n > 0)
        if (close(leaked[--n]) < 0) die("close");
    if (setrlimit(RLIMIT_NOFILE, &saved) < 0) die("setrlimit назад");
}
