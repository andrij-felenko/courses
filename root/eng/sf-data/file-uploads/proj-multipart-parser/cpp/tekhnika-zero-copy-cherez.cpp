#include <fcntl.h>
#include <unistd.h>
#include <system_error>
#include <cstdint>

class KernelSpliceBridge {
public:
    KernelSpliceBridge() {
        if (::pipe2(pipe_fd_, O_NONBLOCK) == -1) {
            throw std::system_error(errno, std::generic_category(), "pipe2 failed");
        }
    }

    ~KernelSpliceBridge() {
        if (pipe_fd_[0] != -1) ::close(pipe_fd_[0]);
        if (pipe_fd_[1] != -1) ::close(pipe_fd_[1]);
    }

    ssize_t transfer(int source_fd, int dest_fd, size_t max_bytes) {
        ssize_t in = ::splice(source_fd, nullptr, pipe_fd_[1], nullptr,
                              max_bytes, SPLICE_F_MOVE | SPLICE_F_NONBLOCK);
        if (in <= 0) return in;

        return ::splice(pipe_fd_[0], nullptr, dest_fd, nullptr,
                        static_cast<size_t>(in), SPLICE_F_MOVE | SPLICE_F_NONBLOCK);
    }

private:
    int pipe_fd_[2] = {-1, -1};
};
