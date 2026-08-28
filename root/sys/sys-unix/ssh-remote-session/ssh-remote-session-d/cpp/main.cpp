#include <iostream>
#include <array>
#include <span>
#include <string>
#include <string_view>
#include <memory>
#include <system_error>
#include <cstdlib>
#include <unistd.h>
#include <termios.h>
#include <sys/ioctl.h>
#include <sys/wait.h>
#include <pty.h>
#include <poll.h>

namespace sys {

class TerminalGuard {
public:
    TerminalGuard() {
        if (::isatty(STDIN_FILENO)) {
            if (::tcgetattr(STDIN_FILENO, &orig_termios_) == 0) {
                active_ = true;
            }
        }
    }

    ~TerminalGuard() noexcept {
        restore();
    }

    TerminalGuard(const TerminalGuard&) = delete;
    TerminalGuard& operator=(const TerminalGuard&) = delete;

    void enable_raw_mode() {
        if (!active_) return;
        struct termios raw = orig_termios_;
        ::cfmakeraw(&raw);
        if (::tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw) == -1) {
            throw std::system_error(errno, std::generic_category(), "tcsetattr raw mode failed");
        }
        raw_enabled_ = true;
    }

    void restore() noexcept {
        if (active_ && raw_enabled_) {
            ::tcsetattr(STDIN_FILENO, TCSAFLUSH, &orig_termios_);
            raw_enabled_ = false;
        }
    }

private:
    struct termios orig_termios_{};
    bool active_{false};
    bool raw_enabled_{false};
};

struct UniqueFd {
    int fd{-1};

    UniqueFd() noexcept = default;
    explicit UniqueFd(int f) noexcept : fd(f) {}
    ~UniqueFd() noexcept { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd(other.fd) { other.fd = -1; }
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset(other.fd);
            other.fd = -1;
        }
        return *this;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd >= 0) ::close(fd);
        fd = new_fd;
    }

    [[nodiscard]] int get() const noexcept { return fd; }
};

struct PtySession {
    UniqueFd master;
    pid_t child_pid{-1};
};

PtySession spawn_pty_session(std::string_view shell_path) {
    struct winsize ws{};
    if (::ioctl(STDIN_FILENO, TIOCGWINSZ, &ws) == -1) {
        ws.ws_col = 80;
        ws.ws_row = 24;
    }

    int master_fd = -1;
    pid_t pid = ::forkpty(&master_fd, nullptr, nullptr, &ws);
    if (pid < 0) {
        throw std::system_error(errno, std::generic_category(), "forkpty failed");
    }

    if (pid == 0) {
        // Дочірній процес у власному просторі сесії з PTY
        std::string path(shell_path.empty() ? "/bin/sh" : shell_path);
        ::execlp(path.c_str(), path.c_str(), "-l", nullptr);
        ::_exit(127);
    }

    return PtySession{UniqueFd(master_fd), pid};
}

void run_event_loop(int master_fd) {
    std::array<struct pollfd, 2> fds{{
        {STDIN_FILENO, POLLIN, 0},
        {master_fd, POLLIN, 0}
    }};

    std::array<char, 4096> buffer{};

    while (true) {
        int ret = ::poll(fds.data(), static_cast<nfds_t>(fds.size()), -1);
        if (ret < 0) {
            if (errno == EINTR) continue;
            break;
        }

        // Ввід користувача -> передача у майстер PTY
        if (fds[0].revents & POLLIN) {
            ssize_t n = ::read(STDIN_FILENO, buffer.data(), buffer.size());
            if (n <= 0) break;
            if (n == 2 && buffer[0] == '~' && buffer[1] == '.') {
                // Аварійний розрив сеансу
                break;
            }
            if (::write(master_fd, buffer.data(), static_cast<size_t>(n)) != n) break;
        }

        // Вивід програми -> передача на екран термінала
        if (fds[1].revents & POLLIN) {
            ssize_t n = ::read(master_fd, buffer.data(), buffer.size());
            if (n <= 0) break;
            if (::write(STDOUT_FILENO, buffer.data(), static_cast<size_t>(n)) != n) break;
        }

        if (fds[1].revents & (POLLHUP | POLLERR)) {
            break;
        }
    }
}

} // namespace sys

int main() {
    try {
        sys::TerminalGuard term_guard;
        const char* shell_env = std::getenv("SHELL");
        std::string_view shell = shell_env ? shell_env : "/bin/sh";

        auto session = sys::spawn_pty_session(shell);
        term_guard.enable_raw_mode();

        sys::run_event_loop(session.master.get());

        term_guard.restore();
        int status = 0;
        ::waitpid(session.child_pid, &status, 0);
        return WIFEXITED(status) ? WEXITSTATUS(status) : 1;
    } catch (const std::exception& e) {
        std::cerr << "Помилка сеансу: " << e.what() << '\n';
        return 1;
    }
}
