#include <signal.h>

struct sigaction {
    void     (*sa_handler)(int);
    void     (*sa_sigaction)(int, siginfo_t *, void *);
    sigset_t   sa_mask;      /* що блокувати на час роботи обробника */
    int        sa_flags;     /* сюди йде SA_RESTART */
    void     (*sa_restorer)(void);   /* службове, програма не заповнює */
};

int sigaction(int signum, const struct sigaction *act,
              struct sigaction *oldact);   /* 0 або -1 з errno */
