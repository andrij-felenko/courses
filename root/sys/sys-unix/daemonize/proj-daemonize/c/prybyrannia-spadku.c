#if defined(__linux__) && defined(SYS_close_range)
static int try_close_range(unsigned lo, unsigned hi)
{
    return (int)syscall(SYS_close_range, lo, hi, 0u);
}
#else
static int try_close_range(unsigned lo, unsigned hi)
{ (void)lo; (void)hi; errno = ENOSYS; return -1; }
#endif

/* Обхід /proc/self/fd — точний список, без вгадування стелі. */
static void close_fds_via_proc(int lo, int keep)
{
    DIR *d = opendir("/proc/self/fd");
    if (!d) {                                  /* немає /proc — лишається вгадувати */
        long max = sysconf(_SC_OPEN_MAX);
        if (max < 0 || max > 65536) max = 65536;
        for (int fd = lo; fd < (int)max; fd++)
            if (fd != keep) (void)close(fd);
        return;
    }
    int dfd = dirfd(d);                         /* його закривати не можна: ще читаємо */
    struct dirent *e;
    while ((e = readdir(d)) != NULL) {
        char *end;
        long fd = strtol(e->d_name, &end, 10);
        if (*end != '\0') continue;             /* «.» і «..» */
        if (fd < lo || fd == dfd || fd == keep) continue;
        (void)close((int)fd);
    }
    closedir(d);
}

/* Дірка на keep — інакше ми закриємо власну трубу готовності. */
static int close_inherited_fds(int keep)
{
    if (keep < 3) { errno = EINVAL; return -1; }

    if (keep > 3 && try_close_range(3u, (unsigned)keep - 1) < 0) goto fallback;
    if (try_close_range((unsigned)keep + 1, ~0u) < 0)            goto fallback;
    return 0;

fallback:
    if (errno != ENOSYS && errno != EPERM && errno != EINVAL) return -1;
    close_fds_via_proc(3, keep);
    return 0;
}
