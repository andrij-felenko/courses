#include <sys/socket.h>
#include <netinet/in.h>
#include <string.h>

/* прийняти датаграму і дізнатися, ЯКІЙ групі вона адресована */
static ssize_t recv_with_dest(int fd, void *buf, size_t len,
                              struct sockaddr_in *from,
                              struct in_addr *dst, unsigned *ifindex)
{
    char control[CMSG_SPACE(sizeof(struct in_pktinfo))];
    struct iovec iov = { .iov_base = buf, .iov_len = len };
    struct msghdr msg = {
        .msg_name = from,      .msg_namelen   = sizeof *from,
        .msg_iov  = &iov,      .msg_iovlen    = 1,
        .msg_control = control, .msg_controllen = sizeof control,
    };

    ssize_t n = recvmsg(fd, &msg, 0);
    if (n < 0)
        return n;

    for (struct cmsghdr *c = CMSG_FIRSTHDR(&msg); c; c = CMSG_NXTHDR(&msg, c)) {
        if (c->cmsg_level == IPPROTO_IP && c->cmsg_type == IP_PKTINFO) {
            struct in_pktinfo pi;
            memcpy(&pi, CMSG_DATA(c), sizeof pi);   /* копія: вирівнювання не гарантоване */
            *dst     = pi.ipi_addr;
            *ifindex = pi.ipi_ifindex;
        }
    }
    return n;
}
