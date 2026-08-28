#include <cerrno>
#include <cstring>
#include <expected>
#include <memory>
#include <optional>
#include <span>
#include <string>
#include <string_view>
#include <system_error>
#include <unistd.h>
#include <utility>

namespace sys {

/* Типізована категорія системних помилок POSIX */
class PosixError {
public:
    explicit PosixError(int code) : code_(code) {}

    [[nodiscard]] int code() const noexcept { return code_; }

    [[nodiscard]] std::string message() const {
        char buf[256];
#if defined(_GNU_SOURCE) && !defined(__APPLE__) && !defined(__FreeBSD__)
        char *msg = strerror_r(code_, buf, sizeof(buf));
        return std::string(msg);
#else
        if (strerror_r(code_, buf, sizeof(buf)) == 0) {
            return std::string(buf);
        }
        return "Unknown error " + std::to_string(code_);
#endif
    }

private:
    int code_;
};

/*
 * RAII-обгортка над файловим дескриптором POSIX.
 * Гарантує закриття дескриптора при виході з області видимості,
 * забороняє копіювання та підтримує семантику переміщення.
 */
class FileDescriptor {
public:
    constexpr FileDescriptor() noexcept : fd_(-1) {}
    explicit constexpr FileDescriptor(int fd) noexcept : fd_(fd) {}

    ~FileDescriptor() { reset(); }

    FileDescriptor(const FileDescriptor &) = delete;
    FileDescriptor &operator=(const FileDescriptor &) = delete;

    FileDescriptor(FileDescriptor &&other) noexcept : fd_(other.release()) {}

    FileDescriptor &operator=(FileDescriptor &&other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
    explicit operator bool() const noexcept { return valid(); }

    [[nodiscard]] int release() noexcept {
        return std::exchange(fd_, -1);
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

private:
    int fd_;
};

/*
 * Надійний повний запис послідовності байтів у дескриптор.
 * Повертає std::expected з кількістю записаних байтів або системною помилкою.
 */
[[nodiscard]] inline std::expected<size_t, PosixError>
write_all(int fd, std::span<const std::byte> data) noexcept {
    size_t total_written = 0;

    while (total_written < data.size()) {
        const auto remaining = data.subspan(total_written);
        ssize_t n = ::write(fd, remaining.data(), remaining.size());

        if (n > 0) {
            total_written += static_cast<size_t>(n);
            continue;
        }
        if (n == 0) {
            return std::unexpected(PosixError(EPIPE));
        }
        if (n == -1) {
            int err = errno;
            if (err == EINTR) {
                continue; // Перервано сигналом — повторюємо
            }
            return std::unexpected(PosixError(err));
        }
    }

    return total_written;
}

/*
 * Надійне повне читання буфера з дескриптора.
 * Заповнює весь переданий span або повертає помилку/ознаку передчасного EOF.
 */
[[nodiscard]] inline std::expected<size_t, PosixError>
read_exact(int fd, std::span<std::byte> buffer) noexcept {
    size_t total_read = 0;

    while (total_read < buffer.size()) {
        auto remaining = buffer.subspan(total_read);
        ssize_t n = ::read(fd, remaining.data(), remaining.size());

        if (n > 0) {
            total_read += static_cast<size_t>(n);
            continue;
        }
        if (n == 0) {
            // Передчасний EOF до повного заповнення буфера
            return std::unexpected(PosixError(ECONNABORTED));
        }
        if (n == -1) {
            int err = errno;
            if (err == EINTR) {
                continue; // Перервано сигналом — продовжуємо
            }
            return std::unexpected(PosixError(err));
        }
    }

    return total_read;
}

} // namespace sys
