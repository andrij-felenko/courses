// Керівний термінал оболонки: хто ним володіє і в якому він режимі.
#pragma once

#include <termios.h>
#include <unistd.h>

#include <csignal>
#include <initializer_list>
#include <optional>

class TerminalControl {
public:
    explicit TerminalControl(int tty_fd)
    {
        // Поки оболонка сама роздає термінал, ці сигнали зупинили б її саму:
        // tcsetpgrp() з фонової групи негайно повертає SIGTTOU.
        for (int sig : { SIGTTOU, SIGTTIN, SIGTSTP, SIGINT, SIGQUIT }) {
            ::signal(sig, SIG_IGN);
        }
        if (tty_fd >= 0 && ::isatty(tty_fd)) {
            fd_ = tty_fd;
            ::termios modes{};
            if (::tcgetattr(fd_, &modes) == 0) {
                saved_modes_ = modes;
            }
            ::tcsetpgrp(fd_, shell_pgid_);
        }
    }

    TerminalControl(const TerminalControl&) = delete;
    TerminalControl& operator=(const TerminalControl&) = delete;

    ~TerminalControl() { reclaim(); }

    [[nodiscard]] bool interactive() const noexcept { return fd_ >= 0; }
    [[nodiscard]] int fd() const noexcept { return fd_; }
    [[nodiscard]] ::pid_t shell_pgid() const noexcept { return shell_pgid_; }

    void give_to(::pid_t pgid) const noexcept
    {
        if (fd_ >= 0 && pgid > 0) {
            ::tcsetpgrp(fd_, pgid);
        }
    }

    void reclaim() const noexcept
    {
        if (fd_ < 0) {
            return;
        }
        ::tcsetpgrp(fd_, shell_pgid_);
        // Завдання могло лишити термінал у неканонічному режимі — повертаємо свій.
        if (saved_modes_) {
            ::tcsetattr(fd_, TCSADRAIN, &*saved_modes_);
        }
    }

private:
    int fd_ = -1;
    ::pid_t shell_pgid_ = ::getpgrp();
    std::optional<::termios> saved_modes_;
};
