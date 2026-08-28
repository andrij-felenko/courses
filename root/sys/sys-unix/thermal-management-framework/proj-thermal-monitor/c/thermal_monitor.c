/* thermal_monitor.c — Системний монітор термальних подій мовою C (POSIX & Netlink API) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/genetlink.h>
#include <linux/rtnetlink.h>
#include <linux/thermal.h>

#define BUFFER_SIZE 8192

/* Зчитування текстового атрибута з sysfs */
static int read_sysfs_string(const char *path, char *buf, size_t size) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) return -1;

    ssize_t bytes = read(fd, buf, size - 1);
    close(fd);
    if (bytes <= 0) return -1;

    buf[bytes] = '\0';
    char *newline = strchr(buf, '\n');
    if (newline) *newline = '\0';
    return 0;
}

/* Зчитування температури зони у градусах Цельсія */
static double read_zone_temperature(int zone_id) {
    char path[256];
    char buf[32];
    snprintf(path, sizeof(path), "/sys/class/thermal/thermal_zone%d/temp", zone_id);
    
    if (read_sysfs_string(path, buf, sizeof(buf)) == 0) {
        long temp_mC = atol(buf);
        return temp_mC / 1000.0;
    }
    return -1.0;
}

/* Створення та прив'язка Netlink-сокета */
static int create_thermal_netlink_socket(void) {
    int fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_GENERIC);
    if (fd < 0) {
        perror("Помилка створення AF_NETLINK сокета");
        return -1;
    }

    /* Збільшення сокетного буфера прийому для запобігання ENOBUFS */
    int rcvbuf = 256 * 1024;
    setsockopt(fd, SOL_SOCKET, SO_RCVBUF, &rcvbuf, sizeof(rcvbuf));

    struct sockaddr_nl local;
    memset(&local, 0, sizeof(local));
    local.nl_family = AF_NETLINK;
    local.nl_groups = 1; /* Підписка на мультикаст події */

    if (bind(fd, (struct sockaddr *)&local, sizeof(local)) < 0) {
        perror("Помилка прив'язки bind() сокета Netlink");
        close(fd);
        return -1;
    }

    return fd;
}

/* Розбір бінарного термального повідомлення Netlink */
static void parse_thermal_nl_message(const char *buf, ssize_t len) {
    struct nlmsghdr *nlh = (struct nlmsghdr *)buf;

    while (NLMSG_OK(nlh, len)) {
        if (nlh->nlmsg_type == NLMSG_ERROR) {
            fprintf(stderr, "Отримано повідомлення про помилку Netlink\n");
            break;
        }

        struct genlmsghdr *gnlh = (struct genlmsghdr *)NLMSG_DATA(nlh);
        printf("[Netlink Event] Команда події: 0x%X (Версія %d)\n",
               gnlh->cmd, gnlh->version);

        /* Інспекція додаткових атрибутів події.
           Розкладка struct nlattr збігається зі struct rtattr (u16 довжина, u16 тип),
           тож обхід робимо макросами RTA_*, які працюють саме зі struct rtattr. */
        struct rtattr *attr = (struct rtattr *)((char *)gnlh + GENL_HDRLEN);
        int attr_len = nlh->nlmsg_len - NLMSG_HDRLEN - GENL_HDRLEN;

        while (RTA_OK(attr, attr_len)) {
            if (attr->rta_type == THERMAL_GENL_ATTR_TZ_TEMP) {
                int temp_mC = *(int *)RTA_DATA(attr);
                printf("  -> Подія температури зони: %.2f °C\n", temp_mC / 1000.0);
            }
            attr = RTA_NEXT(attr, attr_len);
        }

        nlh = NLMSG_NEXT(nlh, len);
    }
}

int main(void) {
    printf("=== Термальний монітор ядра Linux (C POSIX / Netlink) ===\n\n");

    /* 1. Сканування перших двох термальних зон у sysfs */
    for (int zone = 0; zone < 2; zone++) {
        char type_path[256], type_buf[64];
        snprintf(type_path, sizeof(type_path), "/sys/class/thermal/thermal_zone%d/type", zone);

        if (read_sysfs_string(type_path, type_buf, sizeof(type_buf)) == 0) {
            double temp_C = read_zone_temperature(zone);
            printf("Зона %d [%s]: поточна температура = %.2f °C\n", zone, type_buf, temp_C);
        }
    }

    /* 2. Ініціалізація Netlink-сокета для асинхронного відстеження */
    int nl_fd = create_thermal_netlink_socket();
    if (nl_fd < 0) {
        fprintf(stderr, "Продовження роботи у режимі лише sysfs...\n");
        return EXIT_FAILURE;
    }

    printf("\nОчікування асинхронних подій перегріву ядра (Ctrl+C для виходу)...\n");
    char buffer[BUFFER_SIZE];

    while (1) {
        ssize_t bytes_received = recv(nl_fd, buffer, sizeof(buffer), 0);
        if (bytes_received < 0) {
            if (errno == EINTR) continue;
            perror("Помилка читання recv() з Netlink-сокета");
            break;
        }

        parse_thermal_nl_message(buffer, bytes_received);
    }

    close(nl_fd);
    return EXIT_SUCCESS;
}
