static int write_full(int fd, const uint8_t *buf, size_t n) {
    size_t done = 0;
    while (done < n) {
        ssize_t k = write(fd, buf + done, n - done);
        if (k < 0) { if (errno == EINTR) continue; return -1; }
        done += (size_t)k;
    }
    return 0;
}

/* повертає, скільки байтів реально прочитано (менше n — кінець файлу) */
static ssize_t read_full(int fd, uint8_t *buf, size_t n) {
    size_t done = 0;
    while (done < n) {
        ssize_t k = read(fd, buf + done, n - done);
        if (k < 0) { if (errno == EINTR) continue; return -1; }
        if (k == 0) break;
        done += (size_t)k;
    }
    return (ssize_t)done;
}
