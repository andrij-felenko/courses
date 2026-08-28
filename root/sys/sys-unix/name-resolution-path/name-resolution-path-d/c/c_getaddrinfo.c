/* c_getaddrinfo.c — Використання POSIX getaddrinfo() у C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <netdb.h>
#include <arpa/inet.h>

int resolve_host(const char *hostname) {
    struct addrinfo hints;
    struct addrinfo *result = NULL;
    struct addrinfo *rp = NULL;

    memset(&hints, 0, sizeof(struct addrinfo));
    hints.ai_family = AF_UNSPEC;    /* Дозволяємо IPv4 та IPv6 */
    hints.ai_socktype = SOCK_STREAM; /* Потоковий TCP сокет */

    int s = getaddrinfo(hostname, "80", &hints, &result);
    if (s != 0) {
        fprintf(stderr, "Помилка getaddrinfo: %s\n", gai_strerror(s));
        return -1;
    }

    for (rp = result; rp != NULL; rp = rp->ai_next) {
        void *addr = NULL;
        char ipstr[INET6_ADDRSTRLEN];

        if (rp->ai_family == AF_INET) {
            struct sockaddr_in *ipv4 = (struct sockaddr_in *)rp->ai_addr;
            addr = &(ipv4->sin_addr);
        } else {
            struct sockaddr_in6 *ipv6 = (struct sockaddr_in6 *)rp->ai_addr;
            addr = &(ipv6->sin6_addr);
        }

        inet_ntop(rp->ai_family, addr, ipstr, sizeof(ipstr));
        printf("Знайдено адресу: %s (Family: %d)\n", ipstr, rp->ai_family);
    }

    freeaddrinfo(result);
    return 0;
}
