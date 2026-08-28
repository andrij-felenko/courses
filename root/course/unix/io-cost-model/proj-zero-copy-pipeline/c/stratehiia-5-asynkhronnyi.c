#define _GNU_SOURCE
#include <liburing.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>

#define QUEUE_DEPTH 64
#define URING_CHUNK_SIZE (64 * 1024)

ssize_t run_io_uring_pipeline(int fd_in, int fd_out, size_t total_bytes) {
    struct io_uring ring;
    if (io_uring_queue_init(QUEUE_DEPTH, &ring, 0) < 0) {
        return -1;
    }

    /* Виділяємо пул буферів під глибину черги */
    char *buffers = (char *)aligned_alloc(4096, QUEUE_DEPTH * URING_CHUNK_SIZE);
    if (!buffers) {
        io_uring_queue_exit(&ring);
        return -1;
    }

    struct iovec iov[QUEUE_DEPTH];
    for (int i = 0; i < QUEUE_DEPTH; ++i) {
        iov[i].iov_base = buffers + (i * URING_CHUNK_SIZE);
        iov[i].iov_len = URING_CHUNK_SIZE;
    }

    /* Фіксуємо сторінки пам'яті в ядрі */
    io_uring_register_buffers(&ring, iov, QUEUE_DEPTH);

    size_t bytes_transferred = 0;
    off_t in_offset = 0;
    off_t out_offset = 0;

    while (bytes_transferred < total_bytes) {
        int submitted = 0;

        /* Формуємо пачку операцій читання */
        for (int i = 0; i < QUEUE_DEPTH && bytes_transferred + (submitted * URING_CHUNK_SIZE) < total_bytes; ++i) {
            struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);
            if (!sqe) break;

            io_uring_prep_read_fixed(sqe, fd_in, iov[i].iov_base, URING_CHUNK_SIZE, in_offset, i);
            sqe->user_data = (uint64_t)i;
            in_offset += URING_CHUNK_SIZE;
            submitted++;
        }

        if (submitted == 0) break;

        /* Відправляємо пачку одним викликом */
        io_uring_submit_and_wait(&ring, submitted);

        /* Збираємо готові читання та відправляємо їх на запис */
        for (int i = 0; i < submitted; ++i) {
            struct io_uring_cqe *cqe;
            if (io_uring_peek_cqe(&ring, &cqe) == 0) {
                if (cqe->res > 0) {
                    int buf_idx = (int)cqe->user_data;
                    
                    /* Підготовка операції запису */
                    struct io_uring_sqe *sqe_write = io_uring_get_sqe(&ring);
                    if (sqe_write) {
                        io_uring_prep_write_fixed(sqe_write, fd_out, iov[buf_idx].iov_base, 
                                                 cqe->res, out_offset, buf_idx);
                        sqe_write->user_data = (uint64_t)buf_idx;
                        out_offset += cqe->res;
                        bytes_transferred += cqe->res;
                    }
                }
                io_uring_cqe_seen(&ring, cqe);
            }
        }

        /* Завершення циклу запису */
        io_uring_submit_and_wait(&ring, 1);
        struct io_uring_cqe *cqe_w;
        while (io_uring_peek_cqe(&ring, &cqe_w) == 0) {
            io_uring_cqe_seen(&ring, cqe_w);
        }
    }

    io_uring_unregister_buffers(&ring);
    free(buffers);
    io_uring_queue_exit(&ring);
    return (ssize_t)bytes_transferred;
}
