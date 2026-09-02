#pragma once

#include <cerrno>
#include <cstddef>
#include <expected>
#include <span>
#include <system_error>
#include <utility>

#include <fcntl.h>
#include <unistd.h>

// Власник дескриптора. Закриття робить деструктор, тож у гілках помилок
// не треба ані goto out, ані ручного close() у кожному return.
class Fd {
public:
    Fd() = default;
    explicit Fd(int fd) noexcept : fd_(fd) {}

    Fd(const Fd &) = delete;
    Fd &operator=(const Fd &) = delete;

    Fd(Fd &&other) noexcept : fd_(std::exchange(other.fd_, -1)) {}

    Fd &operator=(Fd &&other) noexcept
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

    void reset() noexcept
    {
        if (fd_ >= 0) {
            ::close(fd_);
            fd_ = -1;
        }
    }

private:
    int fd_ = -1;
};

// Канал: обидва кінці під RAII.
struct Pipe {
    Fd readEnd;
    Fd writeEnd;

    static std::expected<Pipe, std::error_code> create()
    {
        int fds[2] = { -1, -1 };
        // O_CLOEXEC ставиться атомарно тим самим викликом. Розбити його на
        // pipe() + fcntl() означало б вікно, у яке сусідній потік устигне
        // зробити fork+execve і винести дескриптор у чужу програму.
        if (::pipe2(fds, O_CLOEXEC) < 0)
            return std::unexpected(std::error_code(errno, std::generic_category()));
        return Pipe{ Fd(fds[0]), Fd(fds[1]) };
    }
};

// write(2) має право записати менше, ніж просили, і обірватися на сигналі.
inline std::error_code writeExactly(int fd, std::span<const std::byte> bytes)
{
    while (!bytes.empty()) {
        const ssize_t written = ::write(fd, bytes.data(), bytes.size());
        if (written < 0) {
            if (errno == EINTR)
                continue;
            return { errno, std::generic_category() };
        }
        bytes = bytes.subspan(static_cast<std::size_t>(written));
    }
    return {};
}

inline std::error_code readExactly(int fd, std::span<std::byte> bytes)
{
    while (!bytes.empty()) {
        const ssize_t got = ::read(fd, bytes.data(), bytes.size());
        if (got < 0) {
            if (errno == EINTR)
                continue;
            return { errno, std::generic_category() };
        }
        if (got == 0)  // EOF раніше часу: дитина вмерла, не дописавши
            return std::make_error_code(std::errc::broken_pipe);
        bytes = bytes.subspan(static_cast<std::size_t>(got));
    }
    return {};
}
