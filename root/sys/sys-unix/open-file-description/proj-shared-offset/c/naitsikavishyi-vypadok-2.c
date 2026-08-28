static void case_scm(void)
{
    int sv[2];
    if (socketpair(AF_UNIX, SOCK_STREAM, 0, sv)) { perror("socketpair"); exit(1); }

    int fd = fresh(0);
    write(fd, "AAAAA", 5);
    fflush(NULL);

    pid_t kid = fork();
    if (kid == 0) {
        close(sv[0]);
        close(fd);                            /* рвемо спадок від батька */
        int got = recv_fd(sv[1]);
        write(got, "BBBBB", 5);
        (void)!write(sv[1], &got, sizeof got); /* кажу батькові свій номер */
        char c; (void)!read(sv[1], &c, 1);     /* чекаю, доки зміряють */
        _exit(0);
    }
    close(sv[1]);
    send_fd(sv[0], fd);

    int kid_fd = -1;
    (void)!read(sv[0], &kid_fd, sizeof kid_fd);

    witness("SCM_RIGHTS", getpid(), fd, kid, kid_fd);

    close(sv[0]);                             /* дитина побачить кінець потоку */
    waitpid(kid, NULL, 0);
    close(fd);
}
