#include <sys/uio.h>
#include <unistd.h>
#include <stdint.h>

struct PacketHeader {
    uint32_t magic;
    uint32_t length;
    uint64_t sequence;
};

ssize_t send_packet(int sock_fd, const struct PacketHeader *hdr, 
                    const void *payload, size_t payload_len) {
    struct iovec iov[2];
    iov[0].iov_base = (void *)hdr;
    iov[0].iov_len = sizeof(struct PacketHeader);
    iov[1].iov_base = (void *)payload;
    iov[1].iov_len = payload_len;

    return writev(sock_fd, iov, 2);
}
