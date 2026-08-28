static int send_resp(int sock, uint32_t status, int fd)
{
    struct resp rs = { .status = status };
    struct iovec iov = { .iov_base = &rs, .iov_len = sizeof rs };
    union { char b[CMSG_SPACE(sizeof(int))]; struct cmsghdr align; } cm;
    struct msghdr msg = { .msg_iov = &iov, .msg_iovlen = 1 };

    if (fd >= 0) {
        memset(cm.b, 0, sizeof cm.b);
        msg.msg_control    = cm.b;
        msg.msg_controllen = sizeof cm.b;            /* SPACE — з вирівнюванням */
        struct cmsghdr *c = CMSG_FIRSTHDR(&msg);
        c->cmsg_level = SOL_SOCKET;
        c->cmsg_type  = SCM_RIGHTS;
        c->cmsg_len   = CMSG_LEN(sizeof(int));       /* LEN — без вирівнювання */
        memcpy(CMSG_DATA(c), &fd, sizeof fd);
    }
    ssize_t n;
    do { n = sendmsg(sock, &msg, MSG_NOSIGNAL); } while (n < 0 && errno == EINTR);
    return n == (ssize_t)sizeof rs ? 0 : -1;
}

static int recv_resp(int sock, struct resp *rs, int *fd)
{
    *fd = -1;
    struct iovec iov = { .iov_base = rs, .iov_len = sizeof *rs };
    union { char b[CMSG_SPACE(sizeof(int))]; struct cmsghdr align; } cm;
    struct msghdr msg = { .msg_iov = &iov, .msg_iovlen = 1,
                          .msg_control = cm.b, .msg_controllen = sizeof cm.b };
    ssize_t n;
    do { n = recvmsg(sock, &msg, MSG_CMSG_CLOEXEC); } while (n < 0 && errno == EINTR);

    if (n != (ssize_t)sizeof *rs) return -1;         /* 0 = монітор пішов */
    if (msg.msg_flags & (MSG_TRUNC | MSG_CTRUNC)) return -1;

    for (struct cmsghdr *c = CMSG_FIRSTHDR(&msg); c; c = CMSG_NXTHDR(&msg, c)) {
        if (c->cmsg_level != SOL_SOCKET || c->cmsg_type != SCM_RIGHTS) return -1;
        if (c->cmsg_len != CMSG_LEN(sizeof(int)))    return -1;   /* рівно один */
        memcpy(fd, CMSG_DATA(c), sizeof *fd);
    }
    return 0;
}
