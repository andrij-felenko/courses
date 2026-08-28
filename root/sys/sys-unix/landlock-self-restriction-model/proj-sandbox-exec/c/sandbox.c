/* sandbox.c — запустити команду з урізаним доступом до файлової системи.
   Збірка:  cc -Wall -O2 -o sandbox sandbox.c                            */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <linux/landlock.h>

/* обгорток у бібліотеці C немає — кличемо номерами */
#ifndef __NR_landlock_create_ruleset
#define __NR_landlock_create_ruleset 444
#define __NR_landlock_add_rule       445
#define __NR_landlock_restrict_self  446
#endif

/* права, що з'явилися пізніше за заголовки, які може мати ця машина */
#ifndef LANDLOCK_ACCESS_FS_REFER
#define LANDLOCK_ACCESS_FS_REFER     (1ULL << 13)
#endif
#ifndef LANDLOCK_ACCESS_FS_TRUNCATE
#define LANDLOCK_ACCESS_FS_TRUNCATE  (1ULL << 14)
#endif
#ifndef LANDLOCK_ACCESS_FS_IOCTL_DEV
#define LANDLOCK_ACCESS_FS_IOCTL_DEV (1ULL << 15)
#endif

#define ACCESS_RO (LANDLOCK_ACCESS_FS_READ_FILE | LANDLOCK_ACCESS_FS_READ_DIR)

#define ACCESS_X  (ACCESS_RO | LANDLOCK_ACCESS_FS_EXECUTE)

#define ACCESS_RW (ACCESS_RO                       | \
    LANDLOCK_ACCESS_FS_WRITE_FILE  | LANDLOCK_ACCESS_FS_TRUNCATE   | \
    LANDLOCK_ACCESS_FS_REMOVE_FILE | LANDLOCK_ACCESS_FS_REMOVE_DIR | \
    LANDLOCK_ACCESS_FS_MAKE_REG    | LANDLOCK_ACCESS_FS_MAKE_DIR   | \
    LANDLOCK_ACCESS_FS_MAKE_SYM    | LANDLOCK_ACCESS_FS_MAKE_SOCK  | \
    LANDLOCK_ACCESS_FS_MAKE_FIFO   | LANDLOCK_ACCESS_FS_REFER      | \
    LANDLOCK_ACCESS_FS_IOCTL_DEV)

/* оголошуємо більше, ніж роздаємо: MAKE_CHAR і MAKE_BLOCK не дістануться нікому */
#define HANDLED (ACCESS_RW | ACCESS_X | \
    LANDLOCK_ACCESS_FS_MAKE_CHAR | LANDLOCK_ACCESS_FS_MAKE_BLOCK)

static int add_path(int ruleset_fd, const char *path, __u64 access)
{
    struct landlock_path_beneath_attr rule = { .allowed_access = access };
    int err;

    rule.parent_fd = open(path, O_PATH | O_CLOEXEC);
    if (rule.parent_fd < 0) {
        fprintf(stderr, "sandbox: %s: %s\n", path, strerror(errno));
        return -1;
    }
    err = syscall(__NR_landlock_add_rule, ruleset_fd,
                  LANDLOCK_RULE_PATH_BENEATH, &rule, 0);
    if (err)
        fprintf(stderr, "sandbox: правило на %s: %s\n", path, strerror(errno));
    close(rule.parent_fd);
    return err;
}

/* "a:b:c" → по правилу на елемент; рядок псується на місці, і це argv */
static int add_list(int ruleset_fd, char *list, __u64 access)
{
    if (list == NULL || access == 0)
        return 0;
    for (char *p = strtok(list, ":"); p != NULL; p = strtok(NULL, ":"))
        if (add_path(ruleset_fd, p, access) != 0)
            return -1;
    return 0;
}

int main(int argc, char *argv[])
{
    char *ro = NULL, *rw = NULL, *ex = NULL;
    __u64 handled = HANDLED;
    int i, abi, ruleset_fd;

    for (i = 1; i + 1 < argc; i += 2) {
        if      (strcmp(argv[i], "-r") == 0) ro = argv[i + 1];
        else if (strcmp(argv[i], "-w") == 0) rw = argv[i + 1];
        else if (strcmp(argv[i], "-x") == 0) ex = argv[i + 1];
        else break;
    }
    if (i < argc && strcmp(argv[i], "--") == 0)
        i++;
    if (i >= argc) {
        fprintf(stderr, "вжиток: %s [-r шляхи] [-w шляхи] [-x шляхи]"
                        " -- команда…\n", argv[0]);
        return 2;
    }

    /* 1. питаємо, що вміє це ядро, і прибираємо решту з оголошення */
    abi = syscall(__NR_landlock_create_ruleset, NULL, 0,
                  LANDLOCK_CREATE_RULESET_VERSION);
    if (abi < 0) {
        fprintf(stderr, "sandbox: Landlock недоступний: %s\n", strerror(errno));
        return 1;
    }
    if (abi < 2) handled &= ~LANDLOCK_ACCESS_FS_REFER;
    if (abi < 3) handled &= ~LANDLOCK_ACCESS_FS_TRUNCATE;
    if (abi < 5) handled &= ~LANDLOCK_ACCESS_FS_IOCTL_DEV;

    /* 2. набір: оголошуємо, за що беремо відповідальність.
          хвіст структури мусить бути нульовий — на ньому тримається
          сумісність із ядром, що знає менше полів                      */
    struct landlock_ruleset_attr attr = { .handled_access_fs = handled };

    ruleset_fd = syscall(__NR_landlock_create_ruleset, &attr, sizeof attr, 0);
    if (ruleset_fd < 0) {
        perror("sandbox: landlock_create_ruleset");
        return 1;
    }

    /* 3. правила — з тією самою вкороченою маскою */
    if (add_list(ruleset_fd, ex, ACCESS_X  & handled) != 0 ||
        add_list(ruleset_fd, ro, ACCESS_RO & handled) != 0 ||
        add_list(ruleset_fd, rw, ACCESS_RW & handled) != 0)
        return 1;

    /* 4. замок; порядок обов'язковий — без no_new_privs буде EPERM */
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) {
        perror("sandbox: PR_SET_NO_NEW_PRIVS");
        return 1;
    }
    if (syscall(__NR_landlock_restrict_self, ruleset_fd, 0) != 0) {
        perror("sandbox: landlock_restrict_self");
        return 1;
    }
    close(ruleset_fd);

    /* 5. з цієї миті назад дороги нема */
    execvp(argv[i], &argv[i]);
    fprintf(stderr, "sandbox: %s: %s\n", argv[i], strerror(errno));
    return 127;
}
