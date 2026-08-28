#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>

#define PIPE_BUFFER_SIZE (1024 * 1024) /* 1 МБ буфер каналу */

ssize_t run_splice_pipeline(int fd_in, int fd_out, size_t total_bytes) {
    int pipefd[2];
    if (pipe(pipefd) < 0) return -1;

    /* Збільшуємо місткість каналу до 1 МБ */
    fcntl(pipefd[0], F_SETPIPE_SZ, PIPE_BUFFER_SIZE);

    size_t bytes_transferred = 0;
    while (bytes_transferred < total_bytes) {
        size_t to_splice = (total_bytes - bytes_transferred > PIPE_BUFFER_SIZE)
                           ? PIPE_BUFFER_SIZE
                           : (total_bytes - bytes_transferred);

        /* Крок 1: Вхідний дескриптор -> Канал (0 CPU копій) */
        ssize_t n_in = splice(fd_in, NULL, pipefd[1], NULL, to_splice, 
                              SPLICE_F_MOVE | SPLICE_F_MORE);
        if (n_in <= 0) {
            if (n_in < 0 && (errno == EINTR || errno == EAGAIN)) continue;
            if (n_in == 0) break;
            close(pipefd[0]);
            close(pipefd[1]);
            return -1;
        }

        /* Крок 2: Канал -> Вихідний дескриптор (0 CPU копій) */
        size_t written = 0;
        while (written < (size_t)n_in) {
            ssize_t n_out = splice(pipefd[0], NULL, fd_out, NULL, 
                                   n_in - written, SPLICE_F_MOVE | SPLICE_F_MORE);
            if (n_out <= 0) {
                if (n_out < 0 && (errno == EINTR || errno == EAGAIN)) continue;
                close(pipefd[0]);
                close(pipefd[1]);
                return -1;
            }
            written += n_out;
        }

        bytes_transferred += written;
    }

    close(pipefd[0]);
    close(pipefd[1]);
    return (ssize_t)bytes_transferred;
}
