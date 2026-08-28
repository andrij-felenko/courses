/* Підняти значення може будь-хто; ЗНИЗИТИ — лише з CAP_SYS_RESOURCE. */
static void set_adj(int adj)
{
    char buf[16];
    int n = snprintf(buf, sizeof buf, "%d\n", adj);
    int fd = open("/proc/self/oom_score_adj", O_WRONLY | O_CLOEXEC);
    if (fd < 0) { perror("open oom_score_adj"); return; }
    if (write(fd, buf, (size_t) n) != n) perror("write oom_score_adj");
    close(fd);
}
