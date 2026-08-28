/* C11 implementation: querying interface state via RTNETLINK */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <net/if.h>
#include <arpa/inet.h>

#define BUF_SIZE 8192

static void parse_rtattr(struct rtattr *tb[], int max, struct rtattr *rta, int len) {
    memset(tb, 0, sizeof(struct rtattr *) * (max + 1));
    while (RTA_OK(rta, len)) {
        if (rta->rta_type <= max) {
            tb[rta->rta_type] = rta;
        }
        rta = RTA_NEXT(rta, len);
    }
}

int main(void) {
    int fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);
    if (fd < 0) {
        perror("socket AF_NETLINK");
        return 1;
    }

    struct {
        struct nlmsghdr nlh;
        struct ifinfomsg ifm;
    } req;

    memset(&req, 0, sizeof(req));
    req.nlh.nlmsg_len = NLMSG_LENGTH(sizeof(struct ifinfomsg));
    req.nlh.nlmsg_type = RTM_GETLINK;
    req.nlh.nlmsg_flags = NLM_F_REQUEST | NLM_F_DUMP;
    req.nlh.nlmsg_seq = 1;
    req.ifm.ifi_family = AF_UNSPEC;

    if (send(fd, &req, req.nlh.nlmsg_len, 0) < 0) {
        perror("send");
        close(fd);
        return 1;
    }

    char buffer[BUF_SIZE];
    ssize_t status = recv(fd, buffer, sizeof(buffer), 0);
    if (status < 0) {
        perror("recv");
        close(fd);
        return 1;
    }

    for (struct nlmsghdr *nlh = (struct nlmsghdr *)buffer;
         NLMSG_OK(nlh, (size_t)status);
         nlh = NLMSG_NEXT(nlh, status)) {

        if (nlh->nlmsg_type == NLMSG_DONE) break;
        if (nlh->nlmsg_type == NLMSG_ERROR) {
            fprintf(stderr, "Error message received from Netlink\n");
            close(fd);
            return 1;
        }

        if (nlh->nlmsg_type == RTM_NEWLINK) {
            struct ifinfomsg *ifi = (struct ifinfomsg *)NLMSG_DATA(nlh);
            struct rtattr *tb[IFLA_MAX + 1];
            int rta_len = nlh->nlmsg_len - NLMSG_SPACE(sizeof(*ifi));

            parse_rtattr(tb, IFLA_MAX, IFLA_RTA(ifi), rta_len);

            const char *ifname = tb[IFLA_IFNAME] ? (const char *)RTA_DATA(tb[IFLA_IFNAME]) : "unknown";
            unsigned int mtu = tb[IFLA_MTU] ? *(unsigned int *)RTA_DATA(tb[IFLA_MTU]) : 0;
            unsigned char operstate = tb[IFLA_OPERSTATE] ? *(unsigned char *)RTA_DATA(tb[IFLA_OPERSTATE]) : 0;

            printf("Interface index %d: name=%s, MTU=%u, IFF_UP=%s, IFF_RUNNING=%s, operstate=%u\n",
                   ifi->ifi_index, ifname, mtu,
                   (ifi->ifi_flags & IFF_UP) ? "YES" : "NO",
                   (ifi->ifi_flags & IFF_RUNNING) ? "YES" : "NO",
                   operstate);
        }
    }

    close(fd);
    return 0;
}
