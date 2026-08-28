static void demo_manual_redirect(void)
{
    banner("close(1) + open: перенаправлення без спеціального виклику");

    fflush(NULL);                  /* буфери батька не повинні поїхати в дитину */
    pid_t pid = fork();
    if (pid < 0) die("fork");

    if (pid == 0) {
        if (close(1) < 0) _exit(10);
        /* найменший вільний тепер 1 — його й забере наступний open */
        int fd = open("fdtour-stdout.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
        if (fd < 0)  _exit(11);
        if (fd != 1) _exit(12);
        printf("цей рядок надруковано звичайним printf\n");
        fflush(stdout);            /* _exit не скидає буферів stdio */
        _exit(0);
    }

    int st;
    if (waitpid(pid, &st, 0) < 0) die("waitpid");
    if (!WIFEXITED(st) || WEXITSTATUS(st) != 0) {
        printf("дитина завершилася з кодом %d\n",
               WIFEXITED(st) ? WEXITSTATUS(st) : -1);
        return;
    }
    printf("а у файлі fdtour-stdout.txt лежить:\n");
    show_file("fdtour-stdout.txt");
}
