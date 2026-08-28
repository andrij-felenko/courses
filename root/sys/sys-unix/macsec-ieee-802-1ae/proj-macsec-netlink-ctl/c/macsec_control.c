/* macsec_control.c — C-реалізація створення та перевірки MACsec через Netlink */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <linux/if_link.h>
#include <linux/if_macsec.h>
#include <net/if.h>

#define NL_BUF_SIZE 4096

/* Допоміжна функція для додавання атрибута Netlink у буфер */
static void add_attr(struct nlmsghdr *nlh, int type, const void *data, int len) {
    int attr_len = RTA_LENGTH(len);
    struct rtattr *rta = (struct rtattr *)(((char *)nlh) + NLMSG_ALIGN(nlh->nlmsg_len));
    rta->rta_type = type;
    rta->rta_len = attr_len;
    if (len > 0 && data != NULL) {
        memcpy(RTA_DATA(rta), data, len);
    }
    nlh->nlmsg_len = NLMSG_ALIGN(nlh->nlmsg_len) + RTA_ALIGN(attr_len);
}

/* Створення віртуального пристрою macsec0 поверх eth0 */
int create_macsec_interface(const char *ifname, unsigned int parent_ifindex, uint64_t sci) {
    int fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);
    if (fd < 0) {
        perror("socket(AF_NETLINK)");
        return -1;
    }

    char buffer[NL_BUF_SIZE];
    memset(buffer, 0, sizeof(buffer));

    struct nlmsghdr *nlh = (struct nlmsghdr *)buffer;
    nlh->nlmsg_len = NLMSG_LENGTH(sizeof(struct ifinfomsg));
    nlh->nlmsg_type = RTM_NEWLINK;
    nlh->nlmsg_flags = NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | NLM_F_ACK;
    nlh->nlmsg_seq = 1;

    struct ifinfomsg *ifi = (struct ifinfomsg *)NLMSG_DATA(nlh);
    ifi->ifi_family = AF_UNSPEC;

    /* Назва нового інтерфейсу */
    add_attr(nlh, IFLA_IFNAME, ifname, strlen(ifname) + 1);
    
    /* Базовий батьківський пристрій (eth0) */
    add_attr(nlh, IFLA_LINK, &parent_ifindex, sizeof(parent_ifindex));

    /* Вкладена конфігурація IFLA_LINKINFO */
    struct rtattr *linkinfo = (struct rtattr *)(((char *)nlh) + NLMSG_ALIGN(nlh->nlmsg_len));
    add_attr(nlh, IFLA_LINKINFO, NULL, 0);

    /* Тип посилання: macsec */
    const char *kind = "macsec";
    add_attr(nlh, IFLA_INFO_KIND, kind, strlen(kind) + 1);

    /* Дані конфігурації MACsec */
    struct rtattr *infodata = (struct rtattr *)(((char *)nlh) + NLMSG_ALIGN(nlh->nlmsg_len));
    add_attr(nlh, IFLA_INFO_DATA, NULL, 0);

    /* Встановлення SCI та увімкнення шифрування */
    add_attr(nlh, IFLA_MACSEC_SCI, &sci, sizeof(sci));
    
    uint8_t encrypt = 1;
    add_attr(nlh, IFLA_MACSEC_ENCRYPT, &encrypt, sizeof(encrypt));

    /* Закриваємо довжини вкладених атрибутів */
    infodata->rta_len = (char *)nlh + nlh->nlmsg_len - (char *)infodata;
    linkinfo->rta_len = (char *)nlh + nlh->nlmsg_len - (char *)linkinfo;

    struct sockaddr_nl sa;
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;

    if (sendto(fd, nlh, nlh->nlmsg_len, 0, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("sendto(AF_NETLINK)");
        close(fd);
        return -1;
    }

    /* Читання відповіді ACK від ядра */
    ssize_t len = recv(fd, buffer, sizeof(buffer), 0);
    close(fd);

    if (len < 0) {
        perror("recv(AF_NETLINK)");
        return -1;
    }

    struct nlmsghdr *res = (struct nlmsghdr *)buffer;
    if (res->nlmsg_type == NLMSG_ERROR) {
        struct nlmsgerr *err = (struct nlmsgerr *)NLMSG_DATA(res);
        if (err->error != 0) {
            fprintf(stderr, "Помилка ядра Netlink: %s (%d)\n", strerror(-err->error), err->error);
            return -1;
        }
    }

    printf("Інтерфейс %s успішно створено у ядрі.\n", ifname);
    return 0;
}

int main(void) {
    unsigned int parent_idx = if_nametoindex("eth0");
    if (parent_idx == 0) {
        fprintf(stderr, "Базовий інтерфейс eth0 не знайдено.\n");
        return 1;
    }

    /* SCI: MAC 00:11:22:33:44:55, Port 1 -> 0x0011223344550001ULL */
    uint64_t sci = 0x0011223344550001ULL;
    return create_macsec_interface("macsec0", parent_idx, sci) == 0 ? 0 : 1;
}
