static void proc_report(pid_t pid);   /* тіло — нижче */

static int lab_one(void)
{
    pid_t child = fork();
    if (child < 0) { perror("fork"); return 1; }
    if (child == 0)
        _exit(3);            /* саме _exit: буфери stdio успадковані, вони батькові */

    wait_until_zombie(child);
    printf("дитина %d: стан %c\n", (int)child, proc_state(child));

    if (kill(child, SIGKILL) == 0)
        printf("kill(SIGKILL) повернув 0 — стан лишився %c\n", proc_state(child));
    if (kill(child, 0) == 0)
        printf("kill(pid, 0) повернув 0 — номер зайнятий, права є\n");

    proc_report(child);

    int status = 0;
    pid_t got = waitpid(child, &status, 0);
    printf("waitpid → %d, вийшла сама: %d, код %d\n",
           (int)got, WIFEXITED(status), WEXITSTATUS(status));
    printf("після wait: запис у /proc %s\n",
           proc_state(child) ? "ще є" : "зник");
    return 0;
}
