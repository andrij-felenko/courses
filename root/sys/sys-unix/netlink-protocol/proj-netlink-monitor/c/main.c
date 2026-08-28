#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <poll.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>

#define BUFFER_SIZE 8192

static void parse_link_event(struct nlmsghdr *nlh) {
    struct ifinfomsg *ifi = (struct ifinfomsg *)NLMSG_DATA(nlh);
    struct rtattr *rta = IFLA_RTA(ifi);
    int rta_len = IFLA_PAYLOAD(nlh);
    char ifname[IFNAMSIZ] = "unknown";

    for (; RTA_OK(rta, rta_len); rta = RTA_NEXT(rta, rta_len)) {
        if (rta->rta_type == IFLA_IFNAME) {
            snprintf(ifname, sizeof(ifname), "%s", (char *)RTA_DATA(rta));
        }
    }

    const char *action = (nlh->nlmsg_type == RTM_NEWLINK) ? "NEWLINK" : "DELLINK";
    const char *state = (ifi->ifi_flags & IFF_UP) ? "UP" : "DOWN";
    const char *running = (ifi->ifi_flags & IFF_RUNNING) ? "RUNNING" : "NOT_RUNNING";

    printf("[LINK %s] Interface %s (index %d): Flags=%s,%s\n", 
           action, ifname, ifi->ifi_index, state, running);
}

static void parse_addr_event(struct nlmsghdr *nlh) {
    struct ifaddrmsg *ifa = (struct ifaddrmsg *)NLMSG_DATA(nlh);
    struct rtattr *rta = IFA_RTA(ifa);
    int rta_len = IFA_PAYLOAD(nlh);
    char ip_str[INET_ADDRSTRLEN] = "0.0.0.0";

    for (; RTA_OK(rta, rta_len); rta = RTA_NEXT(rta, rta_len)) {
        if (rta->rta_type == IFA_ADDRESS || rta->rta_type == IFA_LOCAL) {
            struct in_addr *addr = (struct in_addr *)RTA_DATA(rta);
            inet_ntop(AF_INET, addr, ip_str, sizeof(ip_str));
        }
    }

    const char *action = (nlh->nlmsg_type == RTM_NEWADDR) ? "ADD_ADDR" : "DEL_ADDR";
    printf("[ADDR %s] Interface index %d: IP %s/%d\n", 
           action, ifa->ifa_index, ip_str, ifa->ifa_prefixlen);
}

int main(void) {
    int sock_fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);
    if (sock_fd < 0) {
        perror("socket");
        return 1;
    }

    struct sockaddr_nl sa;
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;
    sa.nl_pid = 0; /* Автоматичний вибір PID ядром */
    sa.nl_groups = RTMGRP_LINK | RTMGRP_IPV4_IFADDR;

    if (bind(sock_fd, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("bind");
        close(sock_fd);
        return 1;
    }

    printf("Netlink monitor started. Listening for RTMGRP_LINK and RTMGRP_IPV4_IFADDR...\n");

    struct pollfd pfd = { .fd = sock_fd, .events = POLLIN };
    char buffer[BUFFER_SIZE];

    while (1) {
        int ret = poll(&pfd, 1, -1);
        if (ret < 0) {
            perror("poll");
            break;
        }

        if (pfd.revents & POLLIN) {
            ssize_t len = recv(sock_fd, buffer, sizeof(buffer), 0);
            if (len < 0) {
                perror("recv");
                break;
            }

            struct nlmsghdr *nlh = (struct nlmsghdr *)buffer;
            for (; NLMSG_OK(nlh, len); nlh = NLMSG_NEXT(nlh, len)) {
                if (nlh->nlmsg_type == NLMSG_DONE) break;
                if (nlh->nlmsg_type == NLMSG_ERROR) {
                    struct nlmsgerr *err = (struct nlmsgerr *)NLMSG_DATA(nlh);
                    fprintf(stderr, "Netlink error: %d\n", err->error);
                    continue;
                }

                if (nlh->nlmsg_type == RTM_NEWLINK || nlh->nlmsg_type == RTM_DELLINK) {
                    parse_link_event(nlh);
                } else if (nlh->nlmsg_type == RTM_NEWADDR || nlh->nlmsg_type == RTM_DELADDR) {
                    parse_addr_event(nlh);
                }
            }
        }
    }

    close(sock_fd);
    return 0;
}
