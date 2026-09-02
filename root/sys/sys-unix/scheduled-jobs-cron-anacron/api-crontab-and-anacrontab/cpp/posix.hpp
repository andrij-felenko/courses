// Тонкий шар над POSIX: володіння дескриптором і перетворення errno на виняток.
#pragma once

#include <cerrno>
#include <string>
#include <system_error>
#include <utility>

#include <unistd.h>

namespace minicron {

[[noreturn]] inline void throw_errno(const std::string& what)
{
    throw std::system_error(errno, std::generic_category(), what);
}

// Дескриптор закривається у деструкторі — жодних гілок «goto out» і жодного
// шансу забути close() на дорозі помилки.
class UniqueFd {
public:
    UniqueFd() noexcept = default;
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(std::exchange(other.fd_, -1)) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept
    {
        if (this != &other) {
            close_now();
            fd_ = std::exchange(other.fd_, -1);
        }
        return *this;
    }

    ~UniqueFd() { close_now(); }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    // Дескриптор віддається назовні: закривати його вже не наша справа.
    [[nodiscard]] int release() noexcept { return std::exchange(fd_, -1); }

    void reset(int fd = -1) noexcept
    {
        if (fd != fd_) {
            close_now();
            fd_ = fd;
        }
    }

private:
    void close_now() noexcept
    {
        if (fd_ >= 0) {
            ::close(fd_);
            fd_ = -1;
        }
    }

    int fd_ = -1;
};

}  // namespace minicron
