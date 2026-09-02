#ifndef TTY_SESSION_H
#define TTY_SESSION_H

#include <signal.h>
#include <termios.h>

/* Сеанс сирого режиму: пам'ятає стан, у якому термінал був до нас, і вміє
   повернути його — і зі звичайного коду, і з обробника сигналу. */
struct tty_session {
    int                   fd;
    struct termios        saved;   /* стан на вході — його ж і повертаємо */
    struct termios        raw;     /* що ми виставили: треба після SIGCONT */
    volatile sig_atomic_t active;  /* 1, поки сирий режим справді ввімкнено */
};

/* Еквівалент cfmakeraw(): прозорий 8-бітний канал без будь-якої обробки. */
void termios_make_raw(struct termios *t);

int tty_session_open(struct tty_session *s, int fd);
int tty_session_enter_raw(struct tty_session *s, unsigned vmin, unsigned vtime);
int tty_session_restore(struct tty_session *s);

/* Повторний вхід у сирий режим — виклик із обробника SIGCONT/SIGTSTP,
   тому всередині лише tcsetattr(). */
int tty_session_reenter(struct tty_session *s);

/* Скидання модальних регістрів емулятора. Усередині сам лише write(),
   тож дозволене в обробнику сигналу. */
void tty_emulator_reset(int fd);

#endif /* TTY_SESSION_H */
