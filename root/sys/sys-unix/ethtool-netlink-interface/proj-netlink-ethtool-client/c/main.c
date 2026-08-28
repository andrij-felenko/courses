#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/genetlink.h>
#include <linux/ethtool_netlink.h>

#define BUFFER_SIZE 8192

/* Допоміжна функція для додавання NLA атрибута в буфер */
static void add_attr(struct nlmsghdr *nlh, int maxlen, int type, const void *data, int alen) {
    int len = RTA_LENGTH(alen);
    struct rtattr *rta;
    if (NLMSG_ALIGN(nlh->nlmsg_len) + RTA_ALIGN(len) > maxlen) {
        fprintf(stderr, "Buffer overflow adding NLA attribute\n");
        return;
    }
    rta = (struct rtattr *)(((char *)nlh) + NLMSG_ALIGN(nlh->nlmsg_len));
    rta->rta_type = type;
    rta->rta_len = len;
    if (alen > 0)
        memcpy(RTA_DATA(rta), data, alen);
    nlh->nlmsg_len = NLMSG_ALIGN(nlh->nlmsg_len) + RTA_ALIGN(len);
}

/* Розв'язання ID сімейства ethtool через Generic Netlink Controller */
static uint16_t resolve_family_id(int fd, const char *family_name) {
    char buf[BUFFER_SIZE];
    memset(buf, 0, sizeof(buf));

    struct nlmsghdr *nlh = (struct nlmsghdr *)buf;
    nlh->nlmsg_len = NLMSG_LENGTH(GENL_HDRLEN);
    nlh->nlmsg_type = GENL_ID_CTRL;
    nlh->nlmsg_flags = NLM_F_REQUEST | NLM_F_ACK;
    nlh->nlmsg_seq = 1;
    nlh->nlmsg_pid = getpid();

    struct genlmsghdr *ghdr = (struct genlmsghdr *)NLMSG_DATA(nlh);
    ghdr->cmd = CTRL_CMD_GETFAMILY;
    ghdr->version = 1;

    add_attr(nlh, sizeof(buf), CTRL_ATTR_FAMILY_NAME, family_name, strlen(family_name) + 1);

    struct sockaddr_nl nladdr = { .nl_family = AF_NETLINK };
    if (sendto(fd, nlh, nlh->nlmsg_len, 0, (struct sockaddr *)&nladdr, sizeof(nladdr)) < 0) {
        perror("sendto CTRL_CMD_GETFAMILY");
        return 0;
    }

    ssize_t ret = recv(fd, buf, sizeof(buf), 0);
    if (ret < 0) {
        perror("recv family response");
        return 0;
    }

    nlh = (struct nlmsghdr *)buf;
    if (!NLMSG_OK(nlh, ret) || nlh->nlmsg_type == NLMSG_ERROR) {
        fprintf(stderr, "Failed to resolve family ID for %s\n", family_name);
        return 0;
    }

    ghdr = (struct genlmsghdr *)NLMSG_DATA(nlh);
    struct rtattr *attr = (struct rtattr *)((char *)ghdr + GENL_HDRLEN);
    int attrlen = nlh->nlmsg_len - NLMSG_LENGTH(GENL_HDRLEN);

    uint16_t family_id = 0;
    while (RTA_OK(attr, attrlen)) {
        if (attr->rta_type == CTRL_ATTR_FAMILY_ID) {
            family_id = *(uint16_t *)RTA_DATA(attr);
            break;
        }
        attr = RTA_NEXT(attr, attrlen);
    }
    return family_id;
}

