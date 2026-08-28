#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <net/if.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <linux/if_link.h>

#define NL_BUF_SIZE 4096

/* Допоміжна функція додавання атрибута Netlink із правильним 4-байтовим вирівнюванням */
static void add_attr(struct nlmsghdr *nlh, int type, const void *data, int len) {
    int attr_len = RTA_LENGTH(len);
    struct rtattr *rta = (struct rtattr *)((char *)nlh + NLMSG_ALIGN(nlh->nlmsg_len));
    rta->rta_type = type;
    rta->rta_len = attr_len;
    if (len > 0 && data) {
        memcpy(RTA_DATA(rta), data, len);
    }
    nlh->nlmsg_len = NLMSG_ALIGN(nlh->nlmsg_len) + RTA_ALIGN(attr_len);
}

/* Основна функція створення інтерфейсу Macvlan */
int create_macvlan_interface(const char *parent_ifname, const char *macvlan_ifname, uint32_t mode) {
    /* Отримання системного індексу батьківського пристрою */
    unsigned int parent_idx = if_nametoindex(parent_ifname);
    if (parent_idx == 0) {
        perror("if_nametoindex failed");
        return -1;
    }

    /* Відкриття сокета AF_NETLINK для роботи з маршрутизацією та лінками */
    int fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);
    if (fd < 0) {
        perror("socket AF_NETLINK failed");
        return -1;
    }

    char buffer[NL_BUF_SIZE];
    memset(buffer, 0, sizeof(buffer));

    /* Ініціалізація заголовка nlmsghdr */
    struct nlmsghdr *nlh = (struct nlmsghdr *)buffer;
    nlh->nlmsg_len = NLMSG_LENGTH(sizeof(struct ifinfomsg));
    nlh->nlmsg_type = RTM_NEWLINK;
    nlh->nlmsg_flags = NLM_F_REQUEST | NLM_F_ACK | NLM_F_CREATE | NLM_F_EXCL;
    nlh->nlmsg_seq = 1;

    struct ifinfomsg *ifi = (struct ifinfomsg *)NLMSG_DATA(nlh);
    ifi->ifi_family = AF_UNSPEC;

    /* 1. Атрибут імені нового інтерфейсу */
    add_attr(nlh, IFLA_IFNAME, macvlan_ifname, strlen(macvlan_ifname) + 1);

    /* 2. Атрибут індексу батьківського фізичного NIC */
    add_attr(nlh, IFLA_LINK, &parent_idx, sizeof(parent_idx));

    /* 3. Вкладений атрибут IFLA_LINKINFO */
    struct rtattr *linkinfo = (struct rtattr *)((char *)nlh + NLMSG_ALIGN(nlh->nlmsg_len));
    add_attr(nlh, IFLA_LINKINFO, NULL, 0);

    /* 3a. Вказівка типу драйвера IFLA_INFO_KIND = "macvlan" */
    const char *kind = "macvlan";
    add_attr(nlh, IFLA_INFO_KIND, kind, strlen(kind) + 1);

    /* 3b. Вкладений атрибут IFLA_INFO_DATA */
    struct rtattr *infodata = (struct rtattr *)((char *)nlh + NLMSG_ALIGN(nlh->nlmsg_len));
    add_attr(nlh, IFLA_INFO_DATA, NULL, 0);

    /* 3c. Режим Macvlan (IFLA_MACVLAN_MODE) */
    add_attr(nlh, IFLA_MACVLAN_MODE, &mode, sizeof(mode));

    /* Зафіксуємо підсумкові довжини вкладених rtattr */
    infodata->rta_len = (char *)nlh + nlh->nlmsg_len - (char *)infodata;
    linkinfo->rta_len = (char *)nlh + nlh->nlmsg_len - (char *)linkinfo;

    /* Відправка пакета у ядро Linux */
    struct sockaddr_nl sa;
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;

    if (sendto(fd, nlh, nlh->nlmsg_len, 0, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("sendto failed");
        close(fd);
        return -1;
    }

    /* Отримання підтвердження (ACK або повідомлення про помилку) */
    char ack_buf[NL_BUF_SIZE];
    ssize_t ret = recv(fd, ack_buf, sizeof(ack_buf), 0);
    close(fd);

    if (ret < 0) {
        perror("recv failed");
        return -1;
    }

    struct nlmsghdr *ack_nlh = (struct nlmsghdr *)ack_buf;
    if (ack_nlh->nlmsg_type == NLMSG_ERROR) {
        struct nlmsgerr *err = (struct nlmsgerr *)NLMSG_DATA(ack_nlh);
        if (err->error != 0) {
            fprintf(stderr, "Netlink error: %s (%d)\n", strerror(-err->error), err->error);
            return -1;
        }
    }

    printf("Успішно створено Macvlan інтерфейс '%s' (mode=%u) на батькові '%s'\n",
           macvlan_ifname, mode, parent_ifname);
    return 0;
}

int main(void) {
    /* MACVLAN_MODE_BRIDGE = 2 */
    return create_macvlan_interface("eth0", "mvlan0", 2) == 0 ? 0 : 1;
}
