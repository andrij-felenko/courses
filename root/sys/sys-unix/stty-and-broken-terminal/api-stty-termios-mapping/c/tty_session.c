#include "tty_session.h"

#include <errno.h>
#include <string.h>
#include <unistd.h>

void termios_make_raw(struct termios *t)
{
    /* Вхід: жодних перетворень над байтами —
       ні обробки BREAK, ні маркування парності, ні відсікання 8-го біта,
       ні нормалізації CR/NL, ні керування потоком XON/XOFF. */
    t->c_iflag &= ~(tcflag_t)(IGNBRK | BRKINT | PARMRK | ISTRIP |
                              INLCR | IGNCR | ICRNL | IXON);

    /* Вихід: OPOST знято — усе, що пише програма, іде в лінію байт у байт
       (саме тому в сирому режимі перевід рядка доводиться писати як \r\n). */
    t->c_oflag &= ~(tcflag_t)OPOST;

    /* Локальні: ні відлуння, ні буферизації рядків, ні сигналів із клавіш,
       ні розширених спецсимволів. Ctrl+C тепер — звичайний байт 0x03. */
    t->c_lflag &= ~(tcflag_t)(ECHO | ECHONL | ICANON | ISIG | IEXTEN);

    /* Кадр: 8 біт без парності. */
    t->c_cflag &= ~(tcflag_t)(CSIZE | PARENB);
    t->c_cflag |= CS8;

    /* read() чекає рівно на один байт і не має таймера. */
    t->c_cc[VMIN]  = 1;
    t->c_cc[VTIME] = 0;
}

int tty_session_open(struct tty_session *s, int fd)
{
    memset(s, 0, sizeof *s);
    s->fd = fd;

    if (!isatty(fd)) {
        errno = ENOTTY;
        return -1;
    }
    if (tcgetattr(fd, &s->saved) < 0)
        return -1;
    s->raw = s->saved;
    return 0;
}

int tty_session_enter_raw(struct tty_session *s, unsigned vmin, unsigned vtime)
{
    struct termios want = s->saved;
    struct termios got;

    termios_make_raw(&want);
    want.c_cc[VMIN]  = (cc_t)vmin;
    want.c_cc[VTIME] = (cc_t)vtime;

    /* TCSAFLUSH: усе, що користувач устиг набрати до перемикання, викидаємо.
       Інакше ці байти прочитаються вже за новими правилами — не тим, для
       чого їх набирали. */
    if (tcsetattr(s->fd, TCSAFLUSH, &want) < 0)
        return -1;

    if (tcgetattr(s->fd, &got) < 0)
        return -1;
    /* Часткове застосування тут особливо небезпечне: лишений ECHO або
       ICANON зіпсує весь подальший діалог із терміналом. */
    if ((got.c_lflag & (ICANON | ECHO | ISIG)) != 0 ||
        (got.c_oflag & OPOST) != 0) {
        errno = EINVAL;
        return -1;
    }

    s->raw    = want;
    s->active = 1;
    return 0;
}

int tty_session_reenter(struct tty_session *s)
{
    /* TCSANOW, а не TCSADRAIN: чекати спустошення черги з обробника
       сигналу не можна — вивід міг бути зупинений по Ctrl+S. */
    if (tcsetattr(s->fd, TCSANOW, &s->raw) < 0)
        return -1;
    s->active = 1;
    return 0;
}

int tty_session_restore(struct tty_session *s)
{
    if (!s->active)
        return 0;
    s->active = 0;
    tty_emulator_reset(s->fd);
    return tcsetattr(s->fd, TCSANOW, &s->saved);
}

void tty_emulator_reset(int fd)
{
    /* Скидання прапорців termios не поверне екран: кінцевий автомат
       емулятора живе окремо й нічого не знає про смерть програми.
       Показати курсор · скинути SGR · G0 = US-ASCII і Shift-In ·
       вимкнути обрамлену вставку, мишу, синхронний кадр · вийти з
       альтернативного екрана · зняти межі прокрутки. */
    static const char seq[] =
        "\033[?25h"
        "\033[0m"
        "\033(B\017"
        "\033[?2004l"
        "\033[?1000l\033[?1002l\033[?1003l\033[?1006l"
        "\033[?2026l"
        "\033[?1049l"
        "\033[r";

    const char *p = seq;
    size_t left = sizeof seq - 1;

    while (left > 0) {
        ssize_t n = write(fd, p, left);
        if (n < 0) {
            if (errno == EINTR)
                continue;
            return;   /* більше нічого не вдіємо: ми можемо бути в обробнику */
        }
        p    += n;
        left -= (size_t)n;
    }
}
