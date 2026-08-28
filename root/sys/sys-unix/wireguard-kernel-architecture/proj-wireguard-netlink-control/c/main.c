#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/genetlink.h>
#include <net/if.h>
#include <arpa/inet.h>

#define WG_GENL_NAME "wireguard"
#define WG_GENL_VERSION 1

enum wg_cmd {
    WG_CMD_GET_DEVICE,
    WG_CMD_SET_DEVICE,
};

enum wgdevice_attribute {
    WGDEVICE_A_UNSPEC,
    WGDEVICE_A_IFINDEX,
    WGDEVICE_A_IFNAME,
    WGDEVICE_A_PRIVATE_KEY,
    WGDEVICE_A_PUBLIC_KEY,
    WGDEVICE_A_LISTEN_PORT,
    WGDEVICE_A_FWMARK,
    WGDEVICE_A_FLAGS,
    WGDEVICE_A_PEERS,
    __WGDEVICE_A_MAX
};

enum wgpeer_attribute {
    WGPEER_A_UNSPEC,
    WGPEER_A_PUBLIC_KEY,
    WGPEER_A_PRESHARED_KEY,
    WGPEER_A_ENDPOINT,
    WGPEER_A_PERSISTENT_KEEPALIVE_INTERVAL,
    WGPEER_A_FLAGS,
    WGPEER_A_ALLOWEDIPS,
    __WGPEER_A_MAX
};

enum wgallowedip_attribute {
    WGALLOWEDIP_A_UNSPEC,
    WGALLOWEDIP_A_FAMILY,
    WGALLOWEDIP_A_IPADDR,
    WGALLOWEDIP_A_CIDR_MASK,
    __WGALLOWEDIP_A_MAX
};

/* Допоміжна функція додавання звичайного атрибута Netlink */
static void add_attr(struct nlmsghdr *nlh, int maxlen, int type, const void *data, int alen) {
    int len = RTA_LENGTH(alen);
    if (NLMSG_ALIGN(nlh->nlmsg_len) + RTA_ALIGN(len) > maxlen) {
        fprintf(stderr, "Помилка: буфер Netlink переповнено\n");
        exit(EXIT_FAILURE);
    }
    struct rtattr *rta = (struct rtattr *)(((char *)nlh) + NLMSG_ALIGN(nlh->nlmsg_len));
    rta->rta_type = type;
    rta->rta_len = len;
    if (data && alen > 0) {
        memcpy(RTA_DATA(rta), data, alen);
    }
    nlh->nlmsg_len = NLMSG_ALIGN(nlh->nlmsg_len) + RTA_ALIGN(len);
}

/* Відкриття вкладеного контейнера атрибутів (NLA_F_NESTED) */
static struct rtattr *nest_start(struct nlmsghdr *nlh, int maxlen, int type) {
    struct rtattr *nest = (struct rtattr *)(((char *)nlh) + NLMSG_ALIGN(nlh->nlmsg_len));
    add_attr(nlh, maxlen, type, NULL, 0);
    return nest;
}

/* Завершення та фіксація довжини вкладеного атрибута */
static void nest_end(struct nlmsghdr *nlh, struct rtattr *nest) {
    nest->rta_len = (char *)nlh + NLMSG_ALIGN(nlh->nlmsg_len) - (char *)nest;
}

int main(void) {
    int fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_GENERIC);
    if (fd < 0) {
        perror("socket");
        return 1;
    }

    struct sockaddr_nl local = { .nl_family = AF_NETLINK };
    if (bind(fd, (struct sockaddr *)&local, sizeof(local)) < 0) {
        perror("bind");
        close(fd);
        return 1;
    }

    char buffer[4096];
    memset(buffer, 0, sizeof(buffer));

    struct nlmsghdr *nlh = (struct nlmsghdr *)buffer;
    nlh->nlmsg_len = NLMSG_LENGTH(sizeof(struct genlmsghdr));
    nlh->nlmsg_type = 0x10; /* Символічний ID сімейства wireguard у ядрі */
    nlh->nlmsg_flags = NLM_F_REQUEST | NLM_F_ACK;
    nlh->nlmsg_seq = 1;

    struct genlmsghdr *genl = (struct genlmsghdr *)NLMSG_DATA(nlh);
    genl->cmd = WG_CMD_SET_DEVICE;
    genl->version = WG_GENL_VERSION;

    /* Вказуємо ім'я пристрою wg0 */
    const char *ifname = "wg0";
    add_attr(nlh, sizeof(buffer), WGDEVICE_A_IFNAME, ifname, strlen(ifname) + 1);

    /* Вкладений блок пірів WGDEVICE_A_PEERS */
    struct rtattr *peers_nest = nest_start(nlh, sizeof(buffer), WGDEVICE_A_PEERS | NLA_F_NESTED);
    struct rtattr *peer_nest = nest_start(nlh, sizeof(buffer), 0 | NLA_F_NESTED);

    /* Фіктивний публічний ключ піра (32 байти) */
    unsigned char pubkey[32] = {
        0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
        0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10,
        0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18,
        0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x20
    };
    add_attr(nlh, sizeof(buffer), WGPEER_A_PUBLIC_KEY, pubkey, 32);

    /* Зовнішня кінцева точка: 192.168.1.100:51820 */
    struct sockaddr_in ep = {
        .sin_family = AF_INET,
        .sin_port = htons(51820)
    };
    inet_pton(AF_INET, "192.168.1.100", &ep.sin_addr);
    add_attr(nlh, sizeof(buffer), WGPEER_A_ENDPOINT, &ep, sizeof(ep));

    /* Додаємо дозволені IP-адреси AllowedIPs (10.0.0.2/32) */
    struct rtattr *aips_nest = nest_start(nlh, sizeof(buffer), WGPEER_A_ALLOWEDIPS | NLA_F_NESTED);
    struct rtattr *aip_nest = nest_start(nlh, sizeof(buffer), 0 | NLA_F_NESTED);

    uint16_t family = AF_INET;
    struct in_addr ip_addr;
    inet_pton(AF_INET, "10.0.0.2", &ip_addr);
    uint8_t cidr = 32;

    add_attr(nlh, sizeof(buffer), WGALLOWEDIP_A_FAMILY, &family, sizeof(family));
    add_attr(nlh, sizeof(buffer), WGALLOWEDIP_A_IPADDR, &ip_addr, sizeof(ip_addr));
    add_attr(nlh, sizeof(buffer), WGALLOWEDIP_A_CIDR_MASK, &cidr, sizeof(cidr));

    nest_end(nlh, aip_nest);
    nest_end(nlh, aips_nest);

    nest_end(nlh, peer_nest);
    nest_end(nlh, peers_nest);

    struct sockaddr_nl nl_kernel = { .nl_family = AF_NETLINK };
    if (sendto(fd, nlh, nlh->nlmsg_len, 0, (struct sockaddr *)&nl_kernel, sizeof(nl_kernel)) < 0) {
        perror("sendto");
        close(fd);
        return 1;
    }

    printf("Повідомлення WG_CMD_SET_DEVICE надіслано до ядра Linux\n");
    close(fd);
    return 0;
}
