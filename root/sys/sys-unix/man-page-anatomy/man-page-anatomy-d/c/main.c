#define _POSIX_C_SOURCE 200809L
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <stdbool.h>

/* Безпечне зчитування блоку даних за специфікацією read(2) */
ssize_t safe_read_exact(int fd, void *buffer, size_t count) {
    size_t bytes_read_total = 0;
    char *dest = (char *)buffer;

    while (bytes_read_total < count) {
        ssize_t result = read(fd, dest + bytes_read_total, count - bytes_read_total);

        if (result > 0) {
            bytes_read_total += (size_t)result;
            continue;
        }

        if (result == 0) {
            /* Кінець файлу (EOF) або сокет закрито віддаленою стороною */
            break;
        }

        /* Обробка системних помилок через перевірку errno */
        if (errno == EINTR) {
            /* Системний виклик перервано сигналом: перезапускаємо читання */
            continue;
        }

        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            /* Дескриптор у неблокуючому режимі O_NONBLOCK: ресурс зайнятий */
            if (bytes_read_total > 0) {
                return (ssize_t)bytes_read_total;
            }
            return -1;
        }

        /* Критична системна помилка (EBADF, EFAULT, EIO тощо) */
        return -1;
    }

    return (ssize_t)bytes_read_total;
}
