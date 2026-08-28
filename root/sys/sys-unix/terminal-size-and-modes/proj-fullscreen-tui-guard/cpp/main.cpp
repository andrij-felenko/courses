#include <iostream>
#include <string>
#include <string_view>
#include <format>
#include <expected>
#include <system_error>
#include <cstdlib>
#include <cstring>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/signalfd.h>
#include <sys/select.h>
#include <termios.h>
#include <csignal>

namespace sys {

struct WindowSize {
    unsigned short rows{24};
    unsigned short cols{80};
    unsigned short x_pixel{0};
    unsigned short y_pixel{0};
};

// RAII-вартовий термінала: повністю контролює життєвий цикл сирого режиму та буферів
class TerminalGuard {
public:
    // Фабричний метод для безпечного захоплення дескриптора термінала
    static std::expected<TerminalGuard, std::error_code> acquire(int fd = STDIN_FILENO) noexcept {
        if (!isatty(fd)) {
            return std::unexpected(std::make_error_code(std::errc::not_a_tty));
        }

        struct termios orig{};
        if (::tcgetattr(fd, &orig) == -1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        struct termios raw = orig;
        raw.c_iflag &= ~(BRKINT | ICRNL | INPCK | ISTRIP | IXON);
        raw.c_oflag &= ~(OPOST);
        raw.c_cflag |= (CS8);
        raw.c_lflag &= ~(ECHO | ICANON | IEXTEN | ISIG);
        raw.c_cc[VMIN] = 1;
        raw.c_cc[VTIME] = 0;

        if (::tcsetattr(fd, TCSAFLUSH, &raw) == -1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        // Активація альтернативного екранного буфера та приховування курсора
        constexpr std::string_view enter_seq = "\x1b[?1049h\x1b[?25l";
        [[maybe_unused]] auto _ = ::write(fd, enter_seq.data(), enter_seq.size());

        return TerminalGuard(fd, orig);
    }

    // Деструктор гарантує відновлення термінала при будь-якому виході з області видимості
    ~TerminalGuard() noexcept {
        restore();
    }

    TerminalGuard(const TerminalGuard&) = delete;
    TerminalGuard& operator=(const TerminalGuard&) = delete;

    TerminalGuard(TerminalGuard&& other) noexcept
        : fd_(other.fd_), orig_termios_(other.orig_termios_), active_(other.active_) {
        other.active_ = false;
    }

    TerminalGuard& operator=(TerminalGuard&& other) noexcept {
        if (this != &other) {
            restore();
            fd_ = other.fd_;
            orig_termios_ = other.orig_termios_;
            active_ = other.active_;
            other.active_ = false;
        }
        return *this;
    }

    [[nodiscard]] std::expected<WindowSize, std::error_code> query_size() const noexcept {
        struct winsize ws{};
        if (::ioctl(fd_, TIOCGWINSZ, &ws) == 0 && ws.ws_row > 0 && ws.ws_col > 0) {
            return WindowSize{ws.ws_row, ws.ws_col, ws.ws_xpixel, ws.ws_ypixel};
        }

        // Fallback на змінні середовища оточення
        const char* lines = std::getenv("LINES");
        const char* cols = std::getenv("COLUMNS");
        if (lines && cols) {
            int r = std::atoi(lines);
            int c = std::atoi(cols);
            if (r > 0 && c > 0) {
                return WindowSize{static_cast<unsigned short>(r), static_cast<unsigned short>(c), 0, 0};
            }
        }

        return WindowSize{24, 80, 0, 0};
    }

    void render_frame(const WindowSize& size, int frame_count) const noexcept {
        std::string frame;
        frame.reserve(1024);
        frame += "\x1b[2J\x1b[H"; // Очищення екрана та перехід у 1,1
        frame += std::format("\x1b[1;37;44m C++23 TUI Guard \x1b[0m — Розмір: \x1b[1;32m{}×{}\x1b[0m | Кадр: \x1b[1;33m#{}\x1b[0m\r\n",
                             size.cols, size.rows, frame_count);
        frame += "Натисніть 'q' для виходу або змініть розмір вікна емулятора.\r\n";
        frame += std::format("\x1b[{};1H\x1b[7m [Q: Quit] | [RAII Guard: Active] \x1b[0m", size.rows);

        [[maybe_unused]] auto _ = ::write(fd_, frame.data(), frame.size());
    }

private:
    TerminalGuard(int fd, const struct termios& orig) noexcept
        : fd_(fd), orig_termios_(orig), active_(true) {}

    void restore() noexcept {
        if (!active_ || fd_ < 0) return;

        constexpr std::string_view restore_seq = "\x1b[?25h\x1b[?1049l\x1b[0m";
        [[maybe_unused]] auto _ = ::write(fd_, restore_seq.data(), restore_seq.size());
        ::tcsetattr(fd_, TCSAFLUSH, &orig_termios_);
        active_ = false;
    }

    int fd_{-1};
    struct termios orig_termios_{};
    bool active_{false};
};

} // namespace sys

int main() {
    auto guard_res = sys::TerminalGuard::acquire();
    if (!guard_res) {
        std::cerr << "Помилка ініціалізації термінала: " << guard_res.error().message() << '\n';
        return EXIT_FAILURE;
    }
    auto& guard = *guard_res;

    // Налаштування signalfd для синхронного опрацювання подій ядра
    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, SIGWINCH);
    sigaddset(&mask, SIGINT);
    sigaddset(&mask, SIGTERM);

    if (::sigprocmask(SIG_BLOCK, &mask, nullptr) == -1) {
        std::perror("sigprocmask");
        return EXIT_FAILURE;
    }

    int sfd = ::signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC);
    if (sfd == -1) {
        std::perror("signalfd");
        return EXIT_FAILURE;
    }

    auto size = guard.query_size().value_or(sys::WindowSize{24, 80, 0, 0});
    int frame_count = 0;
    guard.render_frame(size, ++frame_count);

    bool running = true;
    while (running) {
        fd_set read_fds;
        FD_ZERO(&read_fds);
        FD_SET(STDIN_FILENO, &read_fds);
        FD_SET(sfd, &read_fds);
        int max_fd = std::max(STDIN_FILENO, sfd) + 1;

        if (::select(max_fd, &read_fds, nullptr, nullptr, nullptr) == -1) {
            if (errno == EINTR) continue;
            break;
        }

        if (FD_ISSET(sfd, &read_fds)) {
            struct signalfd_siginfo fdsi{};
            if (::read(sfd, &fdsi, sizeof(fdsi)) == sizeof(fdsi)) {
                if (fdsi.ssi_signo == SIGWINCH) {
                    size = guard.query_size().value_or(sys::WindowSize{24, 80, 0, 0});
                    guard.render_frame(size, ++frame_count);
                } else if (fdsi.ssi_signo == SIGINT || fdsi.ssi_signo == SIGTERM) {
                    running = false;
                }
            }
        }

        if (FD_ISSET(STDIN_FILENO, &read_fds)) {
            char ch{};
            if (::read(STDIN_FILENO, &ch, 1) == 1) {
                if (ch == 'q' || ch == 'Q') {
                    running = false;
                } else {
                    guard.render_frame(size, ++frame_count);
                }
            }
        }
    }

    ::close(sfd);
    // guard автоматично викликає деструктор тут, надійно відновлюючи стан оболонки
    return EXIT_SUCCESS;
}
