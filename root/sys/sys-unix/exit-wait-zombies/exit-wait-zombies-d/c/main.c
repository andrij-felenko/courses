int status;
pid_t pid = waitpid(child, &status, WUNTRACED);
if (pid < 0) { perror("waitpid"); return 1; }

if (WIFEXITED(status)) {
    printf("вийшов сам, код %d\n", WEXITSTATUS(status));
} else if (WIFSIGNALED(status)) {
    printf("убито сигналом %d%s\n", WTERMSIG(status),
           WCOREDUMP(status) ? " (з дампом)" : "");
} else if (WIFSTOPPED(status)) {
    printf("зупинено сигналом %d\n", WSTOPSIG(status));
}
