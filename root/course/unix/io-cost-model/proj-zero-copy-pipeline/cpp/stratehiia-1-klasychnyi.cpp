#include <unistd.h>
#include <vector>
#include <span>
#include <cerrno>
#include <system_error>
#include <cstddef>

constexpr std::size_t ChunkSize = 64 * 1024;

ssize_t run_read_write_pipeline_cpp(int fd_in, int fd_out, std::size_t total_bytes) {
    std::vector<char> buffer(ChunkSize);
    std::size_t bytes_transferred = 0;

    while (bytes_transferred < total_bytes) {
        const std::size_t to_read = std::min(ChunkSize, total_bytes - bytes_transferred);

        ssize_t n_read = ::read(fd_in, buffer.data(), to_read);
        if (n_read <= 0) {
            if (n_read < 0 && errno == EINTR) continue;
            break;
        }

        std::span<const char> pending{buffer.data(), static_cast<std::size_t>(n_read)};
        while (!pending.empty()) {
            ssize_t n_write = ::write(fd_out, pending.data(), pending.size());
            if (n_write <= 0) {
                if (n_write < 0 && errno == EINTR) continue;
                return -1;
            }
            pending = pending.subspan(static_cast<std::size_t>(n_write));
        }
        bytes_transferred += static_cast<std::size_t>(n_read);
    }

    return static_cast<ssize_t>(bytes_transferred);
}
