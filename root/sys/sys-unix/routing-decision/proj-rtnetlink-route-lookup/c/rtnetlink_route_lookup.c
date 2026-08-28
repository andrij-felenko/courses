/*
 * rtnetlink_route_lookup.c
 * Системна програма мовою C для запиту та моніторингу маршрутів через NETLINK_ROUTE.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <linux/rtnetlink.h>

#define BUFFER_SIZE 8192

/* Структура для запиту маршруту до ядра */
struct route_request {
    struct nlmsghdr nl;
    struct rtmsg    rt;
    char            buf[128];
};

/* Допоміжна функція додавання атрибута TLV */
static void add_attr_var(struct nlmsghdr *n, int maxlen, int type, const void *data, int alen) {
    int len = RTA_LENGTH(alen);
    struct rtattr *rta;

    if (NLMSG_ALIGN(n->nlmsg_len) + RTA_ALIGN(len) > maxlen) {
        fprintf(stderr, "Помилка: буфер Netlink переповнено\n");
        return;
    }
    rta = (struct rtattr *)(((char *)n) + NLMSG_ALIGN(n->nlmsg_len));
    rta->rta_type = type;
    rta->rta_len = len;
    memcpy(RTA_DATA(rta), data, alen);
    n->nlmsg_len = NLMSG_ALIGN(n->nlmsg_len) + RTA_ALIGN(len);
}

/* Парсинг атрибутів RTA у відповіді ядра */
static void parse_route_response(struct nlmsghdr *nlh) {
    struct rtmsg *rt = (struct rtmsg *)NLMSG_DATA(nlh);
    struct rtattr *rta = (struct rtattr *)RTM_RTA(rt);
    int rtl = RTM_PAYLOAD(nlh);

    char dst_str[INET_ADDRSTRLEN] = "default";
    char gw_str[INET_ADDRSTRLEN] = "none";
    char src_str[INET_ADDRSTRLEN] = "none";
    int oif = 0;

    for (; RTA_OK(rta, rtl); rta = RTA_NEXT(rta, rtl)) {
        switch (rta->rta_type) {
            case RTA_DST:
                inet_ntop(AF_INET, RTA_DATA(rta), dst_str, sizeof(dst_str));
                break;
            case RTA_GATEWAY:
                inet_ntop(AF_INET, RTA_DATA(rta), gw_str, sizeof(gw_str));
                break;
            case RTA_PREFSRC:
                inet_ntop(AF_INET, RTA_DATA(rta), src_str, sizeof(src_str));
                break;
            case RTA_OIF:
                oif = *(int *)RTA_DATA(rta);
                break;
        }
    }

    char ifname[IF_NAMESIZE] = "unknown";
    if (oif > 0) {
        if_indextoname(oif, ifname);
    }

    printf("[ROUTE] Призначення: %s/%d | Шлюз: %s | Джерело: %s | Інтерфейс: %s (%d)\n",
           dst_str, rt->rtm_dst_len, gw_str, src_str, ifname, oif);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <Destination IPv4>\n", argv[0]);
        return EXIT_FAILURE;
    }

    struct in_addr dst_addr;
    if (inet_pton(AF_INET, argv[1], &dst_addr) <= 0) {
        fprintf(stderr, "Некоректна IP-адреса: %s\n", argv[1]);
        return EXIT_FAILURE;
    }

    int fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);
    if (fd < 0) {
        perror("Помилка створення socket(AF_NETLINK)");
        return EXIT_FAILURE;
    }

    /* Прив'язка до сокета та підписка на події маршрутизації */
    struct sockaddr_nl sa;
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;
    sa.nl_groups = RTMGRP_IPV4_ROUTE;

    if (bind(fd, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("Помилка bind()");
        close(fd);
        return EXIT_FAILURE;
    }

    /* Формування запиту RTM_GETROUTE */
    struct route_request req;
    memset(&req, 0, sizeof(req));
    req.nl.nlmsg_len = NLMSG_LENGTH(sizeof(struct rtmsg));
    req.nl.nlmsg_flags = NLM_F_REQUEST;
    req.nl.nlmsg_type = RTM_GETROUTE;
    req.rt.rtm_family = AF_INET;
    req.rt.rtm_dst_len = 32;

    add_attr_var(&req.nl, sizeof(req), RTA_DST, &dst_addr, sizeof(dst_addr));

    if (send(fd, &req, req.nl.nlmsg_len, 0) < 0) {
        perror("Помилка send()");
        close(fd);
        return EXIT_FAILURE;
    }

    printf("Надіслано запит RTM_GETROUTE для IP: %s\n", argv[1]);

    /* Отримання відповіді та слухання асинхронних подій */
    char buffer[BUFFER_SIZE];
    while (1) {
        ssize_t len = recv(fd, buffer, sizeof(buffer), 0);
        if (len < 0) {
            perror("Помилка recv()");
            break;
        }

        struct nlmsghdr *nlh = (struct nlmsghdr *)buffer;
        for (; NLMSG_OK(nlh, len); nlh = NLMSG_NEXT(nlh, len)) {
            if (nlh->nlmsg_type == NLMSG_DONE) {
                break;
            }
            if (nlh->nlmsg_type == NLMSG_ERROR) {
                fprintf(stderr, "Отримано помилку від ядра Netlink\n");
                break;
            }
            if (nlh->nlmsg_type == RTM_NEWROUTE || nlh->nlmsg_type == RTM_DELROUTE) {
                printf("%s ", (nlh->nlmsg_type == RTM_NEWROUTE) ? "[NEW]" : "[DEL]");
                parse_route_response(nlh);
            }
        }
    }

    close(fd);
    return EXIT_SUCCESS;
}
