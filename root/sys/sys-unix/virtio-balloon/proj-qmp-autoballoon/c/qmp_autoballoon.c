/* qmp_autoballoon.c — демон автобалонінгу мовою C */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <stdint.h>

#define BUFFER_SIZE 4096
#define MIN_RAM_BYTES (2ULL * 1024 * 1024 * 1024) /* Мінімум 2 ГБ */
#define SAFETY_MARGIN_PERCENT 20

static int qmp_send_command(int fd, const char *cmd, char *response, size_t resp_len) {
    if (write(fd, cmd, strlen(cmd)) < 0) {
        perror("write to qmp socket failed");
        return -1;
    }
    ssize_t n = read(fd, response, resp_len - 1);
    if (n < 0) {
        perror("read from qmp socket failed");
        return -1;
    }
    response[n] = '\0';
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях_до_qmp_сокета>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *socket_path = argv[1];
    int sock_fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (sock_fd < 0) {
        perror("socket creation failed");
        return EXIT_FAILURE;
    }

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, socket_path, sizeof(addr.sun_path) - 1);

    if (connect(sock_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("connect to qmp failed");
        close(sock_fd);
        return EXIT_FAILURE;
    }

    char buf[BUFFER_SIZE];
    /* Читаємо вітальне повідомлення QMP */
    read(sock_fd, buf, sizeof(buf) - 1);

    /* 1. Узгодження можливостей QMP */
    const char *qmp_cap = "{\"execute\": \"qmp_capabilities\"}\n";
    if (qmp_send_command(sock_fd, qmp_cap, buf, sizeof(buf)) < 0) {
        close(sock_fd);
        return EXIT_FAILURE;
    }

    /* 2. Встановлюємо інтервал опитування statsq на 2 секунди */
    const char *set_poll = "{\"execute\": \"qom-set\", \"arguments\": "
                           "{\"path\": \"/machine/peripheral/balloon0\", "
                           "\"property\": \"guest-stats-polling-interval\", \"value\": 2}}\n";
    qmp_send_command(sock_fd, set_poll, buf, sizeof(buf));

    printf("[autoballoon] Демон успішно підключився до %s\n", socket_path);

    /* 3. Головний цикл моніторингу */
    while (1) {
        sleep(3);

        const char *get_stats = "{\"execute\": \"qom-get\", \"arguments\": "
                                "\"property\": \"guest-stats\", "
                                "\"path\": \"/machine/peripheral/balloon0\"}}\n";
        if (qmp_send_command(sock_fd, get_stats, buf, sizeof(buf)) < 0)
            break;

        /* Спрощений пошук числових полів у відповіді JSON */
        char *p_total = strstr(buf, "\"stat-total-memory\":");
        char *p_avail = strstr(buf, "\"stat-available-memory\":");

        if (p_total && p_avail) {
            uint64_t total_mem = strtoull(p_total + 20, NULL, 10);
            uint64_t avail_mem = strtoull(p_avail + 24, NULL, 10);

            if (total_mem > 0 && avail_mem > 0) {
                uint64_t used_mem = total_mem - avail_mem;
                uint64_t safety = (total_mem * SAFETY_MARGIN_PERCENT) / 100;
                uint64_t target_mem = used_mem + safety;

                if (target_mem < MIN_RAM_BYTES)
                    target_mem = MIN_RAM_BYTES;
                if (target_mem > total_mem)
                    target_mem = total_mem;

                printf("[autoballoon] Total: %lu МБ, Avail: %lu МБ -> Target: %lu МБ\n",
                       total_mem / (1024 * 1024), avail_mem / (1024 * 1024),
                       target_mem / (1024 * 1024));

                char cmd[256];
                snprintf(cmd, sizeof(cmd),
                         "{\"execute\": \"balloon\", \"arguments\": {\"value\": %lu}}\n",
                         target_mem);
                qmp_send_command(sock_fd, cmd, buf, sizeof(buf));
            }
        }
    }

    close(sock_fd);
    return EXIT_SUCCESS;
}
