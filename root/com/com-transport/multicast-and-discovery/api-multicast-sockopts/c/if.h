#include <net/if.h>
#include <netinet/in.h>
#include <arpa/inet.h>

/* приєднання за індексом — Linux, FreeBSD, macOS */
struct ip_mreqn mreq;
memset(&mreq, 0, sizeof mreq);
inet_pton(AF_INET, "239.1.2.3", &mreq.imr_multiaddr);
mreq.imr_ifindex = (int)if_nametoindex("eth0");     /* 0 = такого імені немає */
setsockopt(fd, IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq, sizeof mreq);

/* переносний запасний варіант — Winsock, lwIP, старі системи */
struct ip_mreq old;
inet_pton(AF_INET, "239.1.2.3", &old.imr_multiaddr);
old.imr_interface.s_addr = inet_addr("192.168.1.7");  /* адреса ЦЬОГО інтерфейсу */
setsockopt(fd, IPPROTO_IP, IP_ADD_MEMBERSHIP, (const char *)&old, sizeof old);
