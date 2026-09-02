#pragma once

#include <expected>
#include <span>
#include <string>
#include <string_view>
#include <system_error>

#include <sys/types.h>

namespace tty {

// Байт стану, який пакетний режим TIOCPKT ставить першим у кожному read().
enum class PacketFlag : unsigned char {
    FlushRead  = 0x01,
    FlushWrite = 0x02,
    Stop       = 0x04,
    Start      = 0x08,
    NoStop     = 0x10,
    DoStop     = 0x20,
    Ioctl      = 0x40,
};

constexpr bool has(unsigned char control_byte, PacketFlag f) noexcept
{
    return (control_byte & static_cast<unsigned char>(f)) != 0;
}

// Файловий дескриптор як ресурс: закривається сам, копіюватися не вміє.
class Fd {
public:
    Fd() noexcept = default;
    explicit Fd(int fd) noexcept : fd_{fd} {}
    ~Fd() { reset(); }

    Fd(Fd&& other) noexcept : fd_{other.fd_} { other.fd_ = -1; }
    Fd& operator=(Fd&& other) noexcept
    {
        if (this != &other) {
            reset(other.fd_);
            other.fd_ = -1;
        }
        return *this;
    }

    Fd(const Fd&) = delete;
    Fd& operator=(const Fd&) = delete;

    int get() const noexcept { return fd_; }
    explicit operator bool() const noexcept { return fd_ >= 0; }
    void reset(int fd = -1) noexcept;

private:
    int fd_{-1};
};

// Ведучий бік псевдотермінала в пакетному режимі.
class PtyMaster {
public:
    static std::expected<PtyMaster, std::error_code> open();

    std::string_view slave_path() const noexcept { return slave_; }

    std::expected<pid_t, std::error_code> spawn(std::span<char* const> argv);

    // Крутить цикл ведучого до кінця сеансу; повертає код виходу дитини.
    std::expected<int, std::error_code> run();

private:
    PtyMaster(Fd fd, std::string slave)
        : fd_{std::move(fd)}, slave_{std::move(slave)} {}

    void handle_packet(std::span<const unsigned char> packet);

    Fd fd_;
    std::string slave_;
    pid_t child_{-1};
    bool flow_stopped_{false};
    bool eof_{false};
};

}  // namespace tty
