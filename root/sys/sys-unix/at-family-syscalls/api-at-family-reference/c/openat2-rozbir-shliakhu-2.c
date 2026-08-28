/* 1 — виклик є і цей набір RESOLVE_* ядру відомий; 0 — ні */
static int openat2_supports(unsigned long long resolve)
{
    struct open_how how;
    memset(&how, 0, sizeof how);              /* усі байти нулі — обов'язково */
    how.flags   = O_RDONLY | O_CLOEXEC | O_DIRECTORY;
    how.resolve = resolve;

    long fd = syscall(SYS_openat2, AT_FDCWD, ".", &how, sizeof how);
    if (fd < 0)
        return 0;                             /* ENOSYS — ядро старше за 5.6;
                                                 EINVAL — прапорця не знає */
    close((int)fd);
    return 1;
}
