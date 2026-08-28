static void receive_one(void)
{
    uint8_t buf[PKT_MAX];
    struct sockaddr_in from;
    struct iovec io;
    io.iov_base = buf;
    io.iov_len  = sizeof buf;

    union { struct cmsghdr align; char raw[CMSG_SPACE(sizeof(struct in_pktinfo))]; } ctl;

    struct msghdr m;
    memset(&m, 0, sizeof m);
    m.msg_name       = &from;
    m.msg_namelen    = sizeof from;
    m.msg_iov        = &io;
    m.msg_iovlen     = 1;
    m.msg_control    = ctl.raw;
    m.msg_controllen = sizeof ctl.raw;

    ssize_t n = recvmsg(sock, &m, 0);
    if (n < 0) return;
    if (m.msg_flags & MSG_TRUNC) return;      /* більша за наш буфер — точно не наша */

    unsigned ifindex = 0;
    for (struct cmsghdr *c = CMSG_FIRSTHDR(&m); c; c = CMSG_NXTHDR(&m, c))
        if (c->cmsg_level == IPPROTO_IP && c->cmsg_type == IP_PKTINFO) {
            struct in_pktinfo pi;
            memcpy(&pi, CMSG_DATA(c), sizeof pi);   /* саме memcpy: вирівнювання */
            ifindex = pi.ipi_ifindex;
        }
    on_packet(buf, (size_t)n, &from.sin_addr, ifindex);
}
