/* Безпечне керування терміналом мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <termios.h>
#include <signal.h>
#include <errno.h>

static struct termios orig_termios;
static volatile sig_atomic_t raw_active = 0;

static void restore_raw_mode(void)
{
    if (raw_active) {
        /* tcsetattr є асинхронно-сигнально безпечною функцією POSIX */
        tcsetattr(STDIN_FILENO, TCSANOW, &orig_termios);
        raw_active = 0;
    }
}

static void fatal_handler(int signo)
{
    int saved_errno = errno;
    restore_raw_mode();

    /* Скидання на SIG_DFL та повторний виклик сигналу */
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = SIG_DFL;
    sigemptyset(&sa.sa_mask);
    sigaction(signo, &sa, NULL);

    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, signo);
    sigprocmask(SIG_UNBLOCK, &mask, NULL);

    raise(signo);
    errno = saved_errno;
}

static void exit_cleanup(void)
{
    restore_raw_mode();
}

int enable_safe_raw(void)
{
    if (!isatty(STDIN_FILENO))
        return -1;

    if (tcgetattr(STDIN_FILENO, &orig_termios) < 0)
        return -1;

    atexit(exit_cleanup);

    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = fatal_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;

    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);
    sigaction(SIGHUP, &sa, NULL);
    sigaction(SIGQUIT, &sa, NULL);

    struct termios raw = orig_termios;
    cfmakeraw(&raw);
    raw.c_cc[VMIN] = 1;
    raw.c_cc[VTIME] = 0;

    if (tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw) < 0)
        return -1;

    raw_active = 1;
    return 0;
}
