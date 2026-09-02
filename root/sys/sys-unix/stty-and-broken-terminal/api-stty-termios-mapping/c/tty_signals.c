#include "tty_signals.h"

#include <errno.h>
#include <signal.h>
#include <stddef.h>
#include <string.h>
#include <unistd.h>

/* Обробник не має ні аргументів, ні контексту — тільки статика. */
static struct tty_session   *g_session;
static volatile sig_atomic_t g_resized;

static int install(int signo, void (*fn)(int), int flags)
{
    struct sigaction sa;

    memset(&sa, 0, sizeof sa);
    sa.sa_handler = fn;
    /* Поки працює обробник, решта сигналів чекає: інакше SIGWINCH
       посеред відновлення termios дав би вкладений виклик. */
    sigfillset(&sa.sa_mask);
    sa.sa_flags = flags;
    return sigaction(signo, &sa, NULL);
}

/* Аварійне завершення. Дозволені лише async-signal-safe виклики:
   tcsetattr, write, sigaction, sigprocmask, raise. Ніякого printf. */
static void fatal_handler(int signo)
{
    int saved_errno = errno;

    if (g_session != NULL && g_session->active) {
        /* TCSANOW, а не TCSADRAIN: якщо вивід зупинено по Ctrl+S, черга
           ніколи не спорожніє, і TCSADRAIN зависне просто тут. */
        tcsetattr(g_session->fd, TCSANOW, &g_session->saved);
        tty_emulator_reset(g_session->fd);
        g_session->active = 0;
    }

    /* Далі — самогубство тим самим сигналом, щоб оболонка побачила
       справжню причину смерті, а не рівний _exit(1). */
    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sigemptyset(&sa.sa_mask);
    sa.sa_handler = SIG_DFL;
    sigaction(signo, &sa, NULL);

    sigset_t set;
    sigemptyset(&set);
    sigaddset(&set, signo);
    sigprocmask(SIG_UNBLOCK, &set, NULL);

    raise(signo);

    errno = saved_errno;
}

/* Ctrl+Z. Зупинитися просто так не можна: оболонка дістане термінал
   у сирому режимі й осліпне. */
static void tstp_handler(int signo)
{
    int saved_errno = errno;

    if (g_session != NULL && g_session->active) {
        tcsetattr(g_session->fd, TCSANOW, &g_session->saved);
        tty_emulator_reset(g_session->fd);
        g_session->active = 0;
    }

    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sigemptyset(&sa.sa_mask);
    sa.sa_handler = SIG_DFL;
    sigaction(signo, &sa, NULL);

    sigset_t set;
    sigemptyset(&set);
    sigaddset(&set, signo);
    sigprocmask(SIG_UNBLOCK, &set, NULL);

    raise(signo);          /* ядро спиняє процес рівно тут */

    /* Сюди повертаємось після fg (SIGCONT): відновлюємо свій обробник
       і власний режим термінала. */
    install(signo, tstp_handler, 0);
    if (g_session != NULL)
        tty_session_reenter(g_session);
    g_resized = 1;         /* хай головний цикл перемалює екран */

    errno = saved_errno;
}

/* Якщо процес зупинили не нашим Ctrl+Z (наприклад, kill -STOP),
   сирий режим доведеться повертати вже тут. */
static void cont_handler(int signo)
{
    int saved_errno = errno;

    (void)signo;
    if (g_session != NULL && !g_session->active)
        tty_session_reenter(g_session);
    g_resized = 1;

    errno = saved_errno;
}

static void winch_handler(int signo)
{
    (void)signo;
    /* Єдина дозволена дія — виставити прапорець: ioctl і перемальовування
       робить головний цикл. */
    g_resized = 1;
}

int tty_signals_install(struct tty_session *s)
{
    static const int FATAL[] = {
        SIGINT, SIGQUIT, SIGTERM, SIGHUP, SIGABRT, SIGSEGV, SIGBUS, SIGPIPE
    };

    g_session = s;

    for (size_t i = 0; i < sizeof FATAL / sizeof FATAL[0]; ++i)
        if (install(FATAL[i], fatal_handler, 0) < 0)
            return -1;

    if (install(SIGTSTP, tstp_handler, 0) < 0)
        return -1;
    if (install(SIGCONT, cont_handler, SA_RESTART) < 0)
        return -1;
    /* Свідомо без SA_RESTART: read() має повернути EINTR, щоб цикл
       помітив зміну розміру, а не висів у ядрі. */
    if (install(SIGWINCH, winch_handler, 0) < 0)
        return -1;

    return 0;
}

int tty_signals_resized(void)
{
    if (!g_resized)
        return 0;
    g_resized = 0;
    return 1;
}
