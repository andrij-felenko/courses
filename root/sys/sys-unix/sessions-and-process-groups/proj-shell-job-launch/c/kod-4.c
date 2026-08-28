static void child_prepare(pid_t pgid)
{
    setpgid(0, pgid);           /* pgid == 0 → «стань лідером власної групи» */

    /* Знехтуваний сигнал ЛИШАЄТЬСЯ знехтуваним після exec. Не скинемо —
       і запущена програма не відреагує ні на Ctrl+C, ні на Ctrl+Z. */
    signal(SIGINT,  SIG_DFL);
    signal(SIGQUIT, SIG_DFL);
    signal(SIGTSTP, SIG_DFL);
    signal(SIGTTIN, SIG_DFL);
    signal(SIGTTOU, SIG_DFL);

    sigset_t empty;             /* маска теж переживає exec */
    sigemptyset(&empty);
    sigprocmask(SIG_SETMASK, &empty, NULL);
}
