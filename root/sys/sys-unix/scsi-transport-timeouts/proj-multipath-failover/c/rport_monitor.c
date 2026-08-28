/* rport_monitor.c — відстеження подій SCSI транспорту через Netlink uevent.
 * Складання: gcc -O2 -Wall -Wextra rport_monitor.c -o rport_monitor
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <time.h>
#include <sys/socket.h>
#include <linux/netlink.h>

#define UEVENT_BUFFER_SIZE 4096

static void log_timestamp(void) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    struct tm tm_info;
    localtime_r(&ts.tv_sec, &tm_info);
    char buf[64];
    strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", &tm_info);
    printf("[%s.%03ld] ", buf, ts.tv_nsec / 1000000L);
}

static void read_sysfs_attr(const char *devpath, const char *attr, char *out, size_t out_len) {
    char full_path[512];
    snprintf(full_path, sizeof(full_path), "/sys%s/%s", devpath, attr);
    int fd = open(full_path, O_RDONLY);
    if (fd < 0) {
        snprintf(out, out_len, "<недоступно>");
        return;
    }
    ssize_t n = read(fd, out, out_len - 1);
    close(fd);
    if (n > 0) {
        if (out[n - 1] == '\n') {
            out[n - 1] = '\0';
        } else {
            out[n] = '\0';
        }
    } else {
        snprintf(out, out_len, "<порожньо>");
    }
}

int main(void) {
    int sock_fd = socket(AF_NETLINK, SOCK_RAW | SOCK_CLOEXEC, NETLINK_KOBJECT_UEVENT);
    if (sock_fd < 0) {
        perror("Помилка створення сокета Netlink");
        return 1;
    }

    struct sockaddr_nl sa;
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;
    sa.nl_groups = 1; /* Отримувати широкомовні uevents */

    if (bind(sock_fd, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("Помилка прив'язки сокета (bind)");
        close(sock_fd);
        return 1;
    }

    printf("=== Запущено моніторинг подій SCSI транспорту (fc_remote_ports / iscsi_session) ===\n");
    printf("Очікування подій ядра... Для виходу натисніть Ctrl+C\n\n");

    char buffer[UEVENT_BUFFER_SIZE];

    while (1) {
        ssize_t len = recv(sock_fd, buffer, sizeof(buffer) - 1, 0);
        if (len <= 0) {
            continue;
        }
        buffer[len] = '\0';

        char *action = NULL;
        char *devpath = NULL;
        char *subsystem = NULL;

        /* Повідомлення uevent складається з рядків, розділених нульовими байтами */
        char *ptr = buffer;
        while (ptr < buffer + len) {
            if (strncmp(ptr, "ACTION=", 7) == 0) {
                action = ptr + 7;
            } else if (strncmp(ptr, "DEVPATH=", 8) == 0) {
                devpath = ptr + 8;
            } else if (strncmp(ptr, "SUBSYSTEM=", 10) == 0) {
                subsystem = ptr + 10;
            }
            ptr += strlen(ptr) + 1;
        }

        if (subsystem && (strcmp(subsystem, "fc_remote_ports") == 0 ||
                          strcmp(subsystem, "iscsi_session") == 0)) {
            log_timestamp();
            printf("ПОДІЯ: дія=%s | підсистема=%s | шлях=%s\n",
                   action ? action : "?", subsystem, devpath ? devpath : "?");

            if (devpath && strcmp(subsystem, "fc_remote_ports") == 0) {
                char state[64], fast_io[32], dev_loss[32], port_name[64];
                read_sysfs_attr(devpath, "port_state", state, sizeof(state));
                read_sysfs_attr(devpath, "fast_io_fail_tmo", fast_io, sizeof(fast_io));
                read_sysfs_attr(devpath, "dev_loss_tmo", dev_loss, sizeof(dev_loss));
                read_sysfs_attr(devpath, "port_name", port_name, sizeof(port_name));

                printf("       └─ WWPN: %s | Стан: %s | fast_io_fail_tmo: %s с | dev_loss_tmo: %s с\n",
                       port_name, state, fast_io, dev_loss);
            } else if (devpath && strcmp(subsystem, "iscsi_session") == 0) {
                char state[64], recovery[32], target[128];
                read_sysfs_attr(devpath, "state", state, sizeof(state));
                read_sysfs_attr(devpath, "recovery_tmo", recovery, sizeof(recovery));
                read_sysfs_attr(devpath, "targetname", target, sizeof(target));

                printf("       └─ Target: %s | Стан: %s | recovery_tmo: %s с\n",
                       target, state, recovery);
            }
            fflush(stdout);
        }
    }

    close(sock_fd);
    return 0;
}
