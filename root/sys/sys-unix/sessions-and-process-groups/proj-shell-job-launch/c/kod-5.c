static int job_stopped(const struct job *j)
{
    for (int i = 0; i < j->n; i++)
        if (j->st[i] == 's')
            return 1;
    return 0;
}

/* Чекаємо, доки в завданні лишиться бодай один живий процес.
   WUNTRACED — це «повідом і про зупинення, не тільки про смерть».
   Без нього waitpid просто спатиме далі, а завдання вже нікуди не рухається. */
static int wait_job(struct job *j)
{
    for (;;) {
        int running = 0;
        for (int i = 0; i < j->n; i++)
            if (j->st[i] == 'r')
                running++;
        if (running == 0)
            break;

        int status;
        pid_t p = waitpid(-j->pgid, &status, WUNTRACED);
        if (p < 0) {
            if (errno == EINTR)
                continue;
            break;                        /* ECHILD: забирати вже нікого */
        }
        for (int i = 0; i < j->n; i++)
            if (j->pid[i] == p)
                j->st[i] = WIFSTOPPED(status) ? 's' : 'x';
    }
    return job_stopped(j);
}
