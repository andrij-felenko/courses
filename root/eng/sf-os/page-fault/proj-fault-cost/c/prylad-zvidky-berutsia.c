/* Ті самі два числа, але видимі ззовні: поля 10 і 12 у /proc/self/stat.
   Починаємо від ОСТАННЬОЇ ')' — усе, що лівіше, це pid та ім'я. */
static void proc_faults(unsigned long *minf, unsigned long *majf)
{
    char buf[1024];
    int fd = open("/proc/self/stat", O_RDONLY);
    if (fd < 0) { *minf = *majf = 0; return; }
    ssize_t n = read(fd, buf, sizeof buf - 1);
    close(fd);
    buf[n > 0 ? n : 0] = '\0';

    char *p = strrchr(buf, ')');
    if (!p) { *minf = *majf = 0; return; }
    /*     state ppid pgrp session tty tpgid flags minflt cminflt majflt */
    sscanf(p + 2, "%*c %*d %*d %*d %*d %*d %*u %lu %*lu %lu", minf, majf);
}
