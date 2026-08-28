#include <unistd.h>
#include <errno.h>

ssize_t write_all(int fd, const void *buf, size_t count)
{
    size_t written = 0;
    const char *ptr = (const char *)buf;

    while (written < count) {
        ssize_t res = write(fd, ptr + written, count - written);
        if (res < 0) {
            if (errno == EINTR)
                continue; /* Переривання сигналом: повторюємо спробу */
            return -1;    /* Справжня помилка: повертаємо невдачу */
        }
        if (res == 0)
            break;        /* Неможливо записати далі */
        written += (size_t)res;
    }
    return (ssize_t)written;
}
