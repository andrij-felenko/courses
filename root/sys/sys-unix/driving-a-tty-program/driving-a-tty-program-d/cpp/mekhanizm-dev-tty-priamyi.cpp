#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <termios.h>
#include <unistd.h>

#include <expected>
#include <memory>
#include <span>
#include <string>
#include <string_view>
#include <system_error>

class TerminalGuard {
public:
    TerminalGuard(int fd, const struct termios& original) noexcept
        : fd_(fd), original_(original), active_(true) {}

    ~TerminalGuard() {
        if (active_ && fd_ >= 0) {
            ::tcsetattr(fd_, TCSAFLUSH, &original_);
        }
    }

    TerminalGuard(const TerminalGuard&) = delete;
    TerminalGuard& operator=(const TerminalGuard&) = delete;

    TerminalGuard(TerminalGuard&& other) noexcept
        : fd_(other.fd_), original_(other.original_), active_(other.active_) {
        other.active_ = false;
    }

private:
    int fd_;
    struct termios original_;
    bool active_;
};

std::expected<std::string, std::error_code> safe_read_passphrase(std::string_view prompt) {
    int fd = ::open("/dev/tty", O_RDWR | O_NOCTTY);
    if (fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    auto close_fd = [](int* p) { if (p && *p >= 0) { ::close(*p); } };
    std::unique_ptr<int, decltype(close_fd)> fd_owner(&fd, close_fd);

    struct termios orig_termios{};
    if (::tcgetattr(fd, &orig_termios) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    TerminalGuard guard(fd, orig_termios);

    struct termios no_echo = orig_termios;
    no_echo.c_lflag &= ~(ECHO | ECHOE | ECHOK | ECHONL);
    if (::tcsetattr(fd, TCSAFLUSH, &no_echo) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    ::write(fd, prompt.data(), prompt.size());

    std::string password;
    char ch = 0;
    while (::read(fd, &ch, 1) == 1) {
        if (ch == '\n' || ch == '\r') {
            break;
        }
        password.push_back(ch);
    }
    ::write(fd, "\n", 1);

    return password;
}
