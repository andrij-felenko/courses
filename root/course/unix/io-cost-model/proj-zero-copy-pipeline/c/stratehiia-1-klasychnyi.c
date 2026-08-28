#define _GNU_SOURCE
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>

#define CHUNK_SIZE (64 * 1024)

ssize_t run_read_write_pipeline(int fd_in, int fd_out, size_t total_bytes) {
    char *buf = (char *)malloc(CHUNK_SIZE);
    if (!buf) return -1;

    size_t bytes_transferred = 0;
    while (bytes_transferred < total_bytes) {
        size_t to_read = (total_bytes - bytes_transferred > CHUNK_SIZE) 
                         ? CHUNK_SIZE 
                         : (total_bytes - bytes_transferred);

        ssize_t n_read = read(fd_in, buf, to_read);
        if (n_read <= 0) {
            if (n_read < 0 && errno == EINTR) continue;
            break;
        }

        size_t written = 0;
        while (written < (size_t)n_read) {
            ssize_t n_write = write(fd_out, buf + written, n_read - written);
            if (n_write <= 0) {
                if (n_write < 0 && errno == EINTR) continue;
                free(buf);
                return -1;
            }
            written += n_write;
        }
        bytes_transferred += written;
    }

    free(buf);
    return (ssize_t)bytes_transferred;
}
