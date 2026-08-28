#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <netdb.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <poll.h>

#define CONNECT_TIMEOUT_MS 3000
#define BANNER_TIMEOUT_MS  2000
#define BUFFER_SIZE        512

typedef struct {
    char ip_str[INET6_ADDRSTRLEN];
    int family;
    int error_stage; // 1: DNS, 2: Connect, 3: Banner, 0: OK
    int sys_errno;
    char banner[BUFFER_SIZE];
} ProbeResult;

static int set_nonblocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags == -1) return -1;
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

int probe_target(const char *host, const char *port_str, ProbeResult *res) {
    memset(res, 0, sizeof(*res));
    
    // Крок 1: Розв'язання імені через NSS / DNS
    struct addrinfo hints;
    struct addrinfo *addr_list = NULL;
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_UNSPEC;     // IPv4 або IPv6
    hints.ai_socktype = SOCK_STREAM; // TCP
    hints.ai_protocol = IPPROTO_TCP;

    int gai_rc = getaddrinfo(host, port_str, &hints, &addr_list);
    if (gai_rc != 0) {
        res->error_stage = 1;
        res->sys_errno = gai_rc;
        return -1;
    }

    int sockfd = -1;
    int connect_success = 0;
    struct addrinfo *rp = NULL;

    // Перебір знайдених IP-адрес
    for (rp = addr_list; rp != NULL; rp = rp->ai_next) {
        void *raw_addr = NULL;
        if (rp->ai_family == AF_INET) {
            raw_addr = &((struct sockaddr_in *)rp->ai_addr)->sin_addr;
        } else if (rp->ai_family == AF_INET6) {
            raw_addr = &((struct sockaddr_in6 *)rp->ai_addr)->sin6_addr;
        }
        inet_ntop(rp->ai_family, raw_addr, res->ip_str, sizeof(res->ip_str));
        res->family = rp->ai_family;

        sockfd = socket(rp->ai_family, rp->ai_socktype, rp->ai_protocol);
        if (sockfd < 0) {
            continue;
        }

        if (set_nonblocking(sockfd) < 0) {
            close(sockfd);
            sockfd = -1;
            continue;
        }

        // Крок 2 та 3: Неблокуюче підключення TCP
        int rc = connect(sockfd, rp->ai_addr, rp->ai_addrlen);
        if (rc == 0) {
            // Миттєве підключення (типово для loopback)
            connect_success = 1;
            break;
        }

        if (errno == EINPROGRESS) {
            struct pollfd pfd;
            pfd.fd = sockfd;
            pfd.events = POLLOUT | POLLERR | POLLHUP;
            pfd.revents = 0;

            int poll_rc;
            do {
                poll_rc = poll(&pfd, 1, CONNECT_TIMEOUT_MS);
            } while (poll_rc < 0 && errno == EINTR);

            if (poll_rc > 0) {
                int sock_err = 0;
                socklen_t opt_len = sizeof(sock_err);
                if (getsockopt(sockfd, SOL_SOCKET, SO_ERROR, &sock_err, &opt_len) < 0) {
                    res->sys_errno = errno;
                } else if (sock_err != 0) {
                    res->sys_errno = sock_err; // ECONNREFUSED, ETIMEDOUT, EHOSTUNREACH
                } else {
                    connect_success = 1;
                    break;
                }
            } else if (poll_rc == 0) {
                res->sys_errno = ETIMEDOUT; // Таймаут очікування SYN-ACK
            } else {
                res->sys_errno = errno;
            }
        } else {
            res->sys_errno = errno; // ENETUNREACH або EHOSTUNREACH
        }

        close(sockfd);
        sockfd = -1;
    }

    freeaddrinfo(addr_list);

    if (!connect_success) {
        res->error_stage = 2;
        return -1;
    }

    // Крок 4: Перевірка прикладного рівня L7 (зчитування банера)
    struct pollfd pfd_read;
    pfd_read.fd = sockfd;
    pfd_read.events = POLLIN;
    pfd_read.revents = 0;

    int poll_read_rc;
    do {
        poll_read_rc = poll(&pfd_read, 1, BANNER_TIMEOUT_MS);
    } while (poll_read_rc < 0 && errno == EINTR);

    if (poll_read_rc > 0 && (pfd_read.revents & POLLIN)) {
        ssize_t n = read(sockfd, res->banner, sizeof(res->banner) - 1);
        if (n > 0) {
            res->banner[n] = '\0';
            // Видаляємо кінцеві перенесення рядків
            char *newline = strpbrk(res->banner, "\r\n");
            if (newline) *newline = '\0';
        }
    } else {
        snprintf(res->banner, sizeof(res->banner), "(сервер мовчить, немає початкового банера)");
    }

    close(sockfd);
    res->error_stage = 0;
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <host> <port>\n", argv[0]);
        return 1;
    }

    const char *target_host = argv[1];
    const char *target_port = argv[2];
    ProbeResult res;

    printf("=== ДІАГНОСТИКА ЗВ'ЯЗКУ: %s:%s ===\n", target_host, target_port);

    int rc = probe_target(target_host, target_port, &res);
    if (rc == 0) {
        printf("[+] Рівень 1 (DNS):   Успіх -> IP-адреса %s (%s)\n",
               res.ip_str, res.family == AF_INET ? "IPv4" : "IPv6");
        printf("[+] Рівень 2-3 (TCP): З'єднання встановлено (порт %s відкритий)\n", target_port);
        printf("[+] Рівень 4 (L7):    Банер служби: \"%s\"\n", res.banner);
        printf("\nРЕЗУЛЬТАТ: Вузол повністю доступний.\n");
        return 0;
    }

    printf("[-] Помилка на стадії %d:\n", res.error_stage);
    if (res.error_stage == 1) {
        printf("    Стадія 1 (Розпізнавання імені DNS/NSS):\n");
        printf("    Код помилки: %s\n", gai_strerror(res.sys_errno));
        printf("    Рекомендація: Перевірте /etc/resolv.conf, systemd-resolved та правильність імені.\n");
    } else if (res.error_stage == 2) {
        printf("    Стадія 2-3 (Маршрутизація / TCP Транспорт):\n");
        printf("    Цільова IP-адреса: %s\n", res.ip_str[0] ? res.ip_str : "(невідома)");
        printf("    Системна помилка errno %d: %s\n", res.sys_errno, strerror(res.sys_errno));
        if (res.sys_errno == ECONNREFUSED) {
            printf("    Аналіз: Отримано TCP RST. Сервіс не запущено або порт слухається лише на 127.0.0.1.\n");
        } else if (res.sys_errno == ETIMEDOUT) {
            printf("    Аналіз: Мовчазний DROP пакета. Перевірте nftables, Security Group або маршрутизатор.\n");
        } else if (res.sys_errno == ENETUNREACH || res.sys_errno == EHOSTUNREACH) {
            printf("    Аналіз: Відсутній маршрут у ядрі або L2-сусід не відповідає на ARP-запити.\n");
        }
    }

    return 2;
}
