int main(void)
{
    int sv[2];
    if (socketpair(AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC, 0, sv) != 0)
        die("socketpair");

    pid_t pid = fork();
    if (pid < 0) die("fork");

    if (pid == 0) {              /* робітник */
        close(sv[0]);
        cage(WORKER_UID, WORKER_GID);
        worker(sv[1]);
        _exit(0);
    }

    close(sv[1]);                /* монітор не тримає кінця робітника */
    monitor(sv[0]);              /* ЛИШЕ ТУТ уперше торкаємося таємниць */
    int st;
    waitpid(pid, &st, 0);
    return 0;
}
