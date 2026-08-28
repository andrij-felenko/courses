/* C Implementation: Standalone POSIX Netlink event monitor */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/genetlink.h>

#define MPTCP_GENL_NAME "mptcp"
#define MPTCP_GENL_EV_GRP "subflow"

int create_netlink_mptcp_socket(void)
{
    int fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_GENERIC);
    if (fd < 0) {
        perror("[c-netlink] socket AF_NETLINK");
        return -1;
    }

    struct sockaddr_nl local;
    memset(&local, 0, sizeof(local));
    local.nl_family = AF_NETLINK;
    local.nl_groups = 0x1; /* Підписка на мультикаст-групу подій MPTCP */

    if (bind(fd, (struct sockaddr *)&local, sizeof(local)) < 0) {
        perror("[c-netlink] bind netlink");
        close(fd);
        return -1;
    }

    return fd;
}

void process_event_stream(int fd)
{
    char buffer[8192];
    while (1) {
        ssize_t len = recv(fd, buffer, sizeof(buffer), 0);
        if (len < 0) {
            perror("[c-netlink] recv netlink");
            break;
        }

        struct nlmsghdr *nlh = (struct nlmsghdr *)buffer;
        while (NLMSG_OK(nlh, len)) {
            if (nlh->nlmsg_type == NLMSG_DONE) break;
            if (nlh->nlmsg_type == NLMSG_ERROR) {
                fprintf(stderr, "[c-netlink] Received Netlink error payload\n");
                break;
            }

            struct genlmsghdr *genl = (struct genlmsghdr *)NLMSG_DATA(nlh);
            printf("[c-netlink] Event Generic Netlink Cmd ID: %u, Version: %u\n",
                   genl->cmd, genl->version);

            nlh = NLMSG_NEXT(nlh, len);
        }
    }
}
