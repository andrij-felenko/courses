static int attach_dev_null(void)
{
    int fd = open("/dev/null", O_RDWR);
    if (fd < 0) return -1;

    if (dup2(fd, STDIN_FILENO)  < 0) return -1;
    if (dup2(fd, STDOUT_FILENO) < 0) return -1;
    if (dup2(fd, STDERR_FILENO) < 0) return -1;   /* dup2 сам закриє старе */

    if (fd > STDERR_FILENO) close(fd);
    return 0;
}
