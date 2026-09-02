#ifndef TTY_SIGNALS_H
#define TTY_SIGNALS_H

#include "tty_session.h"

/* Сигнальний протокол сеансу сирого режиму:
     SIGINT/SIGQUIT/SIGTERM/SIGHUP та аварійні SIGSEGV/SIGBUS/SIGABRT —
       відновити термінал і перевидати сигнал самому собі;
     SIGTSTP/SIGCONT — коректний Ctrl+Z і повернення через fg;
     SIGWINCH — прапорець для головного циклу. */
int tty_signals_install(struct tty_session *s);

/* 1, якщо розмір вікна змінювався; прапорець при цьому скидається. */
int tty_signals_resized(void);

#endif /* TTY_SIGNALS_H */
