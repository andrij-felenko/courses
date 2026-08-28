#include <fcntl.h>
#include <unistd.h>
#include <cerrno>
#include <algorithm>
#include <memory>

class PipeHandle {
public:
    PipeHandle() {
        if (::pipe(fds_.data()) < 0) {
            throw std::system_error(errno, std::generic_category(), "pipe creation failed");
        }
    }
    ~PipeHandle() noexcept {
        if (fds_[0] >= 0) ::close(fds_[0]);
        if (fds_[1] >= 0) ::close(fds_[1]);
    }
    PipeHandle(const PipeHandle&) = delete;
    PipeHandle& operator=(const PipeHandle&) = delete;

    [[nodiscard]] int read_fd() const noexcept { return fds_[0]; }
    [[nodiscard]] int write_fd() const noexcept { return fds_[1]; }

private:
    std::array<int, 2> fds_{-1, -1};
};

constexpr std::size_t SpliceBufferSize = 1024 * 1024;

ssize_t run_splice_pipeline_cpp(int fd_in, int fd_out, std::size_t total_bytes) {
    PipeHandle pipe;
    ::fcntl(pipe.read_fd(), F_SETPIPE_SZ, SpliceBufferSize);

    std::size_t bytes_transferred = 0;
    while (bytes_transferred < total_bytes) {
        const std::size_t to_splice = std::min(SpliceBufferSize, total_bytes - bytes_transferred);

        ssize_t n_in = ::splice(fd_in, nullptr, pipe.write_fd(), nullptr, to_splice,
                                SPLICE_F_MOVE | SPLICE_F_MORE);
        if (n_in <= 0) {
            if (n_in < 0 && (errno == EINTR || errno == EAGAIN)) continue;
            if (n_in == 0) break;
            return -1;
        }

        std::size_t written = 0;
        while (written < static_cast<std::size_t>(n_in)) {
            ssize_t n_out = ::splice(pipe.read_fd(), nullptr, fd_out, nullptr,
                                     static_cast<std::size_t>(n_in) - written,
                                     SPLICE_F_MOVE | SPLICE_F_MORE);
            if (n_out <= 0) {
                if (n_out < 0 && (errno == EINTR || errno == EAGAIN)) continue;
                return -1;
            }
            written += static_cast<std::size_t>(n_out);
        }
        bytes_transferred += written;
    }

    return static_cast<ssize_t>(bytes_transferred);
}
