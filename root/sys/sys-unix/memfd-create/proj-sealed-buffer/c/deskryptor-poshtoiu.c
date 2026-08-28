static int send_fd(int sock, int fd)
{
    char byte = 'F';                       /* хоч один байт звичайних даних */
    struct iovec iov = { .iov_base = &byte, .iov_len = 1 };
    union {                                /* вирівнювання під cmsghdr */
        char buf[CMSG_SPACE(sizeof(int))];
        struct cmsghdr align;
    } u = { 0 };
    struct msghdr msg = {
        .msg_iov = &iov, .msg_iovlen = 1,
        .msg_control = u.buf, .msg_controllen = sizeof u.buf,
    };

    struct cmsghdr *cm = CMSG_FIRSTHDR(&msg);
    cm->cmsg_level = SOL_SOCKET;
    cm->cmsg_type  = SCM_RIGHTS;
    cm->cmsg_len   = CMSG_LEN(sizeof(int));
    memcpy(CMSG_DATA(cm), &fd, sizeof fd);

    return sendmsg(sock, &msg, 0) == 1 ? 0 : -1;
}

static int recv_fd(int sock)
{
    char byte;
    struct iovec iov = { .iov_base = &byte, .iov_len = 1 };
    union {
        char buf[CMSG_SPACE(sizeof(int))];
        struct cmsghdr align;
    } u = { 0 };
    struct msghdr msg = {
        .msg_iov = &iov, .msg_iovlen = 1,
        .msg_control = u.buf, .msg_controllen = sizeof u.buf,
    };

    if (recvmsg(sock, &msg, MSG_CMSG_CLOEXEC) != 1) return -1;
    if (msg.msg_flags & MSG_CTRUNC) return -1;      /* не все влізло */

    struct cmsghdr *cm = CMSG_FIRSTHDR(&msg);
    if (!cm || cm->cmsg_len != CMSG_LEN(sizeof(int))
            || cm->cmsg_level != SOL_SOCKET || cm->cmsg_type != SCM_RIGHTS)
        return -1;                                  /* дескриптора не прислали */

    int fd;
    memcpy(&fd, CMSG_DATA(cm), sizeof fd);
    return fd;
}
