struct duplex { int tx, rx; };

static int xfer_send(int fd, const void *buf, size_t n)
{
        const char *p = buf;
        while (n) {
                ssize_t k = write(fd, p, n);
                if (k < 0) { if (errno == EINTR) continue; return -1; }
                p += k; n -= (size_t)k;
        }
        return 0;
}

static int xfer_recv(int fd, void *buf, size_t n)
{
        char *p = buf;
        while (n) {
                ssize_t k = read(fd, p, n);
                if (k <= 0) { if (k < 0 && errno == EINTR) continue; return -1; }
                p += k; n -= (size_t)k;
        }
        return 0;
}
