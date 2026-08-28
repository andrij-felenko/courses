#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <expected>
#include <system_error>
#include <unistd.h>
#include <poll.h>
#include <sys/socket.h>

class SocketHandle {
    int fd_ = -1;
public:
    explicit SocketHandle(int fd) noexcept : fd_(fd) {}
    ~SocketHandle() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    SocketHandle(const SocketHandle&) = delete;
    SocketHandle& operator=(const SocketHandle&) = delete;
    SocketHandle(SocketHandle&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }
    SocketHandle& operator=(SocketHandle&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

class StreamPipeTunnel {
    static constexpr size_t kBufferSize = 64 * 1024;

public:
    static std::expected<size_t, std::error_code> pipe_data(int src_fd, int dst_fd) {
        std::array<std::byte, kBufferSize> buffer{};
        size_t total_transferred = 0;

        for (;;) {
            ssize_t bytes_read = ::recv(src_fd, buffer.data(), buffer.size(), 0);
            if (bytes_read > 0) {
                auto send_res = write_all(dst_fd, std::span{buffer.data(), static_cast<size_t>(bytes_read)});
                if (!send_res) {
                    return std::unexpected(send_res.error());
                }
                total_transferred += static_cast<size_t>(bytes_read);
                continue;
            }
            if (bytes_read == 0) {
                break; // Успішний EOF
            }
            if (errno == EINTR) {
                continue;
            }
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                struct pollfd pfd{.fd = src_fd, .events = POLLIN, .revents = 0};
                int p_res = ::poll(&pfd, 1, 5000);
                if (p_res > 0 && (pfd.revents & POLLIN)) {
                    continue;
                }
                return std::unexpected(std::make_error_code(std::errc::timed_out));
            }
            return std::unexpected(std::make_error_code(std::errc::io_error));
        }

        return total_transferred;
    }

private:
    static std::expected<void, std::error_code> write_all(int fd, std::span<const std::byte> data) {
        size_t total_written = 0;
        while (total_written < data.size()) {
            ssize_t n = ::send(fd, data.data() + total_written, data.size() - total_written, 0);
            if (n > 0) {
                total_written += static_cast<size_t>(n);
                continue;
            }
            if (n < 0) {
                if (errno == EINTR) continue;
                if (errno == EAGAIN || errno == EWOULDBLOCK) {
                    struct pollfd pfd{.fd = fd, .events = POLLOUT, .revents = 0};
                    int p_res = ::poll(&pfd, 1, 5000);
                    if (p_res > 0 && (pfd.revents & POLLOUT)) continue;
                    return std::unexpected(std::make_error_code(std::errc::timed_out));
                }
                return std::unexpected(std::make_error_code(std::errc::broken_pipe));
            }
            return std::unexpected(std::make_error_code(std::errc::connection_aborted));
        }
        return {};
    }
};
