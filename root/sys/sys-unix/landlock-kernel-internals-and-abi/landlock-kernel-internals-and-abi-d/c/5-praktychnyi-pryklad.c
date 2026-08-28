#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <linux/landlock.h>

#ifndef landlock_create_ruleset
static inline int landlock_create_ruleset(const struct landlock_ruleset_attr *attr,
                                          size_t size, uint32_t flags) {
    return syscall(SYS_landlock_create_ruleset, attr, size, flags);
}

static inline int landlock_add_rule(int ruleset_fd,
                                    enum landlock_rule_type rule_type,
                                    const void *rule_attr, uint32_t flags) {
    return syscall(SYS_landlock_add_rule, ruleset_fd, rule_type, rule_attr, flags);
}

static inline int landlock_restrict_self(int ruleset_fd, uint32_t flags) {
    return syscall(SYS_landlock_restrict_self, ruleset_fd, flags);
}
#endif

/* Допоміжна функція для додавання дозволу на шлях */
static int add_path_rule(int ruleset_fd, const char *path, __u64 access_mask) {
    int fd = open(path, O_PATH | O_CLOEXEC);
    if (fd < 0) {
        /* Якщо каталог відсутній у системі, ігноруємо його */
        return 0;
    }

    struct landlock_path_beneath_attr path_attr = {
        .allowed_access = access_mask,
        .parent_fd = fd,
    };

    int res = landlock_add_rule(ruleset_fd, LANDLOCK_RULE_PATH_BENEATH, &path_attr, 0);
    close(fd);
    return res;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <команда> [аргументи...]\n", argv[0]);
        return 1;
    }

    /* 1. Перевірка версії ABI */
    int abi = landlock_create_ruleset(NULL, 0, LANDLOCK_CREATE_RULESET_VERSION);
    if (abi < 1) {
        perror("Landlock не підтримується ядром");
        return 1;
    }

    /* Маска дій для ABI 1 */
    __u64 handled_fs = LANDLOCK_ACCESS_FS_EXECUTE |
                       LANDLOCK_ACCESS_FS_WRITE_FILE |
                       LANDLOCK_ACCESS_FS_READ_FILE |
                       LANDLOCK_ACCESS_FS_READ_DIR |
                       LANDLOCK_ACCESS_FS_REMOVE_DIR |
                       LANDLOCK_ACCESS_FS_REMOVE_FILE |
                       LANDLOCK_ACCESS_FS_MAKE_CHAR |
                       LANDLOCK_ACCESS_FS_MAKE_DIR |
                       LANDLOCK_ACCESS_FS_MAKE_REG |
                       LANDLOCK_ACCESS_FS_MAKE_SOCK |
                       LANDLOCK_ACCESS_FS_MAKE_FIFO |
                       LANDLOCK_ACCESS_FS_MAKE_BLOCK |
                       LANDLOCK_ACCESS_FS_MAKE_SYM;

    /* Враховуємо прапорці ABI 2 та 3, якщо ядро їх підтримує */
    if (abi >= 2) {
        handled_fs |= LANDLOCK_ACCESS_FS_REFER;
    }
    if (abi >= 3) {
        handled_fs |= LANDLOCK_ACCESS_FS_TRUNCATE;
    }

    struct landlock_ruleset_attr ruleset_attr = {
        .handled_access_fs = handled_fs,
    };

    /* 2. Створення набору правил */
    int ruleset_fd = landlock_create_ruleset(&ruleset_attr, sizeof(ruleset_attr), 0);
    if (ruleset_fd < 0) {
        perror("Помилка landlock_create_ruleset");
        return 1;
    }

    __u64 read_exec = LANDLOCK_ACCESS_FS_READ_FILE | 
                      LANDLOCK_ACCESS_FS_READ_DIR | 
                      LANDLOCK_ACCESS_FS_EXECUTE;

    __u64 read_only = LANDLOCK_ACCESS_FS_READ_FILE | 
                      LANDLOCK_ACCESS_FS_READ_DIR;

    /* 3. Додаємо дозволені шляхи */
    add_path_rule(ruleset_fd, "/usr", read_exec);
    add_path_rule(ruleset_fd, "/bin", read_exec);
    add_path_rule(ruleset_fd, "/lib", read_exec);
    add_path_rule(ruleset_fd, "/lib64", read_exec);
    add_path_rule(ruleset_fd, "/etc", read_only);

    /* 4. Встановлюємо PR_SET_NO_NEW_PRIVS */
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)) {
        perror("Помилка prctl(PR_SET_NO_NEW_PRIVS)");
        close(ruleset_fd);
        return 1;
    }

    /* 5. Застосовуємо правила */
    if (landlock_restrict_self(ruleset_fd, 0)) {
        perror("Помилка landlock_restrict_self");
        close(ruleset_fd);
        return 1;
    }

    close(ruleset_fd);

    /* 6. Запуск цільової програми */
    execvp(argv[1], &argv[1]);
    perror("Помилка execvp");
    return 1;
}
