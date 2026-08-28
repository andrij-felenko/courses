#include <termios.h>
#include <unistd.h>
#include <iostream>
#include <stdexcept>

class RawTerminalGuard {
public:
    RawTerminalGuard() {
        if (tcgetattr(STDIN_FILENO, &orig_termios_) == -1) {
            throw std::runtime_error("Помилка читання конфігурації TTY через tcgetattr");
        }

        struct termios raw = orig_termios_;
        raw.c_iflag &= ~(BRKINT | ICRNL | INPCK | ISTRIP | IXON);
        raw.c_oflag &= ~(OPOST);
        raw.c_cflag |= (CS8);
        raw.c_lflag &= ~(ECHO | ICANON | IEXTEN | ISIG);
        raw.c_cc[VMIN] = 0;
        raw.c_cc[VTIME] = 1;

        if (tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw) == -1) {
            throw std::runtime_error("Помилка активації Raw Mode через tcsetattr");
        }
    }

    ~RawTerminalGuard() noexcept {
        tcsetattr(STDIN_FILENO, TCSAFLUSH, &orig_termios_);
    }

    RawTerminalGuard(const RawTerminalGuard&) = delete;
    RawTerminalGuard& operator=(const RawTerminalGuard&) = delete;

private:
    struct termios orig_termios_{};
};
