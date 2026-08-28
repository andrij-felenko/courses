static int lab_reparent(void)
{
    int printed[2], gate[2];
    pid_t me = getpid(), kid;
    char c, name[64];

    if (pipe(printed) == -1 || pipe(gate) == -1) {
        perror("pipe");
        return 1;
    }

    kid = fork();
    if (kid == -1) {
        perror("fork");
        return 1;
    }

    if (kid == 0) {
        pid_t now;

        close(printed[0]);
        close(gate[1]);            /* писати в gate має ЛИШЕ батько */

        printf("[дитина %d] до: PPID = %d\n", (int) getpid(), (int) getppid());
        if (write(printed[1], "1", 1) != 1)
            _exit(1);

        while (read(gate[0], &c, 1) == -1 && errno == EINTR)
            continue;              /* 0 == EOF: батько закрив свій кінець */

        printf("[дитина %d] EOF уже є, а PPID = %d\n",
               (int) getpid(), (int) getppid());

        now = await_reparent(me, 1000);
        printf("[дитина %d] після: PPID = %d (%s)\n",
               (int) getpid(), (int) now, comm_of(now, name, sizeof name));
        _exit(0);
    }

    close(printed[1]);
    close(gate[0]);
    while (read(printed[0], &c, 1) == -1 && errno == EINTR)
        continue;

    printf("[батько %d] дитина %d надрукувала «до»; виходжу\n",
           (int) me, (int) kid);
    _exit(0);                      /* gate[1] закриється разом із процесом */
}
