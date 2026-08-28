// Безпечне керування терміналом мовою C++ з використанням RAII
#include <iostream>
#include <system_error>
#include <csignal>
#include <cstring>
#include <unistd.h>
#include <termios.h>

namespace terminal {

class SafeRawMode {
public:
    SafeRawMode() {
        if (::isatty(STDIN_FILENO) == 0) {
            throw std::system_error(errno, std::generic_category(), "STDIN не є терміналом");
        }

        if (::tcgetattr(STDIN_FILENO, &m_orig_termios) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка tcgetattr");
        }

        s_instance = this;
        install_signal_handlers();

        struct termios raw = m_orig_termios;
        ::cfmakeraw(&raw);
        raw.c_cc[VMIN] = 1;
        raw.c_cc[VTIME] = 0;

        if (::tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка tcsetattr");
        }

        m_active = true;
    }

    ~SafeRawMode() noexcept {
        restore();
        s_instance = nullptr;
    }

    SafeRawMode(const SafeRawMode&) = delete;
    SafeRawMode& operator=(const SafeRawMode&) = delete;

    void restore() noexcept {
        if (m_active) {
            ::tcsetattr(STDIN_FILENO, TCSANOW, &m_orig_termios);
            m_active = false;
        }
    }

private:
    struct termios m_orig_termios{};
    bool m_active{false};
    inline static SafeRawMode* s_instance{nullptr};

    static void signal_dispatcher(int signo) noexcept {
        int saved_errno = errno;
        if (s_instance != nullptr) {
            s_instance->restore();
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

    static void install_signal_handlers() {
        struct sigaction sa{};
        sa.sa_handler = signal_dispatcher;
        ::sigemptyset(&sa.sa_mask);
        sa.sa_flags = 0;

        for (int sig : { SIGINT, SIGTERM, SIGHUP, SIGQUIT }) {
            if (::sigaction(sig, &sa, nullptr) < 0) {
                throw std::system_error(errno, std::generic_category(), "Помилка sigaction");
            }
        }
    }
};

} // namespace terminal
