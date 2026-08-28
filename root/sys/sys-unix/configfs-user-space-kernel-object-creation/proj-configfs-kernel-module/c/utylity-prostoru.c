/* Утиліта керування configfs мовою C (POSIX API) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <errno.h>

#define CONFIGFS_PATH "/sys/kernel/config/demo_target/node_c"

int main(void)
{
    int fd;
    char buffer[128];
    ssize_t bytes;

    /* 1. Створення ядерного об'єкта через mkdir */
    printf("[C] Створення об'єкта %s...\n", CONFIGFS_PATH);
    if (mkdir(CONFIGFS_PATH, 0755) < 0 && errno != EEXIST) {
        perror("Помилка mkdir");
        return EXIT_FAILURE;
    }

    /* 2. Запис значення атрибута value */
    char attr_val_path[256];
    snprintf(attr_val_path, sizeof(attr_val_path), "%s/value", CONFIGFS_PATH);

    fd = open(attr_val_path, O_WRONLY);
    if (fd < 0) {
        perror("Помилка відкриття value для запису");
        return EXIT_FAILURE;
    }

    const char *val_str = "42";
    if (write(fd, val_str, strlen(val_str)) < 0) {
        perror("Помилка запису в value");
        close(fd);
        return EXIT_FAILURE;
    }
    close(fd);
    printf("[C] Успішно записано value = 42\n");

    /* 3. Зчитання стану об'єкта з атрибута status */
    char attr_status_path[256];
    snprintf(attr_status_path, sizeof(attr_status_path), "%s/status", CONFIGFS_PATH);

    fd = open(attr_status_path, O_RDONLY);
    if (fd >= 0) {
        bytes = read(fd, buffer, sizeof(buffer) - 1);
        if (bytes > 0) {
            buffer[bytes] = '\0';
            printf("[C] Прочитано status:\n%s", buffer);
        }
        close(fd);
    }

    /* 4. Видалення ядерного об'єкта через rmdir */
    printf("[C] Видалення об'єкта через rmdir...\n");
    if (rmdir(CONFIGFS_PATH) < 0) {
        perror("Помилка rmdir");
        return EXIT_FAILURE;
    }

    printf("[C] Об'єкт успішно знищено у ядрі.\n");
    return EXIT_SUCCESS;
}
