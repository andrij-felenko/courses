static void launch_job(struct job *j, char **cmd[], int n, int foreground)
{
    int in = STDIN_FILENO;

    for (int i = 0; i < n; i++) {
        int pfd[2] = { -1, -1 };
        if (i + 1 < n && pipe(pfd) < 0) { perror("pipe"); return; }

        pid_t pid = fork();
        if (pid == 0) {
            child_prepare(j->pgid);
            if (in != STDIN_FILENO)  { dup2(in, STDIN_FILENO);      close(in);     }
            if (pfd[1] >= 0)         { dup2(pfd[1], STDOUT_FILENO); close(pfd[1]); }
            if (pfd[0] >= 0)           close(pfd[0]);
            execvp(cmd[i][0], cmd[i]);
            dprintf(STDERR_FILENO, "mysh: %s: %s\n", cmd[i][0], strerror(errno));
            _exit(127);
        }
        if (pid < 0) { perror("fork"); return; }

        if (j->pgid == 0)
            j->pgid = pid;      /* перша ланка дає групі ім'я */
        setpgid(pid, j->pgid);  /* те саме ВДРУГЕ, з боку батька; помилку ігноруємо свідомо */
        j->pid[j->n] = pid;
        j->st[j->n++] = 'r';

        if (in != STDIN_FILENO) close(in);
        if (pfd[1] >= 0)        close(pfd[1]);
        in = pfd[0];
    }

    if (!foreground) {
        printf("[1] %d\n", (int)j->pgid);
        return;
    }

    give_terminal(j->pgid, NULL);          /* режиму термінала в завдання ще немає */
    int stopped = wait_job(j);
    take_terminal(j, stopped);
    if (stopped)
        printf("\n[1]+ Зупинено   %s\n", j->cmd);
}
