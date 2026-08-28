#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/socket.h>

/* Встановлення неблокуючого прапорця на дескриптор */
bool make_socket_nonblocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags == -1) {
        perror("fcntl F_GETFL");
        return false;
    }
    if (fcntl(fd, F_SETFL, flags | O_NONBLOCK) == -1) {
        perror("fcntl F_SETFL O_NONBLOCK");
        return false;
    }
    return true;
}

typedef enum {
    READ_SUCCESS = 0,
    READ_NO_DATA,   /* EAGAIN / EWOULDBLOCK */
    READ_EOF,       /* Сокет закрито віддаленою стороною */
    READ_ERR        /* Фатальна помилка */
} read_result_t;

read_result_t read_all_available(int fd, uint8_t *dest, size_t max_len, size_t *out_read) {
    *out_read = 0;

    while (*out_read < max_len) {
        ssize_t n = read(fd, dest + *out_read, max_len - *out_read);

        if (n > 0) {
            *out_read += (size_t)n;
            continue; /* Продовжуємо вичитувати до вичерпання буфера ядра */
        }
        if (n == 0) {
            return READ_EOF; /* Віддалена сторона надіслала FIN */
        }
        if (errno == EINTR) {
            continue; /* Перервано системним сигналом — повторюємо */
        }
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            return (*out_read > 0) ? READ_SUCCESS : READ_NO_DATA;
        }
        return READ_ERR; /* Фатальна апаратна або мережева помилка */
    }

    return READ_SUCCESS;
}