/* Запит режимів лінку для інтерфейсу */
static void query_linkmodes(int fd, uint16_t family_id, const char *ifname) {
    char buf[BUFFER_SIZE];
    memset(buf, 0, sizeof(buf));

    struct nlmsghdr *nlh = (struct nlmsghdr *)buf;
    nlh->nlmsg_len = NLMSG_LENGTH(GENL_HDRLEN);
    nlh->nlmsg_type = family_id;
    nlh->nlmsg_flags = NLM_F_REQUEST;
    nlh->nlmsg_seq = 2;
    nlh->nlmsg_pid = getpid();

    struct genlmsghdr *ghdr = (struct genlmsghdr *)NLMSG_DATA(nlh);
    ghdr->cmd = ETHTOOL_MSG_LINKMODES_GET;
    ghdr->version = ETHTOOL_GENL_VERSION;

    /* Створення вкладеного заголовку ETHTOOL_A_HEADER */
    int header_start = nlh->nlmsg_len;
    struct rtattr *hdr_attr = (struct rtattr *)(((char *)nlh) + header_start);
    hdr_attr->rta_type = NLA_F_NESTED | ETHTOOL_A_LINKMODES_HEADER;
    hdr_attr->rta_len = RTA_LENGTH(0);
    nlh->nlmsg_len += RTA_LENGTH(0);

    add_attr(nlh, sizeof(buf), ETHTOOL_A_HEADER_DEV_NAME, ifname, strlen(ifname) + 1);
    hdr_attr->rta_len = nlh->nlmsg_len - header_start;

    struct sockaddr_nl nladdr = { .nl_family = AF_NETLINK };
    if (sendto(fd, nlh, nlh->nlmsg_len, 0, (struct sockaddr *)&nladdr, sizeof(nladdr)) < 0) {
        perror("sendto ETHTOOL_MSG_LINKMODES_GET");
        return;
    }

    ssize_t ret = recv(fd, buf, sizeof(buf), 0);
    if (ret < 0) {
        perror("recv linkmodes");
        return;
    }

    nlh = (struct nlmsghdr *)buf;
    if (NLMSG_OK(nlh, ret) && nlh->nlmsg_type == family_id) {
        ghdr = (struct genlmsghdr *)NLMSG_DATA(nlh);
        if (ghdr->cmd == ETHTOOL_MSG_LINKMODES_GET || ghdr->cmd == ETHTOOL_MSG_LINKMODES_NTF) {
            struct rtattr *attr = (struct rtattr *)((char *)ghdr + GENL_HDRLEN);
            int attrlen = nlh->nlmsg_len - NLMSG_LENGTH(GENL_HDRLEN);

            uint32_t speed = 0;
            uint8_t duplex = 0, autoneg = 0;

            while (RTA_OK(attr, attrlen)) {
                if (attr->rta_type == ETHTOOL_A_LINKMODES_SPEED) {
                    speed = *(uint32_t *)RTA_DATA(attr);
                } else if (attr->rta_type == ETHTOOL_A_LINKMODES_DUPLEX) {
                    duplex = *(uint8_t *)RTA_DATA(attr);
                } else if (attr->rta_type == ETHTOOL_A_LINKMODES_AUTONEG) {
                    autoneg = *(uint8_t *)RTA_DATA(attr);
                }
                attr = RTA_NEXT(attr, attrlen);
            }
            printf("[%s] Speed: %u Mbps, Duplex: %s, Autoneg: %s\n",
                   ifname, speed,
                   duplex == 1 ? "Full" : (duplex == 0 ? "Half" : "Unknown"),
                   autoneg ? "on" : "off");
        }
    }
}

int main(int argc, char *argv[]) {
    const char *ifname = (argc > 1) ? argv[1] : "eth0";

    int fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_GENERIC);
    if (fd < 0) {
        perror("socket(AF_NETLINK)");
        return 1;
    }

    struct sockaddr_nl local = {
        .nl_family = AF_NETLINK,
        .nl_pid = getpid()
    };
    if (bind(fd, (struct sockaddr *)&local, sizeof(local)) < 0) {
        perror("bind");
        close(fd);
        return 1;
    }

    uint16_t family_id = resolve_family_id(fd, ETHTOOL_GENL_NAME);
    if (!family_id) {
        fprintf(stderr, "Ethtool Generic Netlink family not found!\n");
        close(fd);
        return 1;
    }
    printf("Resolved ethtool family ID: %u\n", family_id);

    query_linkmodes(fd, family_id, ifname);

    close(fd);
    return 0;
}
