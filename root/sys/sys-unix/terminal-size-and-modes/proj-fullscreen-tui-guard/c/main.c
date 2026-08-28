#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <signal.h>
#include <sys/ioctl.h>
#include <sys/signalfd.h>
#include <sys/select.h>
#include <termios.h>

/* Глобальний контекст для безпечного аварійного відновлення */
static struct {
    int tty_fd;
    struct termios orig_termios;
    bool is_raw;
    bool is_alt_screen;
} g_term_state = { -1, {0}, false, false };

/* Процедура гарантованого скидання стану термінала */
static void terminal_cleanup(void) {
    if (g_term_state.tty_fd < 0) {
        return;
    }

    /* 1. Показуємо курсор, повертаємо основний екран і скидаємо оформлення */
    if (g_term_state.is_alt_screen) {
        const char restore_seq[] = "\x1b[?25h\x1b[?1049l\x1b[0m";
        (void)write(g_term_state.tty_fd, restore_seq, sizeof(restore_seq) - 1);
        g_term_state.is_alt_screen = false;
    }

    /* 2. Відновлюємо початкові параметри лінії termios */
    if (g_term_state.is_raw) {
        (void)tcsetattr(g_term_state.tty_fd, TCSAFLUSH, &g_term_state.orig_termios);
        g_term_state.is_raw = false;
    }
}

/* Обробник критичних сигналів: скидає стан і дозволяє ядру створити core dump */
static void emergency_signal_handler(int sig) {
    terminal_cleanup();

    /* Скидаємо дію на стандартну та перевикликаємо сигнал */
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = SIG_DFL;
    sigemptyset(&sa.sa_mask);
    sigaction(sig, &sa, NULL);
    raise(sig);
}

/* Опитування поточної геометрії вікна з ланцюжком fallback */
static bool get_window_size(int fd, int *out_rows, int *out_cols) {
    struct winsize ws;
    if (ioctl(fd, TIOCGWINSZ, &ws) == 0 && ws.ws_row > 0 && ws.ws_col > 0) {
        *out_rows = ws.ws_row;
        *out_cols = ws.ws_col;
        return true;
    }

    /* Fallback 1: змінні середовища LINES та COLUMNS */
    const char *env_lines = getenv("LINES");
    const char *env_cols = getenv("COLUMNS");
    if (env_lines && env_cols) {
        int r = atoi(env_lines);
        int c = atoi(env_cols);
        if (r > 0 && c > 0) {
            *out_rows = r;
            *out_cols = c;
            return true;
        }
    }

    /* Fallback 2: стандартне значення VT100 */
    *out_rows = 24;
    *out_cols = 80;
    return false;
}

/* Перемалювання простого інформаційного кадру */
static void render_screen(int fd, int rows, int cols, int frame_count) {
    char buf[1024];
    /* Очищення екрана та переміщення курсора у лівий верхній кут */
    const char clear_cmd[] = "\x1b[2J\x1b[H";
    (void)write(fd, clear_cmd, sizeof(clear_cmd) - 1);

    /* Рядок заголовка */
    int len = snprintf(buf, sizeof(buf),
        "\x1b[1;37;44m TUI Guard Demo \x1b[0m — Розмір: \x1b[1;32m%d×%d\x1b[0m | Кадр: \x1b[1;33m#%d\x1b[0m\r\n",
        cols, rows, frame_count);
    (void)write(fd, buf, len);

    /* Інструкція для користувача */
    const char *msg1 = "Натисніть 'q' для виходу або змініть розмір вікна емулятора.\r\n";
    (void)write(fd, msg1, strlen(msg1));

    /* Статусний рядок у нижній частині вікна */
    len = snprintf(buf, sizeof(buf), "\x1b[%d;1H\x1b[7m [Q: Вихід] | [SIGWINCH: signalfd active] \x1b[0m", rows);
    (void)write(fd, buf, len);
}

