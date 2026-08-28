int main(int argc, char **argv)
{
    int sep = 0;
    for (int i = 1; i < argc; i++)
        if (strcmp(argv[i], ":") == 0) { sep = i; break; }
    if (sep < 2 || sep == argc - 1) {
        dprintf(STDERR_FILENO, "вжиток: %s ланка [арг…] : ланка [арг…]\n", argv[0]);
        return 2;
    }
    argv[sep] = NULL;                            /* два окремі масиви argv в одному */
    char **left = &argv[1], **right = &argv[sep + 1];

    int pfd[2];
    if (pipe2(pfd, O_CLOEXEC) < 0) { perror("pipe2"); return 1; }

    pid_t p1 = spawn(left,  -1, pfd[1], pfd[0]);   /* пише в канал */
    if (p1 < 0) { perror("fork"); return 1; }
    pid_t p2 = spawn(right, pfd[0], -1, pfd[1]);   /* читає з каналу */
    if (p2 < 0) { perror("fork"); return 1; }

    /* Найважливіші два рядки в усій програмі: close №5 і №6.
       Без другого з них лічильник кінців на запис ніколи не дійде до нуля. */
    close(pfd[0]);
    close(pfd[1]);

    int status = 0, last = 0;
    for (int alive = 2; alive > 0; ) {
        pid_t done = waitpid(-1, &status, 0);
        if (done < 0) { if (errno == EINTR) continue; perror("waitpid"); return 1; }
        if (done == p2) last = status;           /* код виходу — від ОСТАННЬОЇ ланки */
        alive--;
    }

    if (WIFEXITED(last))   return WEXITSTATUS(last);
    if (WIFSIGNALED(last)) return 128 + WTERMSIG(last);
    return 1;
}
