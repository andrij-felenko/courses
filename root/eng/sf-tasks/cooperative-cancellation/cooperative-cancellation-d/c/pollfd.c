/* Приклад використання саморобної труби (self-pipe trick) для переривання блокуючого poll у C */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <poll.h>
#include <pthread.h>
#include <stdbool.h>
#include <stdatomic.h>

typedef struct {
    atomic_bool is_cancelled;
    int cancel_pipe[2]; /* [0] - читання, [1] - запис */
} cancellation_context_t;

void cancellation_context_init(cancellation_context_t *ctx) {
    atomic_init(&ctx->is_cancelled, false);
    if (pipe(ctx->cancel_pipe) < 0) {
        perror("Помилка створення pipe");
        exit(EXIT_FAILURE);
    }
    /* Переводимо дескриптор запису в неблокуючий режим */
    fcntl(ctx->cancel_pipe[1], F_SETFL, O_NONBLOCK);
}

void cancellation_context_request(cancellation_context_t *ctx) {
    atomic_store(&ctx->is_cancelled, true);
    char dummy = 'c';
    /* Запис у трубу виводить poll() із блокуючого стану */
    write(ctx->cancel_pipe[1], &dummy, 1);
}

void cancellation_context_cleanup(cancellation_context_t *ctx) {
    close(ctx->cancel_pipe[0]);
    close(ctx->cancel_pipe[1]);
}

int read_with_cancellation(int socket_fd, char *buffer, size_t len, cancellation_context_t *ctx) {
    struct pollfd fds[2];
    fds[0].fd = socket_fd;
    fds[0].events = POLLIN;
    fds[1].fd = ctx->cancel_pipe[0];
    fds[1].events = POLLIN;

    int ret = poll(fds, 2, -1); /* Блокуючий виклик очікування */
    if (ret < 0) {
        return -1; /* Помилка системного виклику */
    }

    /* Перевіряємо, чи спрацював канал скасування */
    if ((fds[1].revents & POLLIN) || atomic_load(&ctx->is_cancelled)) {
        return -2; /* Сигнал скасування отримано */
    }

    if (fds[0].revents & POLLIN) {
        return read(socket_fd, buffer, len);
    }

    return 0;
}
