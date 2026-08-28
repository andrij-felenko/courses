/* bridge_fdb_inject.c - Додавання статичного запису FDB моста через RTNETLINK */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/rtnetlink.h>
#include <linux/if_bridge.h>
#include <linux/neighbour.h>
#include <net/if.h>
#include <errno.h>

#define NL_BUF_SIZE 4096

int add_fdb_entry(int ifindex, const unsigned char mac[6], unsigned short vid) {
    int fd = socket(AF_NETLINK, SOCK_RAW | SOCK_CLOEXEC, NETLINK_ROUTE);
    if (fd < 0) {
        perror("socket AF_NETLINK");
        return -1;
    }

    char buf[NL_BUF_SIZE];
    memset(buf, 0, sizeof(buf));

    struct nlmsghdr *nlh = (struct nlmsghdr *)buf;
    nlh->nlmsg_len = NLMSG_LENGTH(sizeof(struct ndmsg));
    nlh->nlmsg_flags = NLM_F_REQUEST | NLM_F_CREATE | NLM_F_REPLACE | NLM_F_ACK;
    nlh->nlmsg_type = RTM_NEWNEIGH;
    nlh->nlmsg_seq = 1;

    struct ndmsg *ndm = (struct ndmsg *)NLMSG_DATA(nlh);
    ndm->ndm_family = AF_BRIDGE;
    ndm->ndm_ifindex = ifindex;
    ndm->ndm_state = NUD_PERMANENT; /* Статичний запис (не старіє) */
    ndm->ndm_flags = NTF_MASTER;    /* Додати в FDB master-пристрою */

    /* Додаємо атрибут NDA_LLADDR (MAC-адреса) */
    struct rtattr *rta = (struct rtattr *)(((char *)nlh) + NLMSG_ALIGN(nlh->nlmsg_len));
    rta->rta_type = NDA_LLADDR;
    rta->rta_len = RTA_LENGTH(6);
    memcpy(RTA_DATA(rta), mac, 6);
    nlh->nlmsg_len = NLMSG_ALIGN(nlh->nlmsg_len) + RTA_ALIGN(rta->rta_len);

    /* Додаємо атрибут NDA_VLAN (якщо вказано VID) */
    if (vid > 0) {
        rta = (struct rtattr *)(((char *)nlh) + NLMSG_ALIGN(nlh->nlmsg_len));
        rta->rta_type = NDA_VLAN;
        rta->rta_len = RTA_LENGTH(sizeof(unsigned short));
        memcpy(RTA_DATA(rta), &vid, sizeof(unsigned short));
        nlh->nlmsg_len = NLMSG_ALIGN(nlh->nlmsg_len) + RTA_ALIGN(rta->rta_len);
    }

    struct sockaddr_nl sa;
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;

    if (sendto(fd, nlh, nlh->nlmsg_len, 0, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("sendto rtnetlink");
        close(fd);
        return -1;
    }

    /* Отримуємо підтвердження NLMSG_ERROR */
    char rcv_buf[NL_BUF_SIZE];
    ssize_t len = recv(fd, rcv_buf, sizeof(rcv_buf), 0);
    close(fd);

    if (len < 0) {
        perror("recv netlink");
        return -1;
    }

    struct nlmsghdr *resp = (struct nlmsghdr *)rcv_buf;
    if (resp->nlmsg_type == NLMSG_ERROR) {
        struct nlmsgerr *err = (struct nlmsgerr *)NLMSG_DATA(resp);
        if (err->error != 0) {
            fprintf(stderr, "Помилка Netlink FDB: %s (код %d)\n", strerror(-err->error), err->error);
            return err->error;
        }
    }

    printf("FDB запис успішно додано для ifindex=%d, vid=%d\n", ifindex, vid);
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <ifname> <MAC-адреса: XX:XX:XX:XX:XX:XX> [VLAN_ID]\n", argv[0]);
        return 1;
    }

    int ifidx = if_nametoindex(argv[1]);
    if (ifidx == 0) {
        perror("if_nametoindex");
        return 1;
    }

    unsigned char mac[6];
    if (sscanf(argv[2], "%hhx:%hhx:%hhx:%hhx:%hhx:%hhx",
               &mac[0], &mac[1], &mac[2], &mac[3], &mac[4], &mac[5]) != 6) {
        fprintf(stderr, "Некоректний формат MAC-адреси\n");
        return 1;
    }

    unsigned short vid = (argc >= 4) ? (unsigned short)atoi(argv[3]) : 0;
    return add_fdb_entry(ifidx, mac, vid);
}
