#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <linux/if.h>
#include <net/if.h>

#define NLMSG_BUF_SIZE 4096

/* Створення та прив'язка сокета Netlink */
static int open_netlink_socket(void) {
    int fd = socket(AF_NETLINK, SOCK_RAW | SOCK_CLOEXEC, NETLINK_ROUTE);
    if (fd < 0) {
        perror("Помилка створення сокета netlink");
        return -1;
    }

    struct sockaddr_nl sa;
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;

    if (bind(fd, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("Помилка прив'язки сокета netlink");
        close(fd);
        return -1;
    }
    return fd;
}

/* Додавання TLV-атрибута rtattr до буфера повідомлення з вирівнюванням */
static int add_rtattr(struct nlmsghdr *n, size_t maxlen, unsigned short type, const void *data, size_t datalen) {
    size_t len = RTA_LENGTH(datalen);
    if (NLMSG_ALIGN(n->nlmsg_len) + RTA_ALIGN(len) > maxlen) {
        fprintf(stderr, "Помилка: переповнення буфера rtattr\n");
        return -1;
    }
    struct rtattr *rta = (struct rtattr *)(((char *)n) + NLMSG_ALIGN(n->nlmsg_len));
    rta->rta_type = type;
    rta->rta_len = len;
    memcpy(RTA_DATA(rta), data, datalen);
    n->nlmsg_len = NLMSG_ALIGN(n->nlmsg_len) + RTA_ALIGN(len);
    return 0;
}

/* Читання відповіді ACK від ядра */
static int read_netlink_ack(int fd, uint32_t seq) {
    char buf[NLMSG_BUF_SIZE];
    ssize_t res = recv(fd, buf, sizeof(buf), 0);
    if (res < 0) {
        perror("Помилка отримання відповіді від netlink");
        return -errno;
    }

    struct nlmsghdr *h = (struct nlmsghdr *)buf;
    if (!NLMSG_OK(h, (size_t)res)) {
        fprintf(stderr, "Некоректне або пошкоджене повідомлення Netlink\n");
        return -EBADMSG;
    }

    if (h->nlmsg_type == NLMSG_ERROR) {
        struct nlmsgerr *err = (struct nlmsgerr *)NLMSG_DATA(h);
        if (h->nlmsg_len < NLMSG_LENGTH(sizeof(struct nlmsgerr))) {
            fprintf(stderr, "Помилка Netlink: усічене повідомлення\n");
            return -EBADMSG;
        }
        return err->error; /* 0 — успіх (ACK), від'ємне значення — код помилки ядра */
    }
    return 0;
}

/* Перейменування мережевого інтерфейсу через RTM_SETLINK */
int rename_network_interface(const char *old_name, const char *new_name) {
    if (!old_name || !new_name || strlen(new_name) >= IFNAMSIZ) {
        fprintf(stderr, "Некоректна назва: довжина має бути від 1 до %d символів\n", IFNAMSIZ - 1);
        return -EINVAL;
    }

    unsigned int ifindex = if_nametoindex(old_name);
    if (ifindex == 0) {
        fprintf(stderr, "Інтерфейс '%s' не знайдено в системі\n", old_name);
        return -ENODEV;
    }

    int nl_fd = open_netlink_socket();
    if (nl_fd < 0) return -1;

    char req_buf[NLMSG_BUF_SIZE];
    memset(req_buf, 0, sizeof(req_buf));

    struct nlmsghdr *n = (struct nlmsghdr *)req_buf;
    n->nlmsg_len = NLMSG_LENGTH(sizeof(struct ifinfomsg));
    n->nlmsg_flags = NLM_F_REQUEST | NLM_F_ACK;
    n->nlmsg_type = RTM_SETLINK;
    n->nlmsg_seq = 1001;

    struct ifinfomsg *ifi = (struct ifinfomsg *)NLMSG_DATA(n);
    ifi->ifi_family = AF_UNSPEC;
    ifi->ifi_index = (int)ifindex;

    /* Додаємо нове основне ім'я */
    if (add_rtattr(n, sizeof(req_buf), IFLA_IFNAME, new_name, strlen(new_name) + 1) < 0) {
        close(nl_fd);
        return -1;
    }

    struct sockaddr_nl sa;
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;

    if (sendto(nl_fd, n, n->nlmsg_len, 0, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("Помилка надсилання запиту Netlink");
        close(nl_fd);
        return -errno;
    }

    int err = read_netlink_ack(nl_fd, n->nlmsg_seq);
    close(nl_fd);

    if (err < 0) {
        fprintf(stderr, "Ядро відхилило операцію перейменування: %s (%d)\n", strerror(-err), -err);
        return err;
    }

    printf("Інтерфейс успішно перейменовано: %s -> %s (ifindex: %u)\n", old_name, new_name, ifindex);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Використання: %s <старе_ім'я> <нове_ім'я>\n", argv[0]);
        return EXIT_FAILURE;
    }

    int rc = rename_network_interface(argv[1], argv[2]);
    return (rc == 0) ? EXIT_SUCCESS : EXIT_FAILURE;
}
