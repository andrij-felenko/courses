#include <unistd.h>
#include <errno.h>
#include <stdio.h>

typedef enum {
    IO_SUCCESS,
    IO_WOULD_BLOCK,
    IO_CLOSED,
    IO_FATAL_ERROR
} IoStatus;

IoStatus handle_nonblocking_read(int fd, char *buf, size_t size, size_t *out_bytes) {
    while (1) {
        ssize_t n = read(fd, buf, size);
        if (n > 0) {
            *out_bytes = (size_t)n;
            return IO_SUCCESS;
        }
        if (n == 0) {
            return IO_CLOSED;
        }
        if (errno == EINTR) {
            // Сигнал перервав навіть неблокуючий виклик — негайний повтор
            continue;
        }
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            // Даних немає в буфері — повертаємося до циклу epoll
            return IO_WOULD_BLOCK;
        }
        // Усі інші коди — фатальний збій
        return IO_FATAL_ERROR;
    }
}
