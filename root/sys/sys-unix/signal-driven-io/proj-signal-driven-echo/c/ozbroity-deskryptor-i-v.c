static int sig_ready;                 /* SIGRTMIN + 1, рахується в main */

static void arm(int fd)
{
    struct f_owner_ex own = {
        .type = F_OWNER_TID,
        .pid  = (pid_t) syscall(SYS_gettid)
    };

    if (fcntl(fd, F_SETOWN_EX, &own) < 0) die("F_SETOWN_EX");
    if (fcntl(fd, F_SETSIG, sig_ready) < 0) die("F_SETSIG");

    int fl = fcntl(fd, F_GETFL, 0);                       /* забрати старі прапорці */
    if (fl < 0 || fcntl(fd, F_SETFL, fl | O_ASYNC | O_NONBLOCK) < 0)
        die("F_SETFL");
}
