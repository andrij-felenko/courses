#pragma once

#include <cerrno>
#include <chrono>
#include <cstddef>
#include <span>
#include <system_error>
#include <utility>

#include <poll.h>
#include <unistd.h>

namespace gw {

// Дескриптор із власником. Усе, що в C розсипається по гілках `goto out` із
// парним close(fd), тут робить деструктор: помилка кидає виняток, і сокет
// закривається сам, на якому б рядку ми не були.
class Fd {
public:
    Fd() noexcept = default;
    explicit Fd(int fd) noexcept : fd_{fd} {}

    Fd(const Fd&) = delete;
    Fd& operator=(const Fd&) = delete;

    Fd(Fd&& other) noexcept : fd_{std::exchange(other.fd_, -1)} {}
    Fd& operator=(Fd&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = std::exchange(other.fd_, -1);
        }
        return *this;
    }
    ~Fd() { reset(); }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    void reset() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = -1;
    }

    // false — за відведений час нічого не прийшло; це не помилка.
    [[nodiscard]] bool waitReadable(std::chrono::milliseconds timeout) const {
        ::pollfd pfd{fd_, POLLIN, 0};
        const int rc = ::poll(&pfd, 1, static_cast<int>(timeout.count()));
        if (rc > 0) {
            return true;
        }
        if (rc == 0 || errno == EINTR) {
            return false;
        }
        throw std::system_error{errno, std::generic_category(), "poll"};
    }

    // Читає рівно стільки байтів, скільки замовлено, або здається за дедлайном.
    [[nodiscard]] bool readExact(std::span<std::byte> out,
                                 std::chrono::steady_clock::time_point deadline) const {
        std::size_t off = 0;
        while (off < out.size()) {
            const auto left = std::chrono::duration_cast<std::chrono::milliseconds>(
                deadline - std::chrono::steady_clock::now());
            if (left.count() <= 0) {
                return false;
            }

            ::pollfd pfd{fd_, POLLIN, 0};
            const int rc = ::poll(&pfd, 1, static_cast<int>(left.count()));
            if (rc == 0) {
                return false;
            }
            if (rc < 0) {
                if (errno == EINTR) {
                    continue;
                }
                throw std::system_error{errno, std::generic_category(), "poll"};
            }

            const ssize_t n = ::read(fd_, out.data() + off, out.size() - off);
            if (n > 0) {
                off += static_cast<std::size_t>(n);
                continue;
            }
            if (n == 0) {
                // Порт зник або той бік закрив з'єднання — далі чекати нема чого.
                throw std::system_error{ECONNRESET, std::generic_category(), "потік обірвано"};
            }
            if (errno == EINTR || errno == EAGAIN || errno == EWOULDBLOCK) {
                continue;
            }
            throw std::system_error{errno, std::generic_category(), "read"};
        }
        return true;
    }

    void writeAll(std::span<const std::byte> data) const {
        std::size_t off = 0;
        while (off < data.size()) {
            const ssize_t n = ::write(fd_, data.data() + off, data.size() - off);
            if (n > 0) {
                off += static_cast<std::size_t>(n);
                continue;
            }
            if (n < 0 && errno == EINTR) {
                continue;
            }
            if (n < 0 && (errno == EAGAIN || errno == EWOULDBLOCK)) {
                ::pollfd pfd{fd_, POLLOUT, 0};
                if (::poll(&pfd, 1, 1000) <= 0) {
                    throw std::system_error{ETIMEDOUT, std::generic_category(), "запис не пройшов"};
                }
                continue;
            }
            throw std::system_error{errno, std::generic_category(), "write"};
        }
    }

private:
    int fd_{-1};
};

}  // namespace gw
