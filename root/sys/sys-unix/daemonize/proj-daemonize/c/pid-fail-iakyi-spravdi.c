static int claim_pidfile(const char *path)
{
    int fd = open(path, O_RDWR | O_CREAT | O_CLOEXEC, 0644);
    if (fd < 0) return -1;

    /* Ось тут і вирішується, чи ми єдиний примірник. */
    if (flock(fd, LOCK_EX | LOCK_NB) < 0) {      /* EWOULDBLOCK — хтось уже живий */
        int e = errno; close(fd); errno = e; return -1;
    }

    if (ftruncate(fd, 0) < 0) goto fail;         /* старе число могло бути довшим */

    char buf[32];
    int n = snprintf(buf, sizeof buf, "%ld\n", (long)getpid());
    if (write(fd, buf, (size_t)n) != n) goto fail;

    pidfile_fd = fd;      /* ⚠️ дескриптор лишається відкритим НАЗАВЖДИ */
    return 0;

fail: {
    int e = errno; close(fd); errno = e; return -1;
    }
}
