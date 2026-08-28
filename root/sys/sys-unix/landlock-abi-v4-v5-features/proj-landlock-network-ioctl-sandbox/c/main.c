#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/ioctl.h>
#include <linux/landlock.h>

#ifndef LANDLOCK_ACCESS_NET_BIND_TCP
#define LANDLOCK_ACCESS_NET_BIND_TCP (1ULL << 0)
#define LANDLOCK_ACCESS_NET_CONNECT_TCP (1ULL << 1)
#endif

#ifndef LANDLOCK_ACCESS_FS_IOCTL_DEV
#define LANDLOCK_ACCESS_FS_IOCTL_DEV (1ULL << 15)
#endif

#ifndef LANDLOCK_RULE_NET_PORT
#define LANDLOCK_RULE_NET_PORT 2
struct landlock_net_port_attr {
    __u64 allowed_access;
    __u64 port;
};
#endif

static inline int sys_landlock_create_ruleset(const struct landlock_ruleset_attr *attr, size_t size, __u32 flags) {
    return syscall(__NR_landlock_create_ruleset, attr, size, flags);
}

static inline int sys_landlock_add_rule(int ruleset_fd, enum landlock_rule_type rule_type, const void *rule_attr, __u32 flags) {
    return syscall(__NR_landlock_add_rule, ruleset_fd, rule_type, rule_attr, flags);
}

static inline int sys_landlock_restrict_self(int ruleset_fd, __u32 flags) {
    return syscall(__NR_landlock_restrict_self, ruleset_fd, flags);
}

int apply_sandbox(uint16_t allowed_port, const char *allowed_dir) {
    int abi = sys_landlock_create_ruleset(NULL, 0, LANDLOCK_CREATE_RULESET_VERSION);
    if (abi < 1) {
        fprintf(stderr, "Landlock не підтримується ядром (abi=%d)\n", abi);
        return -1;
    }
    printf("Landlock ABI версія: %d\n", abi);

    struct landlock_ruleset_attr attr;
    memset(&attr, 0, sizeof(attr));

    attr.handled_access_fs = LANDLOCK_ACCESS_FS_READ_FILE | LANDLOCK_ACCESS_FS_READ_DIR;
    if (abi >= 5) {
        attr.handled_access_fs |= LANDLOCK_ACCESS_FS_IOCTL_DEV;
    }

    if (abi >= 4) {
        attr.handled_access_net = LANDLOCK_ACCESS_NET_BIND_TCP | LANDLOCK_ACCESS_NET_CONNECT_TCP;
    }

    int ruleset_fd = sys_landlock_create_ruleset(&attr, sizeof(attr), 0);
    if (ruleset_fd < 0) {
        perror("landlock_create_ruleset");
        return -1;
    }

    /* Додавання правила VFS */
    int dir_fd = open(allowed_dir, O_PATH | O_CLOEXEC);
    if (dir_fd >= 0) {
        struct landlock_path_beneath_attr path_attr = {
            .allowed_access = LANDLOCK_ACCESS_FS_READ_FILE | LANDLOCK_ACCESS_FS_READ_DIR,
            .parent_fd = dir_fd,
        };
        if (sys_landlock_add_rule(ruleset_fd, LANDLOCK_RULE_PATH_BENEATH, &path_attr, 0) < 0) {
            perror("landlock_add_rule path");
            close(dir_fd);
            close(ruleset_fd);
            return -1;
        }
        close(dir_fd);
    }

    /* Додавання правила Мережі (ABI v4+) */
    if (abi >= 4) {
        struct landlock_net_port_attr net_attr = {
            .allowed_access = LANDLOCK_ACCESS_NET_BIND_TCP,
            .port = allowed_port,
        };
        if (sys_landlock_add_rule(ruleset_fd, LANDLOCK_RULE_NET_PORT, &net_attr, 0) < 0) {
            perror("landlock_add_rule net");
            close(ruleset_fd);
            return -1;
        }
    }

    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) < 0) {
        perror("prctl NO_NEW_PRIVS");
        close(ruleset_fd);
        return -1;
    }

    if (sys_landlock_restrict_self(ruleset_fd, 0) < 0) {
        perror("landlock_restrict_self");
        close(ruleset_fd);
        return -1;
    }

    close(ruleset_fd);
    printf("Пісочницю успішно застосовано!\n");
    return 0;
}

int main(void) {
    if (apply_sandbox(8080, "/tmp") < 0) {
        return EXIT_FAILURE;
    }

    /* Перевірка 1: bind на дозволений порт 8080 */
    int s1 = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in addr1 = { .sin_family = AF_INET, .sin_port = htons(8080) };
    if (bind(s1, (struct sockaddr *)&addr1, sizeof(addr1)) == 0) {
        printf("УСПІХ: bind(8080) дозволено\n");
    } else {
        printf("ПОМИЛКА: bind(8080) відхилено: %s\n", strerror(errno));
    }
    close(s1);

    /* Перевірка 2: bind на заблокований порт 9090 */
    int s2 = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in addr2 = { .sin_family = AF_INET, .sin_port = htons(9090) };
    if (bind(s2, (struct sockaddr *)&addr2, sizeof(addr2)) < 0 && errno == EACCES) {
        printf("УСПІХ: bind(9090) заблоковано ядром (EACCES)\n");
    }
    close(s2);

    return EXIT_SUCCESS;
}
