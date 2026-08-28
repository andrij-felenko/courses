static void addr_init(struct sockaddr_un *a, socklen_t *len)
{
    memset(a, 0, sizeof *a);
    a->sun_family = AF_UNIX;
    a->sun_path[0] = '\0';                     /* абстрактний простір імен Linux */
    memcpy(a->sun_path + 1, SOCKNAME, strlen(SOCKNAME));
    *len = offsetof(struct sockaddr_un, sun_path) + 1 + strlen(SOCKNAME);
}

static void send_fd(int sock, int fd, const struct handoff *h)
{
    struct iovec iov = { .iov_base = (void *)h, .iov_len = sizeof *h };
    union { char buf[CMSG_SPACE(sizeof(int))]; struct cmsghdr align; } u;
    memset(&u, 0, sizeof u);

    struct msghdr msg = { .msg_iov = &iov, .msg_iovlen = 1,
                          .msg_control = u.buf, .msg_controllen = sizeof u.buf };
    struct cmsghdr *c = CMSG_FIRSTHDR(&msg);
    c->cmsg_level = SOL_SOCKET;
    c->cmsg_type  = SCM_RIGHTS;
    c->cmsg_len   = CMSG_LEN(sizeof(int));
    memcpy(CMSG_DATA(c), &fd, sizeof fd);

    if (sendmsg(sock, &msg, 0) != (ssize_t)sizeof *h) die("sendmsg");
}

static int recv_fd(int sock, struct handoff *h)
{
    struct iovec iov = { .iov_base = h, .iov_len = sizeof *h };
    union { char buf[CMSG_SPACE(sizeof(int))]; struct cmsghdr align; } u;
    struct msghdr msg = { .msg_iov = &iov, .msg_iovlen = 1,
                          .msg_control = u.buf, .msg_controllen = sizeof u.buf };

    ssize_t n = recvmsg(sock, &msg, MSG_CMSG_CLOEXEC);
    if (n < 0) die("recvmsg");
    if (n != (ssize_t)sizeof *h) { fputs("куций заголовок\n", stderr); exit(1); }
    if (msg.msg_flags & MSG_CTRUNC) { fputs("смугу зрізано — fd закрито\n", stderr); exit(1); }

    struct cmsghdr *c = CMSG_FIRSTHDR(&msg);
    if (!c || c->cmsg_level != SOL_SOCKET || c->cmsg_type != SCM_RIGHTS
           || c->cmsg_len != CMSG_LEN(sizeof(int))) {
        fputs("у повідомленні немає дескриптора\n", stderr);
        exit(1);
    }
    int fd;
    memcpy(&fd, CMSG_DATA(c), sizeof fd);
    return fd;
}
