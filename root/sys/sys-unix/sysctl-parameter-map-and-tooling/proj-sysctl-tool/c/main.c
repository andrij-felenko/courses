#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <limits.h>

#define SYSCTL_PREFIX "/proc/sys/"
#define BUFFER_SIZE 4096

/* Перетворення крапкової назви net.ipv4.ip_forward у шлях /proc/sys/net/ipv4/ip_forward */
static int key_to_path(const char *key, char *path_out, size_t max_len)
{
    size_t prefix_len = strlen(SYSCTL_PREFIX);
    size_t key_len = strlen(key);

    if (prefix_len + key_len >= max_len) {
        errno = ENAMETOOLONG;
        return -1;
    }

    strcpy(path_out, SYSCTL_PREFIX);
    for (size_t i = 0; i < key_len; i++) {
        path_out[prefix_len + i] = (key[i] == '.') ? '/' : key[i];
    }
    path_out[prefix_len + key_len] = '\0';
    return 0;
}

/* Зчитування значення параметра sysctl */
static int read_sysctl(const char *key)
{
    char path[PATH_MAX];
    char buffer[BUFFER_SIZE];

    if (key_to_path(key, path, sizeof(path)) < 0) {
        fprintf(stderr, "Помилка: занадто довгий ключ '%s'\n", key);
        return 1;
    }

    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        if (errno == ENOENT) {
            fprintf(stderr, "Помилка: параметр '%s' не існує у /proc/sys\n", key);
        } else if (errno == EACCES) {
            fprintf(stderr, "Помилка: немає прав для читання %s\n", path);
        } else {
            fprintf(stderr, "Помилка відкриття %s: %s\n", path, strerror(errno));
        }
        return 1;
    }

    ssize_t bytes_read = read(fd, buffer, sizeof(buffer) - 1);
    if (bytes_read < 0) {
        /* close() першим ділом затер би errno, тож спершу друкуємо причину */
        fprintf(stderr, "Помилка читання %s: %s\n", path, strerror(errno));
        close(fd);
        return 1;
    }
    close(fd);

    buffer[bytes_read] = '\0';
    /* Видаляємо кінцевий символ нового рядка, якщо він є */
    if (bytes_read > 0 && buffer[bytes_read - 1] == '\n') {
        buffer[bytes_read - 1] = '\0';
    }

    printf("%s = %s\n", key, buffer);
    return 0;
}

/* Запис нового значення у параметр sysctl */
static int write_sysctl(const char *key, const char *value)
{
    char path[PATH_MAX];

    if (key_to_path(key, path, sizeof(path)) < 0) {
        fprintf(stderr, "Помилка: занадто довгий ключ '%s'\n", key);
        return 1;
    }

    int fd = open(path, O_WRONLY);
    if (fd < 0) {
        if (errno == EACCES || errno == EPERM) {
            fprintf(stderr, "Помилка доступу до %s: потрібні привілеї root (CAP_SYS_ADMIN або CAP_NET_ADMIN)\n", path);
        } else if (errno == ENOENT) {
            fprintf(stderr, "Помилка: параметр '%s' не існує у /proc/sys\n", key);
        } else if (errno == EROFS) {
            fprintf(stderr, "Помилка: параметр %s доступний лише для читання\n", path);
        } else {
            fprintf(stderr, "Помилка відкриття %s для запису: %s\n", path, strerror(errno));
        }
        return 1;
    }

    size_t val_len = strlen(value);
    ssize_t bytes_written = write(fd, value, val_len);
    if (bytes_written < 0) {
        if (errno == EINVAL) {
            fprintf(stderr, "Помилка запису у %s: недопустиме значення '%s' (поза діапазоном або хибний тип)\n", path, value);
        } else {
            fprintf(stderr, "Помилка запису у %s: %s\n", path, strerror(errno));
        }
        close(fd);
        return 1;
    }
    close(fd);

    printf("%s = %s\n", key, value);
    return 0;
}

int main(int argc, char *argv[])
{
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <ключ> [значення]\n", argv[0]);
        fprintf(stderr, "Приклад читання: %s net.ipv4.ip_forward\n", argv[0]);
        fprintf(stderr, "Приклад запису:   %s net.ipv4.ip_forward 1\n", argv[0]);
        return 1;
    }

    if (argc == 2) {
        return read_sysctl(argv[1]);
    } else {
        return write_sysctl(argv[1], argv[2]);
    }
}
