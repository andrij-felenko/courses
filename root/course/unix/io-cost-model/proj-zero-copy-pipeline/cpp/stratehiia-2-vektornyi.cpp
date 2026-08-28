#include <sys/uio.h>
#include <unistd.h>
#include <vector>
#include <array>
#include <cstdint>
#include <cerrno>

constexpr std::size_t PayloadSize = 64 * 1024;

struct alignas(64) PacketHeader {
    std::uint32_t magic{0x554E4958};
    std::uint32_t sequence{0};
    std::uint32_t payload_len{PayloadSize};
    std::uint32_t flags{0};
    std::array<std::uint8_t, 48> padding{};
};

ssize_t run_vectored_writev_pipeline_cpp(int fd_in, int fd_out, std::size_t total_bytes) {
    PacketHeader header;
    std::vector<char> payload(PayloadSize);

    std::array<struct iovec, 2> iov{{
        { .iov_base = &header, .iov_len = sizeof(PacketHeader) },
        { .iov_base = payload.data(), .iov_len = payload.size() }
    }};

    std::size_t bytes_transferred = 0;
    while (bytes_transferred < total_bytes) {
        ssize_t n_read = ::read(fd_in, payload.data(), payload.size());
        if (n_read <= 0) {
            if (n_read < 0 && errno == EINTR) continue;
            break;
        }

        header.sequence++;
        header.payload_len = static_cast<std::uint32_t>(n_read);
        iov[1].iov_len = static_cast<std::size_t>(n_read);

        ssize_t n_written = ::writev(fd_out, iov.data(), static_cast<int>(iov.size()));
        if (n_written < 0) {
            if (errno == EINTR) continue;
            return -1;
        }

        bytes_transferred += static_cast<std::size_t>(n_read);
    }

    return static_cast<ssize_t>(bytes_transferred);
}
