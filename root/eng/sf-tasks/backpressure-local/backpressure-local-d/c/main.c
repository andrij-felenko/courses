#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <stdio.h>

/* Обробка неблокуючого протитиску на рівні дескриптора POSIX */
ssize_t safe_write_with_backpressure(int fd, const void *buf, size_t count) {
    size_t written = 0;
    const char *ptr = (const char *)buf;

    while (written < count) {
        ssize_t res = write(fd, ptr + written, count - written);
        if (res > 0) {
            written += res;
            continue;
        }
        if (res == -1) {
            if (errno == EINTR) continue; /* Сигнал ОС: повторити спробу */
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                /* Спрацював протитиск: буфер ядра повний.
                   Повертаємо кількість реально записаних байтів */
                return (written > 0) ? (ssize_t)written : -EAGAIN;
            }
            return -errno; /* Фатальна помилка дескриптора */
        }
    }
    return (ssize_t)written;
}
