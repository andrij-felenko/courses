static void proc_faults(unsigned long &minf, unsigned long &majf) {
    minf = majf = 0;
    int fd = open("/proc/self/stat", O_RDONLY);
    if (fd < 0) return;
    char buf[1024];
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    close(fd);
    if (n <= 0) return;
    buf[n] = '\0';

    char *p = strrchr(buf, ')');
    if (!p) return;
    sscanf(p + 2, "%*c %*d %*d %*d %*d %*d %*u %lu %*lu %lu", &minf, &majf);
}
