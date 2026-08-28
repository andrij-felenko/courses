#define _GNU_SOURCE
#include <sys/uio.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdint.h>
#include <errno.h>

#define PAYLOAD_SIZE (64 * 1024)

struct ProtocolHeader {
    uint32_t magic;
    uint32_t sequence;
    uint32_t payload_len;
    uint32_t flags;
    uint8_t  padding[48];
};

ssize_t run_vectored_writev_pipeline(int fd_in, int fd_out, size_t total_bytes) {
    char *payload = (char *)malloc(PAYLOAD_SIZE);
    if (!payload) return -1;

    struct ProtocolHeader header = {
        .magic = 0x554E4958, /* 'UNIX' */
        .sequence = 0,
        .payload_len = PAYLOAD_SIZE,
        .flags = 0
    };

    struct iovec iov[2];
    iov[0].iov_base = &header;
    iov[0].iov_len = sizeof(struct ProtocolHeader);
    iov[1].iov_base = payload;
    iov[1].iov_len = PAYLOAD_SIZE;

    size_t bytes_transferred = 0;
    while (bytes_transferred < total_bytes) {
        ssize_t n_read = read(fd_in, payload, PAYLOAD_SIZE);
        if (n_read <= 0) {
            if (n_read < 0 && errno == EINTR) continue;
            break;
        }

        header.sequence++;
        header.payload_len = (uint32_t)n_read;
        iov[1].iov_len = (size_t)n_read;

        ssize_t total_chunk = sizeof(struct ProtocolHeader) + n_read;
        ssize_t n_written = writev(fd_out, iov, 2);
        if (n_written < 0) {
            if (errno == EINTR) continue;
            free(payload);
            return -1;
        }

        bytes_transferred += n_read;
    }

    free(payload);
    return (ssize_t)bytes_transferred;
}
