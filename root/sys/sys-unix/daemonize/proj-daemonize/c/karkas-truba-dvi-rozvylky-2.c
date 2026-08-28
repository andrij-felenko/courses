int daemonize(const char *pidpath)
{
    int p[2];
    if (pipe(p) < 0) return -1;            /* ДО першого розділення */

    pid_t pid = fork();
    if (pid < 0) { int e = errno; close(p[0]); close(p[1]); errno = e; return -1; }

    if (pid > 0) {                         /* A: пускач */
        close(p[1]);                       /* ← без цього рядка він чекатиме вічно */
        parent_wait_and_exit(p[0], pid);   /* не повертається */
    }

    /* B: майбутній лідер сеансу */
    close(p[0]);
    ready_fd = p[1];
    fcntl(ready_fd, F_SETFD, FD_CLOEXEC);  /* щоб не протік у чужий образ */

    if (setsid() < 0)  { report('E', errno, "setsid"); _exit(1); }

    pid = fork();                          /* друге розділення */
    if (pid < 0)       { report('E', errno, "fork2");  _exit(1); }
    if (pid > 0) _exit(0);                 /* B іде; його копію труби закриє ядро */

    /* C: власне демон */
    if (chdir("/") < 0) { report('E', errno, "chdir"); _exit(1); }
    umask(0027);                           /* обрано, а не успадковано */

    if (close_inherited_fds(ready_fd) < 0) { report('E', errno, "close-fds"); _exit(1); }
    if (attach_dev_null() < 0)             { report('E', errno, "dev-null");  _exit(1); }
    if (reset_signals() < 0)               { report('E', errno, "signals");   _exit(1); }

    if (pidpath && claim_pidfile(pidpath) < 0) { report('E', errno, "pidfile"); _exit(1); }

    return 0;                              /* далі — справжня ініціалізація */
}
