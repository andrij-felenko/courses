/* Віддати термінал групі pgid і, якщо треба, поставити її режим термінала.
   Блокуємо на ВЕСЬ виклик: щойно tcsetpgrp переведе покажчик на іншу групу,
   ми вже фонові — і наступний же tcsetattr зупинив би нас самих. */
static void give_terminal(pid_t pgid, const struct termios *modes)
{
    sigset_t block, old;
    sigemptyset(&block);
    sigaddset(&block, SIGTTOU);
    sigprocmask(SIG_BLOCK, &block, &old);

    if (tcsetpgrp(tty, pgid) < 0)
        perror("tcsetpgrp");
    if (modes)
        tcsetattr(tty, TCSADRAIN, modes);

    sigprocmask(SIG_SETMASK, &old, NULL);
}

/* Забрати термінал собі. Тут оболонка фонова ВЖЕ на першому рядку. */
static void take_terminal(struct job *j, int save_modes)
{
    sigset_t block, old;
    sigemptyset(&block);
    sigaddset(&block, SIGTTOU);
    sigprocmask(SIG_BLOCK, &block, &old);

    if (save_modes)
        tcgetattr(tty, &j->tmodes);       /* завдання ще житиме — зберігаємо його режим */
    tcsetpgrp(tty, shell_pgid);
    tcsetattr(tty, TCSADRAIN, &shell_tmodes);

    sigprocmask(SIG_SETMASK, &old, NULL);
}
