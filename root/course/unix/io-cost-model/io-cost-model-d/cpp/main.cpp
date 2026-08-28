#include <sys/uio.h>
#include <unistd.h>
#include <array>
#include <span>
#include <cstdint>

struct PacketHeader {
    std::uint32_t magic;
    std::uint32_t length;
    std::uint64_t sequence;
};

ssize_t send_packet_cpp(int sock_fd, const PacketHeader& hdr, 
                        std::span<const std::byte> payload) {
    std::array<struct iovec, 2> iov{{
        { .iov_base = const_cast<PacketHeader*>(&hdr), .iov_len = sizeof(PacketHeader) },
        { .iov_base = const_cast<std::byte*>(payload.data()), .iov_len = payload.size() }
    }};

    return ::writev(sock_fd, iov.data(), static_cast<int>(iov.size()));
}
