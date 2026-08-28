static void shell_init(void)
{
    tty = STDIN_FILENO;
    if (!isatty(tty)) {
        fputs("mysh: вхід — не термінал\n", stderr);
        exit(1);
    }

    /* Нас могли запустити у фоні. Доки термінал не наш, зупиняємо себе самі —
       і цей цикл мусить стояти ДО того, як ми почнемо нехтувати SIGTTIN,
       інакше він крутитиметься вічно. */
    while (tcgetpgrp(tty) != (shell_pgid = getpgrp()))
        kill(-shell_pgid, SIGTTIN);

    signal(SIGINT,  SIG_IGN);   /* Ctrl+C на промпті не має вбивати оболонку */
    signal(SIGQUIT, SIG_IGN);
    signal(SIGTSTP, SIG_IGN);   /* і Ctrl+Z не має її зупиняти */
    signal(SIGTTIN, SIG_IGN);

    shell_pgid = getpid();
    setpgid(shell_pgid, shell_pgid);   /* оболонка — сама собі завдання */
    give_terminal(shell_pgid, NULL);   /* після setpgid ми вже фонові: блокування потрібне */
    tcgetattr(tty, &shell_tmodes);     /* еталон, до якого повертатимемо термінал */
}
