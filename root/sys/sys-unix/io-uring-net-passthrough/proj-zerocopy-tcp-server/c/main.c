/* c */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <liburing.h>

#define QUEUE_DEPTH 256
#define BUFFER_SIZE 65536
#define NUM_BUFFERS 64

enum conn_state {
    STATE_ACCEPT,
    STATE_READ,
    STATE_SEND_ZC,
    STATE_WAIT_NOTIF
};

struct client_ctx {
    int fd;
    enum conn_state state;
    int buf_idx;
    size_t bytes_to_send;
    size_t bytes_sent;
};

static char g_buffers[NUM_BUFFERS][BUFFER_SIZE] __attribute__((aligned(4096)));
static int g_buf_freelist[NUM_BUFFERS];
static int g_buf_free_top = NUM_BUFFERS;

static int alloc_buffer(void) {
    if (g_buf_free_top <= 0) return -1;
    return g_buf_freelist[--g_buf_free_top];
}

static void free_buffer(int idx) {
    if (g_buf_free_top < NUM_BUFFERS) {
        g_buf_freelist[g_buf_free_top++] = idx;
    }
}

int main(int argc, char *argv[]) {
    int port = 8080;
    if (argc > 1) port = atoi(argv[1]);

    for (int i = 0; i < NUM_BUFFERS; i++) {
        g_buf_freelist[i] = i;
    }

    int listen_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (listen_fd < 0) {
        perror("socket");
        return 1;
    }

    int val = 1;
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &val, sizeof(val));

    struct sockaddr_in addr = {
        .sin_family = AF_INET,
        .sin_port = htons(port),
        .sin_addr.s_addr = INADDR_ANY
    };

    if (bind(listen_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind");
        return 1;
    }

    if (listen(listen_fd, 128) < 0) {
        perror("listen");
        return 1;
    }

    struct io_uring ring;
    if (io_uring_queue_init(QUEUE_DEPTH, &ring, 0) < 0) {
        fprintf(stderr, "Failed to init io_uring\n");
        return 1;
    }

    /* Реєстрація масиву буферів для Zero-Copy */
    struct iovec iovs[NUM_BUFFERS];
    for (int i = 0; i < NUM_BUFFERS; i++) {
        iovs[i].iov_base = g_buffers[i];
        iovs[i].iov_len = BUFFER_SIZE;
    }

    if (io_uring_register_buffers(&ring, iovs, NUM_BUFFERS) < 0) {
        fprintf(stderr, "Failed to register fixed buffers\n");
        return 1;
    }

    printf("SendZC TCP Echo Server listening on port %d...\n", port);

    /* Додаємо первинний accept у чергу */
    struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);
    struct client_ctx accept_ctx = { .fd = listen_fd, .state = STATE_ACCEPT };
    io_uring_prep_accept(sqe, listen_fd, NULL, NULL, 0);
    io_uring_sqe_set_data(sqe, &accept_ctx);
    io_uring_submit(&ring);

    while (1) {
        struct io_uring_cqe *cqe;
        int ret = io_uring_wait_cqe(&ring, &cqe);
        if (ret < 0) break;

        struct client_ctx *ctx = (struct client_ctx *)io_uring_cqe_get_data(cqe);
        int res = cqe->res;
        unsigned int flags = cqe->flags;

        if (ctx->state == STATE_ACCEPT) {
            if (res >= 0) {
                int client_fd = res;
                struct client_ctx *cctx = malloc(sizeof(*cctx));
                cctx->fd = client_fd;
                cctx->buf_idx = alloc_buffer();
                cctx->state = STATE_READ;

                if (cctx->buf_idx >= 0) {
                    sqe = io_uring_get_sqe(&ring);
                    io_uring_prep_read_fixed(sqe, client_fd, g_buffers[cctx->buf_idx], 
                                             BUFFER_SIZE, 0, cctx->buf_idx);
                    io_uring_sqe_set_data(sqe, cctx);
                } else {
                    close(client_fd);
                    free(cctx);
                }
            }
            /* Перепідготовка accept */
            sqe = io_uring_get_sqe(&ring);
            io_uring_prep_accept(sqe, listen_fd, NULL, NULL, 0);
            io_uring_sqe_set_data(sqe, &accept_ctx);
            io_uring_submit(&ring);
        } 
        else if (ctx->state == STATE_READ) {
            if (res > 0) {
                ctx->bytes_to_send = res;
                ctx->bytes_sent = 0;
                ctx->state = STATE_SEND_ZC;

                sqe = io_uring_get_sqe(&ring);
                /* Подаємо IORING_OP_SEND_ZC з зареєстрованим буфером */
                io_uring_prep_send_zc_fixed(sqe, ctx->fd, g_buffers[ctx->buf_idx], 
                                           res, 0, 0, ctx->buf_idx);
                io_uring_sqe_set_data(sqe, ctx);
                io_uring_submit(&ring);
            } else {
                /* Клієнт закрив з'єднання або помилка */
                close(ctx->fd);
                free_buffer(ctx->buf_idx);
                free(ctx);
            }
        }
        else if (ctx->state == STATE_SEND_ZC) {
            /* Обробка першого або другого CQE для SendZC */
            if (flags & IORING_CQE_F_NOTIF) {
                /* Другий CQE: сповіщення про завершення DMA та звільнення пам'яті */
                sqe = io_uring_get_sqe(&ring);
                ctx->state = STATE_READ;
                io_uring_prep_read_fixed(sqe, ctx->fd, g_buffers[ctx->buf_idx], 
                                         BUFFER_SIZE, 0, ctx->buf_idx);
                io_uring_sqe_set_data(sqe, ctx);
                io_uring_submit(&ring);
            } else {
                /* Перший CQE: повернув кількість переданих байт */
                if (res < 0) {
                    close(ctx->fd);
                    free_buffer(ctx->buf_idx);
                    free(ctx);
                } else if (!(flags & IORING_CQE_F_MORE)) {
                    /* Запитів більше немає, чекаємо або читаємо далі */
                }
            }
        }

        io_uring_cqe_seen(&ring, cqe);
    }

    io_uring_queue_exit(&ring);
    close(listen_fd);
    return 0;
}
