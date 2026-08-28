#include <termios.h>
#include <unistd.h>
#include <string_view>

void restore_terminal(int fd, const struct termios& orig) noexcept {
    // 1. Показуємо курсор, повертаємо основний екран, скидаємо кольори
    constexpr std::string_view reset_seq = "\x1b[?25h\x1b[?1049l\x1b[0m";
    [[maybe_unused]] auto _ = ::write(fd, reset_seq.data(), reset_seq.size());

    // 2. Відновлюємо прапорці termios
    ::tcsetattr(fd, TCSAFLUSH, &orig);
}
