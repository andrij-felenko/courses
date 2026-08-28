/* ==========================================================================
 * safe_terminal.c — Надійний менеджер сирого режиму TTY мовою C.
 * Гарантоване відновлення termios через atexit, sigaction та Job Control.
 * ========================================================================== */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <termios.h>
#include <signal.h>
#include <errno.h>

/* Глобальний збережений стан термінала та атомарні прапорці */
static struct termios g_orig_termios;
static struct termios g_raw_termios;
static volatile sig_atomic_t g_is_raw = 0;

/* Асинхронно-сигнально безпечне відновлення початкового стану */
static void restore_terminal_raw(void)
{
    if (g_is_raw) {
        /* tcsetattr належить до переліку Async-Signal-Safe функцій POSIX */
        tcsetattr(STDIN_FILENO, TCSANOW, &g_orig_termios);
        g_is_raw = 0;
    }
}

/* Обробник atexit() для штатного завершення процесу */
static void on_exit_cleanup(void)
{
    restore_terminal_raw();
}

/* Обробник фатальних сигналів (SIGINT, SIGTERM, SIGHUP, SIGQUIT) */
static void on_fatal_signal(int signo)
{
    int saved_errno = errno;
    restore_terminal_raw();

    /* Скидаємо дію на типову (SIG_DFL) та повторно надсилаємо сигнал */
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = SIG_DFL;
    sigemptyset(&sa.sa_mask);
    sigaction(signo, &sa, NULL);

    sigset_t unblock_mask;
    sigemptyset(&unblock_mask);
    sigaddset(&unblock_mask, signo);
    sigprocmask(SIG_UNBLOCK, &unblock_mask, NULL);

    raise(signo);
    errno = saved_errno;
}

/* Обробник призупинення процесу (Job Control: Ctrl+Z) */
static void on_tstp_signal(int signo)
{
    (void)signo;
    int saved_errno = errno;

    /* 1. Повертаємо канонічний режим термінала для оболонки */
    restore_terminal_raw();

    /* 2. Скидаємо обробник на SIG_DFL, щоб ядро призупинило процес */
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = SIG_DFL;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGTSTP, &sa, NULL);

    sigset_t unblock_mask;
    sigemptyset(&unblock_mask);
    sigaddset(&unblock_mask, SIGTSTP);
    sigprocmask(SIG_UNBLOCK, &unblock_mask, NULL);

    /* 3. Надсилаємо SIGTSTP самі собі — процес зупиняється */
    raise(SIGTSTP);

    /* 4. Коли процес повертають на передній план (команда fg),
     * виконання поновлюється з цієї точки. Відновлюємо наш обробник. */
    sa.sa_handler = on_tstp_signal;
    sigaction(SIGTSTP, &sa, NULL);

    errno = saved_errno;
}

/* Обробник поновлення процесу з фону (Job Control: fg / SIGCONT) */
static void on_cont_signal(int signo)
{
    (void)signo;
    int saved_errno = errno;

    /* Повторно перемикаємо термінал у сирий режим */
    if (!g_is_raw) {
        tcsetattr(STDIN_FILENO, TCSAFLUSH, &g_raw_termios);
        g_is_raw = 1;
    }

    errno = saved_errno;
}

/* Налаштування обробників усіх сигналів */
static int setup_signal_handlers(void)
{
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));

    sa.sa_handler = on_fatal_signal;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;

    int fatal_signals[] = { SIGINT, SIGTERM, SIGHUP, SIGQUIT };
    for (size_t i = 0; i < sizeof(fatal_signals) / sizeof(fatal_signals[0]); ++i) {
        if (sigaction(fatal_signals[i], &sa, NULL) < 0) {
            return -1;
        }
    }

    sa.sa_handler = on_tstp_signal;
    if (sigaction(SIGTSTP, &sa, NULL) < 0) {
        return -1;
    }

    sa.sa_handler = on_cont_signal;
    if (sigaction(SIGCONT, &sa, NULL) < 0) {
        return -1;
    }

    return 0;
}

/* Активація сирого режиму TTY */
static int enable_raw_mode(void)
{
    if (!isatty(STDIN_FILENO)) {
        errno = ENOTTY;
        return -1;
    }

    if (tcgetattr(STDIN_FILENO, &g_orig_termios) < 0) {
        return -1;
    }

    if (atexit(on_exit_cleanup) != 0) {
        return -1;
    }

    if (setup_signal_handlers() < 0) {
        return -1;
    }

    g_raw_termios = g_orig_termios;
    cfmakeraw(&g_raw_termios);

    /* Читання від 1 байта без часового ліміту */
    g_raw_termios.c_cc[VMIN] = 1;
    g_raw_termios.c_cc[VTIME] = 0;

    if (tcsetattr(STDIN_FILENO, TCSAFLUSH, &g_raw_termios) < 0) {
        return -1;
    }

    g_is_raw = 1;
    return 0;
}

int main(void)
{
    if (enable_raw_mode() < 0) {
        perror("Помилка ініціалізації термінала");
        return EXIT_FAILURE;
    }

    const char intro[] = "Сирий режим активовано. Натискайте будь-які клавіші (q — вихід, Ctrl+Z — тест Job Control):\r\n";
    (void)write(STDOUT_FILENO, intro, sizeof(intro) - 1);

    unsigned char c = 0;
    while (1) {
        ssize_t n = read(STDIN_FILENO, &c, 1);
        if (n < 0) {
            if (errno == EINTR) {
                continue; /* Перервано сигналом, продовжуємо цикл */
            }
            break;
        }
        if (n == 0) {
            break; /* Кінцевий EOF */
        }

        if (c == 'q') {
            const char msg[] = "\r\nОтримано команду виходу 'q'. Відновлення термінала...\r\n";
            (void)write(STDOUT_FILENO, msg, sizeof(msg) - 1);
            break;
        }

        char buf[64];
        int len = snprintf(buf, sizeof(buf), "Код байта: 0x%02X ('%c')\r\n", c, (c >= 32 && c <= 126) ? c : '.');
        if (len > 0) {
            (void)write(STDOUT_FILENO, buf, (size_t)len);
        }
    }

    return EXIT_SUCCESS;
}
