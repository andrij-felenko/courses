/* dac_inspect.c — Діагностика ідентичності та перевірка прав доступу на C */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>

void print_credentials(void) {
    uid_t ruid, euid, suid;
    gid_t rgid, egid, sgid;

    if (getresuid(&ruid, &euid, &suid) != 0 || getresgid(&rgid, &egid, &sgid) != 0) {
        perror("getresuid/getresgid");
        return;
    }

    int ngroups = getgroups(0, NULL);
    gid_t *groups = NULL;
    if (ngroups > 0) {
        groups = malloc(sizeof(gid_t) * ngroups);
        if (groups && getgroups(ngroups, groups) < 0) {
            free(groups);
            groups = NULL;
            ngroups = 0;
        }
    }

    printf("Ідентичність процесу [PID %d]:\n", getpid());
    printf("  UID: real=%u, effective=%u, saved=%u\n", ruid, euid, suid);
    printf("  GID: real=%u, effective=%u, saved=%u\n", rgid, egid, sgid);
    printf("  Додаткові групи (%d): ", ngroups);
    for (int i = 0; i < ngroups; ++i) {
        printf("%u ", groups[i]);
    }
    printf("\n");
    free(groups);
}

int check_access_effective(const char *path, int mode) {
    if (faccessat(AT_FDCWD, path, mode, AT_EACCESS) == 0) {
        return 0;
    }
    return errno;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях_до_файлу>\n", argv[0]);
        return 1;
    }

    print_credentials();

    const char *target = argv[1];
    printf("\nПеревірка доступу до '%s' (faccessat з AT_EACCESS):\n", target);

    int err_r = check_access_effective(target, R_OK);
    int err_w = check_access_effective(target, W_OK);
    int err_x = check_access_effective(target, X_OK);

    printf("  Читання (R_OK):   %s\n", err_r == 0 ? "ДОЗВОЛЕНО" : strerror(err_r));
    printf("  Запис (W_OK):     %s\n", err_w == 0 ? "ДОЗВОЛЕНО" : strerror(err_w));
    printf("  Виконання (X_OK): %s\n", err_x == 0 ? "ДОЗВОЛЕНО" : strerror(err_x));

    return 0;
}
