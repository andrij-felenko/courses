/* netlink_bond.c — C реалізація створення bonding-інтерфейсу через rtnetlink */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <net/if.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <linux/if_bonding.h>

#define NL_BUF_SIZE 4096

/* Допоміжна функція для додавання атрибутів типу rtattr */
static int add_attr(struct nlmsghdr *n, int maxlen, int type, const void *data, int alen) {
    int len = RTA_LENGTH(alen);
    if (NLMSG_ALIGN(n->nlmsg_len) + RTA_ALIGN(len) > maxlen) {
        return -1;
    }
    struct rtattr *rta = (struct rtattr *)(((char *)n) + NLMSG_ALIGN(n->nlmsg_len));
    rta->rta_type = type;
    rta->rta_len = len;
    if (alen > 0 && data != NULL) {
        memcpy(RTA_DATA(rta), data, alen);
    }
    n->nlmsg_len = NLMSG_ALIGN(n->nlmsg_len) + RTA_ALIGN(len);
    return 0;
}

/* Допоміжна функція для відкриття контейнера атрибутів */
static struct rtattr *nested_attr_begin(struct nlmsghdr *n, int maxlen, int type) {
    struct rtattr *nested = (struct rtattr *)(((char *)n) + NLMSG_ALIGN(n->nlmsg_len));
    if (add_attr(n, maxlen, type, NULL, 0) < 0) {
        return NULL;
    }
    return nested;
}

/* Завершення та коригування довжини вкладеного контейнера */
static void nested_attr_end(struct nlmsghdr *n, struct rtattr *nested) {
    nested->rta_len = (char *)n + NLMSG_ALIGN(n->nlmsg_len) - (char *)nested;
}

int create_bond_interface(const char *bond_name, uint8_t mode, uint32_t miimon_ms) {
    int fd = socket(AF_NETLINK, SOCK_RAW | SOCK_CLOEXEC, NETLINK_ROUTE);
    if (fd < 0) {
        perror("socket(AF_NETLINK)");
        return -1;
    }

    char buffer[NL_BUF_SIZE];
    memset(buffer, 0, sizeof(buffer));

    struct nlmsghdr *n = (struct nlmsghdr *)buffer;
    n->nlmsg_len = NLMSG_LENGTH(sizeof(struct ifinfomsg));
    n->nlmsg_flags = NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | NLM_F_ACK;
    n->nlmsg_type = RTM_NEWLINK;

    struct ifinfomsg *ifi = (struct ifinfomsg *)NLMSG_DATA(n);
    ifi->ifi_family = AF_UNSPEC;

    /* Назва логічного інтерфейсу bond */
    if (add_attr(n, sizeof(buffer), IFLA_IFNAME, bond_name, strlen(bond_name) + 1) < 0) {
        close(fd);
        return -1;
    }

    /* Відкриваємо вкладений атрибут IFLA_LINKINFO */
    struct rtattr *linkinfo = nested_attr_begin(n, sizeof(buffer), IFLA_LINKINFO);
    if (!linkinfo) {
        close(fd);
        return -1;
    }

    /* Тип створюваного інтерфейсу — "bond" */
    const char *kind = "bond";
    if (add_attr(n, sizeof(buffer), IFLA_INFO_KIND, kind, strlen(kind) + 1) < 0) {
        close(fd);
        return -1;
    }

    /* Відкриваємо вкладений атрибут IFLA_INFO_DATA з параметрами bonding */
    struct rtattr *infodata = nested_attr_begin(n, sizeof(buffer), IFLA_INFO_DATA);
    if (!infodata) {
        close(fd);
        return -1;
    }

    /* Встановлюємо режим Bonding (наприклад, Mode 4 - 802.3ad) */
    if (add_attr(n, sizeof(buffer), IFLA_BOND_MODE, &mode, sizeof(mode)) < 0) {
        close(fd);
        return -1;
    }

    /* Встановлюємо інтервал MII моніторингу у мілісекундах */
    if (add_attr(n, sizeof(buffer), IFLA_BOND_MIIMON, &miimon_ms, sizeof(miimon_ms)) < 0) {
        close(fd);
        return -1;
    }

    nested_attr_end(n, infodata);
    nested_attr_end(n, linkinfo);

    /* Надсилаємо запит у ядро */
    struct sockaddr_nl sa;
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;

    if (sendto(fd, n, n->nlmsg_len, 0, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("sendto(AF_NETLINK)");
        close(fd);
        return -1;
    }

    /* Отримуємо відповідь-підтвердження (ACK) від ядра */
    char ack_buf[NL_BUF_SIZE];
    ssize_t status = recv(fd, ack_buf, sizeof(ack_buf), 0);
    if (status < 0) {
        perror("recv(ACK)");
        close(fd);
        return -1;
    }

    struct nlmsghdr *ack_hdr = (struct nlmsghdr *)ack_buf;
    if (ack_hdr->nlmsg_type == NLMSG_ERROR) {
        struct nlmsgerr *err = (struct nlmsgerr *)NLMSG_DATA(ack_hdr);
        if (err->error != 0) {
            fprintf(stderr, "Помилка Rtnetlink: %s (%d)\n", strerror(-err->error), err->error);
            close(fd);
            return -1;
        }
    }

    close(fd);
    printf("Bonding пристрій '%s' успішно створено (Mode: %d, MII: %d ms)\n", bond_name, mode, miimon_ms);
    return 0;
}

int main(void) {
    /* Створюємо bond0 у режимі BOND_MODE_8023AD (4) із miimon 100мс */
    if (create_bond_interface("bond0", BOND_MODE_8023AD, 100) < 0) {
        fprintf(stderr, "Не вдалося створити bonding пристрій\n");
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
