#include <iostream>
#include <vector>
#include <span>
#include <expected>
#include <cstdint>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/socket.h>

enum class SocketError {
    NoDataAvailable, // EAGAIN / EWOULDBLOCK
    PeerClosed,      // EOF
    SyscallFailed
};

class UniqueSocket {
public:
    explicit UniqueSocket(int fd = -1) noexcept : fd_(fd) {}
    ~UniqueSocket() { reset(); }

    UniqueSocket(const UniqueSocket&) = delete;
    UniqueSocket& operator=(const UniqueSocket&) = delete;

    UniqueSocket(UniqueSocket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    UniqueSocket& operator=(UniqueSocket&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool is_valid() const noexcept { return fd_ >= 0; }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

    [[nodiscard]] bool set_nonblocking() const noexcept {
        if (fd_ < 0) return false;
        int flags = ::fcntl(fd_, F_GETFL, 0);
        if (flags == -1) return false;
        return ::fcntl(fd_, F_SETFL, flags | O_NONBLOCK) != -1;
    }

private:
    int fd_{-1};
};

// Ідіоматичне читання з неблокуючого сокета через std::span та std::expected
[[nodiscard]] std::expected<size_t, SocketError> read_available(
    const UniqueSocket& socket, 
    std::span<std::byte> destination
) noexcept {
    size_t total_read = 0;

    while (total_read < destination.size()) {
        ssize_t n = ::read(
            socket.get(), 
            destination.data() + total_read, 
            destination.size() - total_read
        );

        if (n > 0) {
            total_read += static_cast<size_t>(n);
            continue;
        }
        if (n == 0) {
            return total_read > 0 ? std::expected<size_t, SocketError>(total_read) 
                                  : std::unexpected(SocketError::PeerClosed);
        }
        if (errno == EINTR) {
            continue;
        }
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            return total_read > 0 ? std::expected<size_t, SocketError>(total_read) 
                                  : std::unexpected(SocketError::NoDataAvailable);
        }
        return std::unexpected(SocketError::SyscallFailed);
    }

    return total_read;
}
