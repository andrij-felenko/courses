static void on_child_exit(int ep, int *pidfd, int *state)
{
    siginfo_t info;
    memset(&info, 0, sizeof info);

    int rc = waitid(P_PIDFD, (id_t)*pidfd, &info, WEXITED | WNOHANG);
    if (rc < 0)
        perror("waitid");                          /* ECHILD: прибрали без нас */
    else if (info.si_pid == 0)
        fprintf(stderr, "подія без зміни стану\n"); /* сюди ми потрапити не мали */
    else if (info.si_code == CLD_EXITED)
        fprintf(stderr, "вийшла сама, код %d\n", info.si_status);
    else
        fprintf(stderr, "убита сигналом %d\n", info.si_status);

    epoll_ctl(ep, EPOLL_CTL_DEL, *pidfd, NULL);   /* саме до close() */
    close(*pidfd);
    *pidfd = -1;
    *state = ST_DONE;
}
