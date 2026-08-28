#include <termios.h>
#include <unistd.h>

void restore_terminal(int fd, const struct termios *orig) {
    /* 1. Показуємо курсор, повертаємо основний екран, скидаємо кольори */
    const char reset_seq[] = "\x1b[?25h\x1b[?1049l\x1b[0m";
    (void)write(fd, reset_seq, sizeof(reset_seq) - 1);

    /* 2. Відновлюємо прапорці termios */
    tcsetattr(fd, TCSAFLUSH, orig);
}
