#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <arpa/inet.h>

struct nl_req {
    struct nlmsghdr n;
    struct ifaddrmsg ifa;
    char buf[256];
};

static void add_attr(struct nlmsghdr *n, int maxlen, int type, const void *data, int alen) {
    int len = RTA_LENGTH(alen);
    if (NLMSG_ALIGN(n->nlmsg_len) + RTA_ALIGN(len) > maxlen) return;
    struct rtattr *rta = (struct rtattr *)(((char *)n) + NLMSG_ALIGN(n->nlmsg_len));
    rta->rta_type = type;
    rta->rta_len = len;
    memcpy(RTA_DATA(rta), data, alen);
    n->nlmsg_len = NLMSG_ALIGN(n->nlmsg_len) + RTA_ALIGN(len);
}

int main(void) {
    int fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);
    if (fd < 0) {
        perror("socket");
        return 1;
    }

    struct nl_req req;
    memset(&req, 0, sizeof(req));

    req.n.nlmsg_len = NLMSG_LENGTH(sizeof(struct ifaddrmsg));
    req.n.nlmsg_flags = NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | NLM_F_ACK;
    req.n.nlmsg_type = RTM_NEWADDR;
    req.n.nlmsg_seq = 1;

    req.ifa.ifa_family = AF_INET;
    req.ifa.ifa_prefixlen = 24;
    req.ifa.ifa_flags = IFA_F_PERMANENT;
    req.ifa.ifa_scope = RT_SCOPE_UNIVERSE;
    req.ifa.ifa_index = 2; // ifindex цільового інтерфейсу

    struct in_addr addr;
    inet_pton(AF_INET, "192.168.10.50", &addr);
    add_attr(&req.n, sizeof(req), IFA_LOCAL, &addr, sizeof(addr));
    add_attr(&req.n, sizeof(req), IFA_ADDRESS, &addr, sizeof(addr));

    struct sockaddr_nl sa;
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;

    if (sendto(fd, &req, req.n.nlmsg_len, 0, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("sendto");
        close(fd);
        return 1;
    }

    printf("Повідомлення RTM_NEWADDR успішно надіслано в ядро.\n");
    close(fd);
    return 0;
}
