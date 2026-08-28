static pid_t spawn(char **argv, int in_fd, int out_fd, int foreign_fd)
{
    pid_t pid = fork();
    if (pid != 0)
        return pid;                              /* батько; −1 розбере той, хто кликав */

    /* Далі тільки дитина. Виходимо через _exit, а не exit: exit злив би буфери
       stdio, успадковані від батька, і той самий текст надрукувався б удруге. */
    close(foreign_fd);                           /* close №3 і №4 */
    if (in_fd  >= 0 && move_to(in_fd,  STDIN_FILENO)  < 0) _exit(126);
    if (out_fd >= 0 && move_to(out_fd, STDOUT_FILENO) < 0) _exit(126);

    execvp(argv[0], argv);
    dprintf(STDERR_FILENO, "mypipe: %s: %s\n", argv[0], strerror(errno));
    _exit(127);   /* коди за угодою оболонок: 126 — не вдалося виконати,
                     127 — не вдалося знайти чи запустити команду взагалі */
}
