#include <sys/sendfile.h>
#include <unistd.h>
#include <cerrno>
#include <algorithm>
#include <cstddef>

constexpr std::size_t SendfileChunk = 1024 * 1024;

ssize_t run_sendfile_pipeline_cpp(int fd_in, int fd_out, std::size_t total_bytes) {
    std::size_t bytes_transferred = 0;
    off_t current_offset = 0;

    while (bytes_transferred < total_bytes) {
        const std::size_t to_send = std::min(SendfileChunk, total_bytes - bytes_transferred);

        ssize_t n_sent = ::sendfile(fd_out, fd_in, &current_offset, to_send);
        if (n_sent <= 0) {
            if (n_sent < 0 && (errno == EINTR || errno == EAGAIN)) continue;
            if (n_sent == 0) break;
            return -1;
        }
        bytes_transferred += static_cast<std::size_t>(n_sent);
    }

    return static_cast<ssize_t>(bytes_transferred);
}
