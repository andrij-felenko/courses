int main(void)
{
    setvbuf(stdout, NULL, _IOLBF, 0);       /* щоб fork не подвоїв буфер виводу */

    int sv[2];
    if (socketpair(AF_UNIX, SOCK_STREAM, 0, sv) < 0) die("socketpair");

    pid_t pid = fork();
    if (pid < 0) die("fork");

    if (pid == 0) {                                    /* ─── дитина ─── */
        close(sv[0]);
        int fd = recv_fd(sv[1]);
        if (fd < 0) die("recv_fd");

        printf("дитина: номер %d, позиція %lld\n",
               fd, (long long)lseek(fd, 0, SEEK_CUR));
        if (write(fd, "bbbb", 4) != 4) die("write");

        close(fd);
        if (write(sv[1], "!", 1) != 1) die("ack");     /* «я дописала» */
        _exit(0);
    }

    close(sv[1]);                                      /* ─── батько ─── */
    int fd = open("/tmp/scm-demo.txt", O_RDWR | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) die("open");
    if (write(fd, "aaaa", 4) != 4) die("write");
    printf("батько: номер %d, позиція %lld\n",
           fd, (long long)lseek(fd, 0, SEEK_CUR));

    if (send_fd(sv[0], fd) < 0) die("send_fd");

    char ack;
    if (read(sv[0], &ack, 1) != 1) die("read");        /* чекаємо на дитину */
    printf("батько після дитини: позиція %lld\n",
           (long long)lseek(fd, 0, SEEK_CUR));
    if (write(fd, "cccc", 4) != 4) die("write");

    close(fd);
    close(sv[0]);
    wait(NULL);
    return 0;
}
