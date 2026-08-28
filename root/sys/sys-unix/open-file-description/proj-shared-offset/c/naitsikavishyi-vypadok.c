static int send_fd(int sock, int fd)
{
    char one = 'x';
    struct iovec io = { .iov_base = &one, .iov_len = 1 };
    union { char buf[CMSG_SPACE(sizeof(int))]; struct cmsghdr align; } u = {0};
    struct msghdr m = {0};

    m.msg_iov = &io;        m.msg_iovlen = 1;
    m.msg_control = u.buf;  m.msg_controllen = sizeof u.buf;

    struct cmsghdr *c = CMSG_FIRSTHDR(&m);
    c->cmsg_level = SOL_SOCKET;
    c->cmsg_type  = SCM_RIGHTS;
    c->cmsg_len   = CMSG_LEN(sizeof(int));
    memcpy(CMSG_DATA(c), &fd, sizeof(int));

    return sendmsg(sock, &m, 0) < 0 ? -1 : 0;
}

static int recv_fd(int sock)
{
    char one;
    struct iovec io = { .iov_base = &one, .iov_len = 1 };
    union { char buf[CMSG_SPACE(sizeof(int))]; struct cmsghdr align; } u;
    struct msghdr m = {0};

    m.msg_iov = &io;        m.msg_iovlen = 1;
    m.msg_control = u.buf;  m.msg_controllen = sizeof u.buf;

    if (recvmsg(sock, &m, 0) <= 0) return -1;
    struct cmsghdr *c = CMSG_FIRSTHDR(&m);
    if (!c || c->cmsg_len != CMSG_LEN(sizeof(int))
           || c->cmsg_level != SOL_SOCKET || c->cmsg_type != SCM_RIGHTS)
        return -1;
    int got;
    memcpy(&got, CMSG_DATA(c), sizeof got);
    return got;
}
