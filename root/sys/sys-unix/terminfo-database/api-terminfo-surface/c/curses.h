#include <curses.h>
#include <term.h>

int        setupterm(const char *term, int filedes, int *errret);
int        tigetflag(const char *cap);
int        tigetnum(const char *cap);
char      *tigetstr(const char *cap);
char      *tparm(const char *str, long p1 /* … */, long p9);
char      *tiparm(const char *str, ...);
int        tputs(const char *str, int affcnt, int (*putc)(int));
int        putp(const char *str);
TERMINAL  *set_curterm(TERMINAL *nterm);
int        del_curterm(TERMINAL *oterm);
int        restartterm(const char *term, int filedes, int *errret);
