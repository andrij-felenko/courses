static void demo_exec(const char *child)
{
    banner("fork + dup2 + exec: перенаправлення руками");

    int out = open("fdtour-exec.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (out < 0) die("open fdtour-exec.txt");
    int plain = open("/dev/null", O_RDONLY);               /* має пережити exec */
    if (plain < 0) die("open /dev/null");
    int sealed = open("/dev/null", O_RDONLY | O_CLOEXEC);  /* не має пережити */
    if (sealed < 0) die("open /dev/null");
    printf("готуємо: out=%d  plain=%d  sealed=%d\n", out, plain, sealed);

    char a[16], b[16];
    snprintf(a, sizeof a, "%d", plain);
    snprintf(b, sizeof b, "%d", sealed);

    fflush(NULL);
    pid_t pid = fork();
    if (pid < 0) die("fork");
    if (pid == 0) {
        if (dup2(out, 1) < 0) _exit(20);  /* номер 1 → той самий опис, що й out */
        if (close(out) < 0)   _exit(21);  /* саме число out більше не потрібне */
        execl(child, child, a, b, (char *)NULL);
        fprintf(stderr, "!! execl %s: %s\n", child, strerror(errno));
        _exit(127);                       /* сюди доходимо лише при невдачі exec */
    }

    int st;
    if (waitpid(pid, &st, 0) < 0) die("waitpid");
    printf("у fdtour-exec.txt (тобто в stdout нащадка):\n");
    show_file("fdtour-exec.txt");

    /* out теж треба закрити: копія в нащадкові вже своя, а наш номер
     * інакше витече й зсуне всі номери в наступних дослідах. */
    if (close(out) < 0 || close(plain) < 0 || close(sealed) < 0) die("close");
}
