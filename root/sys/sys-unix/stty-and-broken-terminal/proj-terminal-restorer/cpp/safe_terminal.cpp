// ==========================================================================
// safe_terminal.cpp — Ідіоматичний RAII-менеджер сирого режиму C++.
// Автоматичне відновлення в деструкторі, безпека винятків та обробка сигналів.
// ==========================================================================

#include <iostream>
#include <string_view>
#include <vector>
#include <array>
#include <memory>
#include <system_error>
#include <csignal>
#include <cstring>
#include <unistd.h>
#include <termios.h>

namespace tty {

class TerminalGuard {
public:
    TerminalGuard() {
        if (::isatty(STDIN_FILENO) == 0) {
            throw std::system_error(errno, std::generic_category(), "STDIN не є терміналом");
        }

        if (::tcgetattr(STDIN_FILENO, &m_orig_termios) < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося отримати termios");
        }

        s_active_instance = this;
        setup_signals();

        m_raw_termios = m_orig_termios;
        ::cfmakeraw(&m_raw_termios);
        m_raw_termios.c_cc[VMIN] = 1;
        m_raw_termios.c_cc[VTIME] = 0;

        if (::tcsetattr(STDIN_FILENO, TCSAFLUSH, &m_raw_termios) < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося встановити сирий режим");
        }

        m_is_raw = true;
    }

    ~TerminalGuard() noexcept {
        restore_raw();
        s_active_instance = nullptr;
    }

    TerminalGuard(const TerminalGuard&) = delete;
    TerminalGuard& operator=(const TerminalGuard&) = delete;
    TerminalGuard(TerminalGuard&&) = delete;
    TerminalGuard& operator=(TerminalGuard&&) = delete;

    void restore_raw() noexcept {
        if (m_is_raw) {
            ::tcsetattr(STDIN_FILENO, TCSANOW, &m_orig_termios);
            m_is_raw = false;
        }
    }

    void enable_raw() noexcept {
        if (!m_is_raw) {
            ::tcsetattr(STDIN_FILENO, TCSAFLUSH, &m_raw_termios);
            m_is_raw = true;
        }
    }

    [[nodiscard]] bool is_raw() const noexcept {
        return m_is_raw;
    }

private:
    struct termios m_orig_termios{};
    struct termios m_raw_termios{};
    bool m_is_raw{false};

    inline static TerminalGuard* s_active_instance{nullptr};

    static void signal_handler(int signo) noexcept {
        int saved_errno = errno;
        if (s_active_instance != nullptr) {
            s_active_instance->restore_raw();
        }

        struct sigaction sa{};
        sa.sa_handler = SIG_DFL;
        ::sigemptyset(&sa.sa_mask);
        ::sigaction(signo, &sa, nullptr);

        sigset_t unblock_mask;
        ::sigemptyset(&unblock_mask);
        ::sigaddset(&unblock_mask, signo);
        ::sigprocmask(SIG_UNBLOCK, &unblock_mask, nullptr);

        ::raise(signo);
        errno = saved_errno;
    }

    static void tstp_handler(int signo) noexcept {
        (void)signo;
        int saved_errno = errno;
        if (s_active_instance != nullptr) {
            s_active_instance->restore_raw();
        }

        struct sigaction sa{};
        sa.sa_handler = SIG_DFL;
        ::sigemptyset(&sa.sa_mask);
        ::sigaction(SIGTSTP, &sa, nullptr);

        sigset_t unblock_mask;
        ::sigemptyset(&unblock_mask);
        ::sigaddset(&unblock_mask, SIGTSTP);
        ::sigprocmask(SIG_UNBLOCK, &unblock_mask, nullptr);

        ::raise(SIGTSTP);

        sa.sa_handler = tstp_handler;
        ::sigaction(SIGTSTP, &sa, nullptr);
        errno = saved_errno;
    }

    static void cont_handler(int signo) noexcept {
        (void)signo;
        int saved_errno = errno;
        if (s_active_instance != nullptr) {
            s_active_instance->enable_raw();
        }
        errno = saved_errno;
    }

    static void setup_signals() {
        struct sigaction sa{};
        sa.sa_handler = signal_handler;
        ::sigemptyset(&sa.sa_mask);
        sa.sa_flags = 0;

        constexpr std::array<int, 4> fatal_signals = { SIGINT, SIGTERM, SIGHUP, SIGQUIT };
        for (int sig : fatal_signals) {
            if (::sigaction(sig, &sa, nullptr) < 0) {
                throw std::system_error(errno, std::generic_category(), "sigaction failed");
            }
        }

        sa.sa_handler = tstp_handler;
        if (::sigaction(SIGTSTP, &sa, nullptr) < 0) {
            throw std::system_error(errno, std::generic_category(), "sigaction SIGTSTP failed");
        }

        sa.sa_handler = cont_handler;
        if (::sigaction(SIGCONT, &sa, nullptr) < 0) {
            throw std::system_error(errno, std::generic_category(), "sigaction SIGCONT failed");
        }
    }
};

} // namespace tty

int main() {
    try {
        tty::TerminalGuard term_guard;

        std::string_view intro = "C++ RAII термінал активовано. Натисніть 'q' для виходу або Ctrl+Z для перевірки:\r\n";
        ::write(STDOUT_FILENO, intro.data(), intro.size());

        unsigned char ch = 0;
        while (true) {
            ssize_t n = ::read(STDIN_FILENO, &ch, 1);
            if (n < 0) {
                if (errno == EINTR) {
                    continue;
                }
                break;
            }
            if (n == 0) {
                break;
            }

            if (ch == 'q') {
                std::string_view exit_msg = "\r\nВихід за запитом користувача.\r\n";
                ::write(STDOUT_FILENO, exit_msg.data(), exit_msg.size());
                break;
            }

            std::string out = "Отримано байт: 0x" + std::to_string(static_cast<int>(ch)) + "\r\n";
            ::write(STDOUT_FILENO, out.data(), out.size());
        }
    } catch (const std::exception& ex) {
        std::cerr << "Виняток: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
