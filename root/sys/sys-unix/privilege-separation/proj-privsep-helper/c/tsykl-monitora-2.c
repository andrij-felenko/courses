static int recv_req(int sock, struct req *rq)
{
    struct iovec iov = { .iov_base = rq, .iov_len = sizeof *rq };
    union { char b[CMSG_SPACE(sizeof(int) * 8)]; struct cmsghdr align; } cm;
    struct msghdr msg = { .msg_iov = &iov, .msg_iovlen = 1,
                          .msg_control = cm.b, .msg_controllen = sizeof cm.b };
    ssize_t n;
    do { n = recvmsg(sock, &msg, MSG_CMSG_CLOEXEC); } while (n < 0 && errno == EINTR);

    if (n == 0) return REQ_EOF;                        /* робітник помер — кінець сесії */
    if (n < 0)  return REQ_ERR;
    if (n != (ssize_t)sizeof *rq) return REQ_ERR;      /* межі зберігає SEQPACKET */
    if (msg.msg_flags & (MSG_TRUNC | MSG_CTRUNC)) return REQ_ERR;

    /* Робітник не має права слати дескриптори. Прийшли — закрити й розірвати. */
    int hostile = 0;
    for (struct cmsghdr *c = CMSG_FIRSTHDR(&msg); c; c = CMSG_NXTHDR(&msg, c)) {
        hostile = 1;
        if (c->cmsg_level == SOL_SOCKET && c->cmsg_type == SCM_RIGHTS) {
            size_t k = (c->cmsg_len - CMSG_LEN(0)) / sizeof(int);
            for (size_t i = 0; i < k; i++) {
                int fd;
                memcpy(&fd, CMSG_DATA(c) + i * sizeof(int), sizeof fd);
                close(fd);
            }
        }
    }
    return hostile ? REQ_ERR : REQ_OK;
}
