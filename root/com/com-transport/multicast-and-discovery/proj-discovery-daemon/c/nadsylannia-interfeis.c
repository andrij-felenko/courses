static void send_on(unsigned ifindex, const void *buf, size_t len)
{
    struct iovec io;
    io.iov_base = (void *)buf;
    io.iov_len  = len;

    union {                                   /* об'єднання дає потрібне вирівнювання */
        struct cmsghdr align;
        char           raw[CMSG_SPACE(sizeof(struct in_pktinfo))];
    } ctl;
    memset(&ctl, 0, sizeof ctl);

    struct msghdr m;
    memset(&m, 0, sizeof m);
    m.msg_name       = (void *)&group;        /* 239.7.7.7:7711 */
    m.msg_namelen    = sizeof group;
    m.msg_iov        = &io;
    m.msg_iovlen     = 1;
    m.msg_control    = ctl.raw;
    m.msg_controllen = sizeof ctl.raw;

    struct cmsghdr *c = CMSG_FIRSTHDR(&m);
    c->cmsg_level = IPPROTO_IP;
    c->cmsg_type  = IP_PKTINFO;
    c->cmsg_len   = CMSG_LEN(sizeof(struct in_pktinfo));

    struct in_pktinfo pi;
    memset(&pi, 0, sizeof pi);
    pi.ipi_ifindex = ifindex;                 /* цей пакет — саме в цей сегмент */
    memcpy(CMSG_DATA(c), &pi, sizeof pi);
    m.msg_controllen = CMSG_SPACE(sizeof(struct in_pktinfo));

    if (sendmsg(sock, &m, 0) < 0 && errno != ENETUNREACH && errno != ENETDOWN)
        fprintf(stderr, "надсилання на if%u: %s\n", ifindex, strerror(errno));
}
