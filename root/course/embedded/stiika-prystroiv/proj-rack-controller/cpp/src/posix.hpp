// Тонкий шар над POSIX: володіння дескриптором і перетворення errno на виняток.
#pragma once

#include <cerrno>
#include <csignal>
#include <string>
#include <string_view>
#include <system_error>
#include <utility>

#include <unistd.h>

// Ставить обробник SIGINT/SIGTERM у main.cpp; цикли очікування його бачать.
extern volatile std::sig_atomic_t gStopRequested;

// Дескриптор із єдиним власником: рівно те, що в C доводиться робити руками
// в кожній гілці помилки. Закриття відбувається й при виході через виняток.
class UniqueFd {
public:
    UniqueFd() = default;
    explicit UniqueFd(int fd) noexcept : fd_{fd} {}

    UniqueFd(UniqueFd&& other) noexcept : fd_{std::exchange(other.fd_, -1)} {}
    UniqueFd& operator=(UniqueFd&& other) noexcept
    {
        if (this != &other) {
            reset(std::exchange(other.fd_, -1));
        }
        return *this;
    }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    ~UniqueFd() { reset(); }

    [[nodiscard]] int get() const noexcept { return fd_; }
    explicit operator bool() const noexcept { return fd_ >= 0; }

    void reset(int fd = -1) noexcept
    {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = fd;
    }

private:
    int fd_{-1};
};

[[noreturn]] inline void throwErrno(std::string_view what)
{
    // system_error несе і код, і текст: далі його ловить один catch у main.
    throw std::system_error{errno, std::system_category(), std::string{what}};
}
