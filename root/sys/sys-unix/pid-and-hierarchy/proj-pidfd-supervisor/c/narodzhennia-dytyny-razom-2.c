/* Повертає pidfd. Номер потрібен тільки для журналу — діяти ним ми не будемо. */
static int spawn(char *const argv[], pid_t *pid_out)
{
    int pidfd = -1;
    struct clone_args a;
    memset(&a, 0, sizeof a);
    a.flags       = CLONE_PIDFD;
    a.pidfd       = (uint64_t)(uintptr_t)&pidfd;
    a.exit_signal = SIGCHLD;      /* інакше waitid() вимагав би __WALL */

    long rc = sys_clone3(&a, sizeof a);
    if (rc == 0) {                       /* ми — дитина */
        signal(SIGPIPE, SIG_DFL);        /* SIG_IGN переживає exec, скидаємо */
        setpgid(0, 0);                   /* власна група процесів */
        execvp(argv[0], argv);
        _exit(127);
    }
    if (rc > 0) { *pid_out = (pid_t)rc; return pidfd; }
    if (errno != ENOSYS) return -1;      /* справжня біда, а не старе ядро */

    /* Запасний шлях для ядер до 5.3: спершу народити, потім узяти посилання. */
    pid_t p = fork();
    if (p == 0) {
        signal(SIGPIPE, SIG_DFL);
        setpgid(0, 0);
        execvp(argv[0], argv);
        _exit(127);
    }
    if (p < 0) return -1;
    *pid_out = p;
    return sys_pidfd_open(p, 0);
}
