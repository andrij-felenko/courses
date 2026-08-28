#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

/* Атомарний обмін місцями активної конфігурації та резервної */
int swap_configurations(const char *active_path, const char *backup_path) {
    if (renameat2(AT_FDCWD, active_path, AT_FDCWD, backup_path, RENAME_EXCHANGE) < 0) {
        perror("Помилка атомарного обміну файлів");
        return -1;
    }
    return 0;
}
