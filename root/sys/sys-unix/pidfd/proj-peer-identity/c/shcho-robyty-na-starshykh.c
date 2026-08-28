/* Ядро 6.5…6.12: дескриптор є, ioctl немає. */
static int proc_dir_of(int pidfd)
{
    struct pollfd pfd = { .fd = pidfd, .events = POLLIN };
    char path[64], line[128];
    int pid = -1, dir;

    if (poll(&pfd, 1, 0) != 0)          /* уже мертвий — далі нема про що */
        return -1;

    snprintf(path, sizeof path, "/proc/self/fdinfo/%d", pidfd);
    FILE *f = fopen(path, "r");
    if (!f) return -1;
    while (fgets(line, sizeof line, f))
        if (sscanf(line, "Pid: %d", &pid) == 1)   /* −1 мертвий, 0 не видно */
            break;
    fclose(f);
    if (pid <= 0) return -1;

    snprintf(path, sizeof path, "/proc/%d", pid);
    dir = open(path, O_DIRECTORY | O_PATH | O_CLOEXEC);
    if (dir < 0) return -1;

    /* Дескриптор стає читабельним, щойно ціль вийшла, — тобто ЩЕ ДО того,
     * як її прибрали й номер міг комусь дістатися. Він і досі мовчить,
     * отже, номер весь цей час належав тому самому процесові,
     * отже, відкритий каталог — його. */
    if (poll(&pfd, 1, 0) != 0) { close(dir); return -1; }
    return dir;
}
