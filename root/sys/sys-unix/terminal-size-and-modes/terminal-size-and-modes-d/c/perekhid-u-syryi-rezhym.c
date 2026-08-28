#include <termios.h>
#include <unistd.h>

void enable_raw_mode(int fd, const struct termios *orig, struct termios *raw) {
    *raw = *orig;

    /* Вхідні прапорці: вимикаємо перетворення CR у NL, перевірку парності та XON/XOFF */
    raw->c_iflag &= ~(BRKINT | ICRNL | INPCK | ISTRIP | IXON);

    /* Вихідні прапорці: вимикаємо системну пост-обробку виводу (перетворення \n у \r\n) */
    raw->c_oflag &= ~(OPOST);

    /* Прапорці керування лінією: 8 біт на символ */
    raw->c_cflag |= (CS8);

    /* Локальні прапорці: вимикаємо відлуння, канонічний режим та обробку сигналів */
    raw->c_lflag &= ~(ECHO | ICANON | IEXTEN | ISIG);

    /* Керуючі символи: блокуючий read() повертає результат при появі 1 байта */
    raw->c_cc[VMIN] = 1;
    raw->c_cc[VTIME] = 0;

    /* Застосовуємо налаштування зі скиданням вхідної черги */
    tcsetattr(fd, TCSAFLUSH, raw);
}
