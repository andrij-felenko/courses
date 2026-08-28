#define _GNU_SOURCE
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <errno.h>

int safe_write_report(int dirfd, const char* filename, const char* data, size_t len) {
    // 1. Атомарне відкриття з прапорцями безпеки:
    // O_NOFOLLOW забороняє перехід за симлінком на кінцевому кроці
    // O_CLOEXEC запобігає витоку дескриптора в дочірні процеси
    int fd = openat(dirfd, filename, O_WRONLY | O_NOFOLLOW | O_CLOEXEC);
    if (fd < 0) {
        if (errno == ELOOP) {
            fprintf(stderr, "Безпекова помилка: виявлено заборонене символьне посилання!\n");
            return -1;
        }
        perror("openat failed");
        return -1;
    }

    // 2. Валідація закріпленого об'єкта через fstat
    struct stat st;
    if (fstat(fd, &st) != 0) {
        close(fd);
        return -1;
    }

    // 3. Перевіряємо, що це саме регулярний файл, а не сокет, FIFO чи спецпристрій
    if (!S_ISREG(st.st_mode)) {
        fprintf(stderr, "Помилка: цільовий об'єкт не є звичайним файлом\n");
        close(fd);
        return -1;
    }

    // 4. Запис у зафіксований дескриптор
    ssize_t written = write(fd, data, len);
    close(fd);
    return (written == (ssize_t)len) ? 0 : -1;
}
