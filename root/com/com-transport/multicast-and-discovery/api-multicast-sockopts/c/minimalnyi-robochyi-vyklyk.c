#include <arpa/inet.h>
#include <net/if.h>
#include <netinet/in.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

/* приймач: слухати групу group:port на інтерфейсі ifname */
int mcast_rx(const char *group, unsigned short port, const char *ifname)
{
    int fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0)
        return -1;

    int on = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof on);
#ifdef SO_REUSEPORT
    setsockopt(fd, SOL_SOCKET, SO_REUSEPORT, &on, sizeof on);   /* потрібне на BSD */
#endif

    /* підстановна адреса — єдиний варіант, що поводиться однаково всюди */
    struct sockaddr_in a;
    memset(&a, 0, sizeof a);
    a.sin_family      = AF_INET;
    a.sin_port        = htons(port);
    a.sin_addr.s_addr = htonl(INADDR_ANY);
    if (bind(fd, (struct sockaddr *)&a, sizeof a) < 0)
        goto fail;

    struct ip_mreqn mreq;
    memset(&mreq, 0, sizeof mreq);
    if (inet_pton(AF_INET, group, &mreq.imr_multiaddr) != 1)
        goto fail;
    mreq.imr_ifindex = (int)if_nametoindex(ifname);
    if (mreq.imr_ifindex == 0)                  /* немає такого інтерфейсу */
        goto fail;
    if (setsockopt(fd, IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq, sizeof mreq) < 0)
        goto fail;

#ifdef IP_MULTICAST_ALL
    int off = 0;                                /* Linux: чужих груп не хочу */
    setsockopt(fd, IPPROTO_IP, IP_MULTICAST_ALL, &off, sizeof off);
#endif
    setsockopt(fd, IPPROTO_IP, IP_PKTINFO, &on, sizeof on);
    return fd;

fail:
    close(fd);
    return -1;
}

/* відправник: слати в групу з того самого інтерфейсу, ttl переходів углиб */
int mcast_tx(const char *ifname, int ttl)
{
    int fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0)
        return -1;

    struct ip_mreqn out;
    memset(&out, 0, sizeof out);
    out.imr_ifindex = (int)if_nametoindex(ifname);
    if (out.imr_ifindex == 0 ||
        setsockopt(fd, IPPROTO_IP, IP_MULTICAST_IF, &out, sizeof out) < 0) {
        close(fd);
        return -1;
    }
    setsockopt(fd, IPPROTO_IP, IP_MULTICAST_TTL, &ttl, sizeof ttl);
    return fd;                                  /* приєднання для слання не треба */
}
