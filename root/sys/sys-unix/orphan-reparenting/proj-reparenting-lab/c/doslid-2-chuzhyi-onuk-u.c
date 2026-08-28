static int lab_subreaper(void)
{
    pid_t me, mid;
    int isset = -1;

    if (prctl(PR_SET_CHILD_SUBREAPER, 1UL, 0UL, 0UL, 0UL) == -1) {
        perror("PR_SET_CHILD_SUBREAPER");
        return 1;
    }
    prctl(PR_GET_CHILD_SUBREAPER, (unsigned long) &isset, 0UL, 0UL, 0UL);
    me = getpid();
    printf("[lab %d] я прибирач (child_subreaper = %d)\n", (int) me, isset);

    mid = fork();
    if (mid == -1) {
        perror("fork");
        return 1;
    }

    if (mid == 0) {                          /* середній: подвійна вилка */
        pid_t self = getpid();
        pid_t grand = fork();
        int inherited = -1;

        if (grand == -1)
            _exit(127);
        if (grand > 0) {
            prctl(PR_GET_CHILD_SUBREAPER, (unsigned long) &inherited,
                  0UL, 0UL, 0UL);
            printf("[середній %d] мій child_subreaper = %d; онук %d\n",
                   (int) self, inherited, (int) grand);
            msleep(50);                      /* дати онукові надрукувати «до» */
            _exit(3);
        }

        printf("[онук %d] поки що батько = %d\n",
               (int) getpid(), (int) getppid());
        printf("[онук %d] новий батько = %d\n",
               (int) getpid(), (int) await_reparent(self, 1000));
        msleep(200);
        _exit(42);
    }

    printf("[lab %d] я створив рівно один процес: %d\n", (int) me, (int) mid);

    for (;;) {
        int st;
        pid_t got = waitpid(-1, &st, 0);

        if (got == -1) {
            if (errno == EINTR)
                continue;
            if (errno == ECHILD)
                break;
            perror("waitpid");
            return 1;
        }
        printf("[lab %d] wait: %d, код %d — %s\n", (int) me, (int) got,
               WIFEXITED(st) ? WEXITSTATUS(st) : -1,
               got == mid ? "мій" : "ЧУЖИЙ, я його не створював");
    }
    printf("[lab %d] дітей більше нема (ECHILD)\n", (int) me);
    return 0;
}
