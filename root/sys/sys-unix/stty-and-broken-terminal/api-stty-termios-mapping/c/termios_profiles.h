#ifndef TERMIOS_PROFILES_H
#define TERMIOS_PROFILES_H

#include <termios.h>

/* Профілі stty, які нічого не роблять із дескриптором — лише правлять
   структуру. Сирий режим живе в tty_session.c: там він потрібен разом
   із поверненням назад. */
void termios_make_sane(struct termios *t);
void termios_make_cooked(struct termios *t);

/* tcsetattr плюс звірка. POSIX дозволяє повернути 0, застосувавши лише
   частину змін, тож питаємо ядро, що воно взяло насправді.
   0 — усе на місці; -1 — помилка виклику або розбіжність (звіт у stderr). */
int termios_apply_verified(int fd, int optional_actions, const struct termios *want);

#endif /* TERMIOS_PROFILES_H */
