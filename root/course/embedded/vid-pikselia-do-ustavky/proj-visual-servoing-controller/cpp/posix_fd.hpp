#pragma once

#include <system_error>
#include <utility>

#include <unistd.h>

namespace servo {

/* Дескриптор із власником. Гілок помилок у відкритті пристроїв багато, і
 * жодна з них не має шансу забути close(): деструктор єдиний. */
class PosixFd {
public:
    PosixFd() noexcept = default;
    explicit PosixFd(int fd) noexcept : fd_{fd} {}

    PosixFd(const PosixFd&) = delete;
    PosixFd& operator=(const PosixFd&) = delete;

    PosixFd(PosixFd&& other) noexcept : fd_{std::exchange(other.fd_, -1)} {}

    PosixFd& operator=(PosixFd&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = std::exchange(other.fd_, -1);
        }
        return *this;
    }

    ~PosixFd() { reset(); }

    void reset() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
            fd_ = -1;
        }
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] explicit operator bool() const noexcept { return fd_ >= 0; }

private:
    int fd_{-1};
};

/* Помилка ядра — це виняток, а не −1, який хтось забуде перевірити. */
[[noreturn]] inline void throw_errno(const char* what) {
    throw std::system_error(errno, std::generic_category(), what);
}

}  // namespace servo