int main(void) {
    /* 1. Перевірка інтерактивності */
    if (!isatty(STDIN_FILENO)) {
        fprintf(stderr, "Помилка: програма вимагає інтерактивного термінала.\n");
        return EXIT_FAILURE;
    }
    g_term_state.tty_fd = STDIN_FILENO;

    /* 2. Збереження початкового стану termios */
    if (tcgetattr(g_term_state.tty_fd, &g_term_state.orig_termios) == -1) {
        perror("tcgetattr");
        return EXIT_FAILURE;
    }

    /* 3. Реєстрація очищення в atexit */
    if (atexit(terminal_cleanup) != 0) {
        fprintf(stderr, "Не вдалося зареєструвати atexit handler.\n");
        return EXIT_FAILURE;
    }

    /* 4. Встановлення перехоплення фатальних збоїв */
    struct sigaction sa_fault;
    memset(&sa_fault, 0, sizeof(sa_fault));
    sa_fault.sa_handler = emergency_signal_handler;
    sigemptyset(&sa_fault.sa_mask);
    sa_fault.sa_flags = SA_RESETHAND;
    sigaction(SIGSEGV, &sa_fault, NULL);
    sigaction(SIGBUS, &sa_fault, NULL);
    sigaction(SIGABRT, &sa_fault, NULL);

    /* 5. Блокування сигналів для синхронного читання через signalfd */
    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, SIGWINCH);
    sigaddset(&mask, SIGINT);
    sigaddset(&mask, SIGTERM);
    sigaddset(&mask, SIGHUP);

    if (sigprocmask(SIG_BLOCK, &mask, NULL) == -1) {
        perror("sigprocmask");
        return EXIT_FAILURE;
    }

    int sfd = signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC);
    if (sfd == -1) {
        perror("signalfd");
        return EXIT_FAILURE;
    }

    /* 6. Налаштування сирого режиму termios */
    struct termios raw = g_term_state.orig_termios;
    raw.c_iflag &= ~(BRKINT | ICRNL | INPCK | ISTRIP | IXON);
    raw.c_oflag &= ~(OPOST);
    raw.c_cflag |= (CS8);
    raw.c_lflag &= ~(ECHO | ICANON | IEXTEN | ISIG);
    raw.c_cc[VMIN] = 1;
    raw.c_cc[VTIME] = 0;

    if (tcsetattr(g_term_state.tty_fd, TCSAFLUSH, &raw) == -1) {
        perror("tcsetattr raw");
        close(sfd);
        return EXIT_FAILURE;
    }
    g_term_state.is_raw = true;

    /* 7. Активація альтернативного буфера та приховування курсора */
    const char enter_seq[] = "\x1b[?1049h\x1b[?25l";
    (void)write(g_term_state.tty_fd, enter_seq, sizeof(enter_seq) - 1);
    g_term_state.is_alt_screen = true;

    /* 8. Головний цикл опитування */
    int rows = 24, cols = 80, frame = 0;
    get_window_size(g_term_state.tty_fd, &rows, &cols);
    render_screen(g_term_state.tty_fd, rows, cols, ++frame);

    bool running = true;
    while (running) {
        fd_set read_fds;
        FD_ZERO(&read_fds);
        FD_SET(STDIN_FILENO, &read_fds);
        FD_SET(sfd, &read_fds);
        int max_fd = (STDIN_FILENO > sfd ? STDIN_FILENO : sfd) + 1;

        if (select(max_fd, &read_fds, NULL, NULL, NULL) == -1) {
            if (errno == EINTR) continue;
            perror("select");
            break;
        }

        /* Обробка системних сигналів */
        if (FD_ISSET(sfd, &read_fds)) {
            struct signalfd_siginfo fdsi;
            ssize_t s = read(sfd, &fdsi, sizeof(fdsi));
            if (s == sizeof(fdsi)) {
                if (fdsi.ssi_signo == SIGWINCH) {
                    get_window_size(g_term_state.tty_fd, &rows, &cols);
                    render_screen(g_term_state.tty_fd, rows, cols, ++frame);
                } else if (fdsi.ssi_signo == SIGINT || fdsi.ssi_signo == SIGTERM || fdsi.ssi_signo == SIGHUP) {
                    running = false;
                }
            }
        }

        /* Обробка вводу користувача */
        if (FD_ISSET(STDIN_FILENO, &read_fds)) {
            char ch;
            if (read(STDIN_FILENO, &ch, 1) == 1) {
                if (ch == 'q' || ch == 'Q') {
                    running = false;
                } else {
                    render_screen(g_term_state.tty_fd, rows, cols, ++frame);
                }
            }
        }
    }

    close(sfd);
    /* terminal_cleanup() викликається автоматично через atexit */
    return EXIT_SUCCESS;
}
