ssize_t write_all(int fd, const void *buf, size_t len) {
    const char *p = buf;
    size_t left = len;
    while (left > 0) {
        ssize_t n = write(fd, p, left);
        if (n < 0) {
            if (errno == EINTR) continue;   /* перервали — просто ще раз */
            return -1;                      /* справжня помилка */
        }
        p += n;                             /* віддали менше, ніж просили */
        left -= (size_t) n;
    }
    return (ssize_t) len;
}
