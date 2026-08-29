#pragma once

#include <utility>

#include <sys/socket.h>
#include <unistd.h>

namespace portal {

/*
 * Власник дескриптора сокета. Замінює ланцюжок goto out із close()
 * у кожній гілці: дескриптор закривається сам, яким би шляхом
 * керування не вийшло з області видимості.
 */
class UniqueSocket {
public:
    UniqueSocket() noexcept = default;

    explicit UniqueSocket(int fd) noexcept : fd_{fd} {}

    UniqueSocket(const UniqueSocket &) = delete;
    UniqueSocket &operator=(const UniqueSocket &) = delete;

    UniqueSocket(UniqueSocket &&other) noexcept
        : fd_{std::exchange(other.fd_, kInvalid)} {}

    UniqueSocket &operator=(UniqueSocket &&other) noexcept
    {
        if (this != &other) {
            reset(std::exchange(other.fd_, kInvalid));
        }
        return *this;
    }

    ~UniqueSocket() { reset(); }

    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
    explicit operator bool() const noexcept { return valid(); }

    [[nodiscard]] int get() const noexcept { return fd_; }

    /* Віддає дескриптор назовні, знімаючи з себе відповідальність. */
    [[nodiscard]] int release() noexcept { return std::exchange(fd_, kInvalid); }

    void reset(int fd = kInvalid) noexcept
    {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = fd;
    }

    /*
     * Розриває сокет, не закриваючи дескриптора: завдання, що стоїть
     * у recvfrom, прокидається помилкою й виходить із циклу саме.
     */
    void shutdown() const noexcept
    {
        if (fd_ >= 0) {
            ::shutdown(fd_, SHUT_RDWR);
        }
    }

private:
    static constexpr int kInvalid = -1;

    int fd_{kInvalid};
};

}  // namespace portal
