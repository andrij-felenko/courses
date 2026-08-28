/* devtmpfs_inspector.c — Перехоплення uevent та перевірка вузлів у devtmpfs (C) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <linux/netlink.h>

#define UEVENT_BUFFER_SIZE 8192

static void inspect_devtmpfs_node(const char *devname, unsigned int expected_maj, unsigned int expected_min) {
    char full_path[512];
    struct stat st;

    snprintf(full_path, sizeof(full_path), "/dev/%s", devname);

    /* Використовуємо lstat, щоб не слідувати за можливими символьними посиланнями */
    if (lstat(full_path, &st) < 0) {
        fprintf(stderr, "  [VFS Check] Failed to lstat path %s: %s (node missing in devtmpfs)\n",
                full_path, strerror(errno));
        return;
    }

    unsigned int actual_maj = major(st.st_rdev);
    unsigned int actual_min = minor(st.st_rdev);

    const char *type_str = S_ISCHR(st.st_mode) ? "CHARACTER" :
                           S_ISBLK(st.st_mode) ? "BLOCK" : "OTHER";

    printf("  [VFS Check] Path: %s\n", full_path);
    printf("              Type: %s | Mode: 0%o | UID: %d | GID: %d\n",
           type_str, st.st_mode & 07777, st.st_uid, st.st_gid);
    printf("              Major:Minor -> Kernel: %u:%u | devtmpfs: %u:%u\n",
           expected_maj, expected_min, actual_maj, actual_min);

    if (actual_maj == expected_maj && actual_min == expected_min) {
        printf("              STATUS: MATCH (devtmpfs node verified successfully)\n");
    } else {
        printf("              STATUS: MISMATCH (Kernel and devtmpfs dev_t differ!)\n");
    }
}

int main(void) {
    int fd = socket(PF_NETLINK, SOCK_RAW, NETLINK_KOBJECT_UEVENT);
    if (fd < 0) {
        perror("socket(PF_NETLINK) failed");
        return EXIT_FAILURE;
    }

    /* Налаштовуємо більший розмір приймального буфера сокета */
    int rcvbuf = 1024 * 1024;
    if (setsockopt(fd, SOL_SOCKET, SO_RCVBUFFORCE, &rcvbuf, sizeof(rcvbuf)) < 0) {
        setsockopt(fd, SOL_SOCKET, SO_RCVBUF, &rcvbuf, sizeof(rcvbuf));
    }

    struct sockaddr_nl sa;
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;
    sa.nl_groups = 1; /* Kernel Multicast uevents group */

    if (bind(fd, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("bind failed");
        close(fd);
        return EXIT_FAILURE;
    }

    printf("=== Listening for Kernel Uevents and inspecting devtmpfs (/dev) ===\n");

    char buffer[UEVENT_BUFFER_SIZE];
    while (1) {
        ssize_t len = recv(fd, buffer, sizeof(buffer) - 1, 0);
        if (len <= 0) {
            if (len < 0 && errno == EINTR) continue;
            perror("recv failed");
            break;
        }

        buffer[len] = '\0';

        char *action = NULL;
        char *devname = NULL;
        unsigned int maj = 0, min = 0;

        char *ptr = buffer;
        while (ptr < buffer + len) {
            if (strncmp(ptr, "ACTION=", 7) == 0) action = ptr + 7;
            else if (strncmp(ptr, "DEVNAME=", 8) == 0) devname = ptr + 8;
            else if (strncmp(ptr, "MAJOR=", 6) == 0) maj = (unsigned int)atoi(ptr + 6);
            else if (strncmp(ptr, "MINOR=", 6) == 0) min = (unsigned int)atoi(ptr + 6);

            ptr += strlen(ptr) + 1;
        }

        if (action && devname) {
            printf("\n[NETLINK Event] Action: %s | Devname: %s | DevT: %u:%u\n",
                   action, devname, maj, min);

            if (strcmp(action, "add") == 0) {
                /* Оборонна пауза: ядро гарантує, що вузол уже створено (див. розбір нижче) */
                usleep(1000);
                inspect_devtmpfs_node(devname, maj, min);
            }
        }
    }

    close(fd);
    return EXIT_SUCCESS;
}
