// Володіння файловим дескриптором і парою каналу: закриття — робота деструктора.
#pragma once

#include <fcntl.h>
#include <unistd.h>

#include <cerrno>
#include <string>
#include <system_error>
#include <utility>

class Fd {
public:
    Fd() = default;
    explicit Fd(int fd) noexcept : fd_(fd) {}

    Fd(const Fd&) = delete;
    Fd& operator=(const Fd&) = delete;

    Fd(Fd&& other) noexcept : fd_(std::exchange(other.fd_, -1)) {}
    Fd& operator=(Fd&& other) noexcept
    {
        if (this != &other) {
            reset();
            fd_ = std::exchange(other.fd_, -1);
        }
        return *this;
    }
    ~Fd() { reset(); }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
    [[nodiscard]] int release() noexcept { return std::exchange(fd_, -1); }

    void reset() noexcept
    {
        if (fd_ >= 0) {
            ::close(fd_);
            fd_ = -1;
        }
    }

    void dup_onto(int target) const
    {
        if (fd_ == target) {
            return;
        }
        if (::dup2(fd_, target) < 0) {
            throw std::system_error(errno, std::generic_category(), "dup2");
        }
    }

    static Fd open_file(const std::string& path, int flags, ::mode_t mode = 0644)
    {
        const int fd = ::open(path.c_str(), flags, mode);
        if (fd < 0) {
            throw std::system_error(errno, std::generic_category(), path);
        }
        return Fd{fd};
    }

private:
    int fd_ = -1;
};

// Кінці каналу живуть рівно стільки, скільки живе об'єкт: забути закрити
// кінець запису (і лишити читача без EOF) тут просто немає як.
struct Pipe {
    Fd read_end;
    Fd write_end;

    static Pipe make()
    {
        int fds[2] = { -1, -1 };
        if (::pipe2(fds, O_CLOEXEC) < 0) {
            throw std::system_error(errno, std::generic_category(), "pipe2");
        }
        return Pipe{Fd{fds[0]}, Fd{fds[1]}};
    }
};
