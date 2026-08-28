#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <expected>
#include <system_error>
#include <unistd.h>
#include <poll.h>
#include <sys/socket.h>

class SafeSocket {
    int fd_ = -1;
public:
    explicit SafeSocket(int fd) noexcept : fd_(fd) {}
    ~SafeSocket() {
        if (fd_ >= 0) ::close(fd_);
    }
    SafeSocket(const SafeSocket&) = delete;
    SafeSocket& operator=(const SafeSocket&) = delete;
    SafeSocket(SafeSocket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }
    SafeSocket& operator=(SafeSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int native_handle() const noexcept { return fd_; }
};

class StreamForwarder {
    static constexpr size_t kBufferSize = 64 * 1024;

public:
    static std::expected<size_t, std::error_code> pipe(int src_fd, int dst_fd) {
        std::array<std::byte, kBufferSize> buffer{};
        size_t total_bytes = 0;

        for (;;) {
            ssize_t bytes_read = ::recv(src_fd, buffer.data(), buffer.size(), 0);
            if (bytes_read > 0) {
                auto res = write_all(dst_fd, std::span{buffer.data(), static_cast<size_t>(bytes_read)});
                if (!res) {
                    return std::unexpected(res.error());
                }
                total_bytes += static_cast<size_t>(bytes_read);
                continue;
            }
            if (bytes_read == 0) {
                break; // Успішне завершення потоку
            }
            if (errno == EINTR) continue;
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                struct pollfd pfd{.fd = src_fd, .events = POLLIN, .revents = 0};
                if (::poll(&pfd, 1, 5000) > 0 && (pfd.revents & POLLIN)) continue;
                return std::unexpected(std::make_error_code(std::errc::timed_out));
            }
            return std::unexpected(std::make_error_code(std::errc::io_error));
        }

        return total_bytes;
    }

private:
    static std::expected<void, std::error_code> write_all(int fd, std::span<const std::byte> chunk) {
        size_t sent = 0;
        while (sent < chunk.size()) {
            ssize_t n = ::send(fd, chunk.data() + sent, chunk.size() - sent, 0);
            if (n > 0) {
                sent += static_cast<size_t>(n);
                continue;
            }
            if (n < 0) {
                if (errno == EINTR) continue;
                if (errno == EAGAIN || errno == EWOULDBLOCK) {
                    struct pollfd pfd{.fd = fd, .events = POLLOUT, .revents = 0};
                    if (::poll(&pfd, 1, 5000) > 0 && (pfd.revents & POLLOUT)) continue;
                    return std::unexpected(std::make_error_code(std::errc::timed_out));
                }
                return std::unexpected(std::make_error_code(std::errc::broken_pipe));
            }
            return std::unexpected(std::make_error_code(std::errc::connection_aborted));
        }
        return {};
    }
};
