#define _GNU_SOURCE
#include <sys/sendfile.h>
#include <unistd.h>
#include <errno.h>

#define SENDFILE_CHUNK (1024 * 1024) /* 1 МБ за виклик */

ssize_t run_sendfile_pipeline(int fd_in, int fd_out, size_t total_bytes) {
    size_t bytes_transferred = 0;
    off_t offset = 0;

    while (bytes_transferred < total_bytes) {
        size_t to_send = (total_bytes - bytes_transferred > SENDFILE_CHUNK)
                         ? SENDFILE_CHUNK
                         : (total_bytes - bytes_transferred);

        ssize_t n_sent = sendfile(fd_out, fd_in, &offset, to_send);
        if (n_sent <= 0) {
            if (n_sent < 0 && (errno == EINTR || errno == EAGAIN)) continue;
            if (n_sent == 0) break; /* EOF */
            return -1;
        }
        bytes_transferred += n_sent;
    }

    return (ssize_t)bytes_transferred;
}
