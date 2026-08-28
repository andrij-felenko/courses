/* дескриптор, або -1 з причиною в errno */
static int open_beneath(int dirfd, const char *path)
{
    struct open_how how;
    memset(&how, 0, sizeof how);
    how.flags   = O_RDONLY | O_CLOEXEC;
    how.resolve = RESOLVE_BENEATH | RESOLVE_NO_SYMLINKS;

    for (int tries = 0; tries < 8; tries++) {
        long fd = syscall(SYS_openat2, dirfd, path, &how, sizeof how);
        if (fd >= 0)
            return (int)fd;
        if (errno != EAGAIN)                  /* EXDEV чи ELOOP — шлях назовні,
                                                 ENOSYS чи EINVAL — ядро старе */
            return -1;
    }
    errno = EAGAIN;                           /* дерево не вгамувалося */
    return -1;
}
