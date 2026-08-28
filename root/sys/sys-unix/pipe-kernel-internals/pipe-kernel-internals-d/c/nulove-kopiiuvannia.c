#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

/* Перекачування даних із мережевого сокета у файл через канал без участі юзерспейсу */
ssize_t zero_copy_stream(int sock_fd, int file_fd, size_t total_bytes) {
    int pfd[2];
    if (pipe(pfd) < 0) return -1;

    size_t transferred = 0;
    while (transferred < total_bytes) {
        /* Крок 1: Переміщуємо сторінки із сокета в канал (zero-copy) */
        ssize_t n_in = splice(sock_fd, NULL, pfd[1], NULL,
                              total_bytes - transferred, SPLICE_F_MOVE | SPLICE_F_MORE);
        if (n_in <= 0) break;

        /* Крок 2: Переміщуємо сторінки з каналу у цільовий файл (zero-copy) */
        ssize_t n_out = splice(pfd[0], NULL, file_fd, NULL,
                               (size_t)n_in, SPLICE_F_MOVE | SPLICE_F_MORE);
        if (n_out <= 0) break;

        transferred += (size_t)n_out;
    }

    close(pfd[0]);
    close(pfd[1]);
    return (ssize_t)transferred;
}
