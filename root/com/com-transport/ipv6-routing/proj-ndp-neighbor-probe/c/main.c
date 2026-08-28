#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <netinet/in.h>
#include <netinet/icmp6.h>
#include <arpa/inet.h>

#define SOLICITED_NODE_PREFIX "ff02::1:ff00:0"
#define PACKET_BUFFER_SIZE 1500

/* Отримання апаратної MAC-адреси локального мережевого інтерфейсу */
static int get_interface_mac(int sock, const char *ifname, uint8_t *mac_out) {
    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, ifname, IFNAMSIZ - 1);

    if (ioctl(sock, SIOCGIFHWADDR, &ifr) < 0) {
        perror("ioctl(SIOCGIFHWADDR)");
        return -1;
    }
    memcpy(mac_out, ifr.ifr_hwaddr.sa_data, 6);
    return 0;
}

/* Розрахунок адреси Solicited-Node Multicast за цільовою IPv6 */
static void make_solicited_node_addr(const struct in6_addr *target, struct in6_addr *solicited_out) {
    inet_pton(AF_INET6, SOLICITED_NODE_PREFIX, solicited_out);
    /* Підставляємо молодші 24 біти (останні 3 байти) цільової адреси */
    solicited_out->s6_addr[13] = target->s6_addr[13];
    solicited_out->s6_addr[14] = target->s6_addr[14];
    solicited_out->s6_addr[15] = target->s6_addr[15];
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <інтерфейс> <цільова-IPv6-адреса>\n", argv[0]);
        return 1;
    }

    const char *ifname = argv[1];
    const char *target_ip_str = argv[2];

    struct in6_addr target_ip;
    if (inet_pton(AF_INET6, target_ip_str, &target_ip) != 1) {
        fprintf(stderr, "Помилка: некоректний формат IPv6-адреси: %s\n", target_ip_str);
        return 1;
    }

    unsigned int ifindex = if_nametoindex(ifname);
    if (ifindex == 0) {
        fprintf(stderr, "Помилка: не знайдено мережевий інтерфейс %s\n", ifname);
        return 1;
    }

    /* Створення raw-сокета для протоколу ICMPv6 */
    int sock = socket(AF_INET6, SOCK_RAW, IPPROTO_ICMPV6);
    if (sock < 0) {
        perror("socket(AF_INET6, SOCK_RAW, IPPROTO_ICMPV6)");
        fprintf(stderr, "Примітка: для роботи з сирими сокетами потрібні привілеї root (sudo).\n");
        return 1;
    }

    uint8_t local_mac[6];
    if (get_interface_mac(sock, ifname, local_mac) < 0) {
        close(sock);
        return 1;
    }

    /* Встановлення обов'язкового ліміту переходів Hop Limit = 255 */
    int hops = 255;
    if (setsockopt(sock, IPPROTO_IPV6, IPV6_MULTICAST_HOPS, &hops, sizeof(hops)) < 0) {
        perror("setsockopt(IPV6_MULTICAST_HOPS)");
        close(sock);
        return 1;
    }
    if (setsockopt(sock, IPPROTO_IPV6, IPV6_UNICAST_HOPS, &hops, sizeof(hops)) < 0) {
        perror("setsockopt(IPV6_UNICAST_HOPS)");
        close(sock);
        return 1;
    }

    /* Таймаут очікування відповіді на сокеті (2 секунди) */
    struct timeval tv = { .tv_sec = 2, .tv_usec = 0 };
    if (setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) < 0) {
        perror("setsockopt(SO_RCVTIMEO)");
        close(sock);
        return 1;
    }

    /* Прив'язка сокета до конкретного фізичного інтерфейсу */
    if (setsockopt(sock, SOL_SOCKET, SO_BINDTODEVICE, ifname, strlen(ifname)) < 0) {
        perror("setsockopt(SO_BINDTODEVICE)");
        close(sock);
        return 1;
    }

    /* Формування пакетного буфера: заголовок NS + опція Source Link-Layer */
    struct {
        struct nd_neighbor_solicit ns_hdr;
        struct nd_opt_hdr opt_hdr;
        uint8_t mac[6];
    } __attribute__((packed)) probe_pkt;

    memset(&probe_pkt, 0, sizeof(probe_pkt));
    probe_pkt.ns_hdr.nd_ns_type = ND_NEIGHBOR_SOLICIT;
    probe_pkt.ns_hdr.nd_ns_code = 0;
    probe_pkt.ns_hdr.nd_ns_target = target_ip;

    /* Опція 1: Source Link-Layer Address (довжина 1 блок = 8 байтів) */
    probe_pkt.opt_hdr.nd_opt_type = ND_OPT_SOURCE_LINKADDR;
    probe_pkt.opt_hdr.nd_opt_len = 1;
    memcpy(probe_pkt.mac, local_mac, 6);

    /* Формування адреси призначення */
    struct sockaddr_in6 dst_addr;
    memset(&dst_addr, 0, sizeof(dst_addr));
    dst_addr.sin6_family = AF_INET6;
    dst_addr.sin6_scope_id = ifindex;
    make_solicited_node_addr(&target_ip, &dst_addr.sin6_addr);

    char solicited_str[INET6_ADDRSTRLEN];
    inet_ntop(AF_INET6, &dst_addr.sin6_addr, solicited_str, sizeof(solicited_str));
    printf("Надсилання Neighbor Solicitation для %s на %s%%%s...\n",
           target_ip_str, solicited_str, ifname);

    ssize_t sent = sendto(sock, &probe_pkt, sizeof(probe_pkt), 0,
                          (struct sockaddr *)&dst_addr, sizeof(dst_addr));
    if (sent < 0) {
        perror("sendto");
        close(sock);
        return 1;
    }

    /* Цикл отримання та аналізу відповідей NA */
    uint8_t recv_buf[PACKET_BUFFER_SIZE];
    while (1) {
        struct sockaddr_in6 src_addr;
        socklen_t addr_len = sizeof(src_addr);
        ssize_t recvd = recvfrom(sock, recv_buf, sizeof(recv_buf), 0,
                                 (struct sockaddr *)&src_addr, &addr_len);
        if (recvd < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                fprintf(stderr, "Час очікування вичерпано: вузол %s не відповів.\n", target_ip_str);
            } else {
                perror("recvfrom");
            }
            close(sock);
            return 1;
        }

        if (recvd < (ssize_t)sizeof(struct nd_neighbor_advert)) {
            continue;
        }

        struct nd_neighbor_advert *na = (struct nd_neighbor_advert *)recv_buf;
        if (na->nd_na_type != ND_NEIGHBOR_ADVERT || na->nd_na_code != 0) {
            continue;
        }

        /* Звіряємо, чи це відповідь саме на нашу цільову адресу */
        if (memcmp(&na->nd_na_target, &target_ip, sizeof(struct in6_addr)) != 0) {
            continue;
        }

        char responder_ip[INET6_ADDRSTRLEN];
        inet_ntop(AF_INET6, &src_addr.sin6_addr, responder_ip, sizeof(responder_ip));

        printf("Отримано Neighbor Advertisement від %s!\n", responder_ip);
        printf("Прапорці: [Router=%d, Solicited=%d, Override=%d]\n",
               (na->nd_na_flags_reserved & ND_NA_FLAG_ROUTER) ? 1 : 0,
               (na->nd_na_flags_reserved & ND_NA_FLAG_SOLICITED) ? 1 : 0,
               (na->nd_na_flags_reserved & ND_NA_FLAG_OVERRIDE) ? 1 : 0);

        /* Парсинг ланцюжка опцій: шукаємо Target Link-Layer Address (Type 2) */
        uint8_t *opts = recv_buf + sizeof(struct nd_neighbor_advert);
        ssize_t opts_len = recvd - sizeof(struct nd_neighbor_advert);
        int mac_found = 0;

        while (opts_len >= 8) {
            uint8_t opt_type = opts[0];
            uint8_t opt_len_units = opts[1];
            if (opt_len_units == 0) break;
            size_t opt_bytes = (size_t)opt_len_units * 8;
            if (opt_bytes > (size_t)opts_len) break;

            if (opt_type == ND_OPT_TARGET_LINKADDR && opt_bytes >= 8) {
                uint8_t *target_mac = opts + 2;
                printf("Знайдено MAC-адресу: %02x:%02x:%02x:%02x:%02x:%02x\n",
                       target_mac[0], target_mac[1], target_mac[2],
                       target_mac[3], target_mac[4], target_mac[5]);
                mac_found = 1;
                break;
            }
            opts += opt_bytes;
            opts_len -= opt_bytes;
        }

        if (!mac_found) {
            printf("У відповіді NA відсутня опція Target Link-Layer Address.\n");
        }

        break;
    }

    close(sock);
    return 0;
}
