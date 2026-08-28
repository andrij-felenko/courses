/* Приймає один дескриптор; усе зайве закриває, щоб нічого не зависло. */
static int recv_fd(int sock)
{
    char byte;
    struct iovec iov = { .iov_base = &byte, .iov_len = 1 };

    union {
        char buf[CMSG_SPACE(sizeof(int))];
        struct cmsghdr align;
    } u;

    struct msghdr msg = {
        .msg_iov        = &iov,
        .msg_iovlen     = 1,
        .msg_control    = u.buf,
        .msg_controllen = sizeof(u.buf),
    };

    ssize_t n;
    do {
        n = recvmsg(sock, &msg, MSG_CMSG_CLOEXEC);
    } while (n < 0 && errno == EINTR);
    if (n <= 0) return -1;                  /* 0 — інший кінець закрито */

    int fd = -1;
    for (struct cmsghdr *cm = CMSG_FIRSTHDR(&msg); cm; cm = CMSG_NXTHDR(&msg, cm)) {
        if (cm->cmsg_level != SOL_SOCKET || cm->cmsg_type != SCM_RIGHTS)
            continue;
        unsigned count = (cm->cmsg_len - CMSG_LEN(0)) / sizeof(int);
        for (unsigned i = 0; i < count; i++) {
            int got;
            memcpy(&got, CMSG_DATA(cm) + i * sizeof(int), sizeof(int));
            if (fd < 0) fd = got;           /* перший лишаємо собі */
            else close(got);                /* решту не тримаємо */
        }
    }

    if (msg.msg_flags & MSG_CTRUNC) {       /* надлишок ядро закрило само */
        if (fd >= 0) close(fd);
        errno = EMSGSIZE;
        return -1;
    }
    if (fd < 0) errno = ENOENT;             /* дані прийшли, дескриптора немає */
    return fd;
}
