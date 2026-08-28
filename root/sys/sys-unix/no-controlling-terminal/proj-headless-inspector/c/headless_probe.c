/* headless_probe.c
   cc -std=c11 -D_GNU_SOURCE -Wall -Wextra -o headless_probe headless_probe.c */

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <termios.h>
#include <unistd.h>

/* Структура звіту про стан термінального контексту */
struct terminal_status {
    int stdin_is_tty;
    int stdout_is_tty;
    int stderr_is_tty;
    int dev_tty_fd;
    int dev_tty_errno;
    int kernel_tty_nr;
};

/* Читання поля tty_nr (7-ме поле) з /proc/self/stat */
static int read_kernel_tty_nr(void)
{
    int fd = open("/proc/self/stat", O_RDONLY | O_CLOEXEC);
    if (fd < 0) {
        return -1;
    }

    char buf[512];
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    close(fd);

    if (n <= 0) {
        return -1;
    }
    buf[n] = '\0';

    /* Пропускаємо PID та назву програми у дужках (наприклад: "12345 (bash) S ...") */
    char *rparen = strrchr(buf, ')');
    if (!rparen) {
        return -1;
    }

    char state;
    int ppid, pgrp, session, tty_nr = 0;
    if (sscanf(rparen + 1, " %c %d %d %d %d", &state, &ppid, &pgrp, &session, &tty_nr) != 5) {
        return -1;
    }

    return tty_nr;
}

/* Збір повної діагностики середовища */
static struct terminal_status inspect_environment(void)
{
    struct terminal_status st;
    st.stdin_is_tty = isatty(STDIN_FILENO);
    st.stdout_is_tty = isatty(STDOUT_FILENO);
    st.stderr_is_tty = isatty(STDERR_FILENO);
    st.kernel_tty_nr = read_kernel_tty_nr();

    /* Спроба відкрити керуючий термінал процесу */
    st.dev_tty_fd = open("/dev/tty", O_RDWR | O_NOCTTY | O_CLOEXEC);
    if (st.dev_tty_fd < 0) {
        st.dev_tty_errno = errno;
    } else {
        st.dev_tty_errno = 0;
    }

    return st;
}

/* Безпечне читання пароля з вимкненням луни (якщо доступний TTY)
   або читання з stdin у неінтерактивному режимі */
static int read_secret_safe(char *buf, size_t max_len, const char *prompt)
{
    int tty_fd = open("/dev/tty", O_RDWR | O_NOCTTY | O_CLOEXEC);

    if (tty_fd >= 0) {
        /* Інтерактивний шлях: є прямий зв'язок з терміналом */
        struct termios orig_termios, raw_termios;
        tcgetattr(tty_fd, &orig_termios);
        raw_termios = orig_termios;
        raw_termios.c_lflag &= ~(ECHO); /* Вимикаємо відображення символів */

        tcsetattr(tty_fd, TCSAFLUSH, &raw_termios);
        dprintf(tty_fd, "%s", prompt);

        char *res = fgets(buf, (int)max_len, fdopen(tty_fd, "r"));
        tcsetattr(tty_fd, TCSAFLUSH, &orig_termios);
        dprintf(tty_fd, "\n");
        close(tty_fd);

        if (!res) {
            return -1;
        }
    } else if (errno == ENXIO || errno == ENOENT || errno == ENODEV) {
        /* Неінтерактивний шлях (headless): читаємо з пайпу stdin */
        fprintf(stderr, "[headless] Термінала немає (/dev/tty: %s). Читаємо секрет зі stdin...\n",
                strerror(errno));
        if (!fgets(buf, (int)max_len, stdin)) {
            return -1;
        }
    } else {
        perror("open(/dev/tty)");
        return -1;
    }

    /* Прибираємо символ нового рядка наприкінці */
    size_t len = strlen(buf);
    if (len > 0 && buf[len - 1] == '\n') {
        buf[len - 1] = '\0';
    }

    return 0;
}

int main(void)
{
    /* Запобігаємо зависанню логів: перемикаємо stdout на лінійну буферизацію */
    setvbuf(stdout, NULL, _IOLBF, 0);

    struct terminal_status st = inspect_environment();

    printf("=== ДІАГНОСТИКА ТЕРМІНАЛЬНОГО КОНТЕКСТУ ===\n");
    printf("STDIN  (fd 0) isatty: %s\n", st.stdin_is_tty ? "ТАК (термінал)" : "НІ (пайп/файл/null)");
    printf("STDOUT (fd 1) isatty: %s\n", st.stdout_is_tty ? "ТАК (термінал)" : "НІ (пайп/файл/null)");
    printf("STDERR (fd 2) isatty: %s\n", st.stderr_is_tty ? "ТАК (термінал)" : "НІ (пайп/файл/null)");
    printf("Ядро (proc stat tty_nr): %d %s\n",
           st.kernel_tty_nr,
           st.kernel_tty_nr == 0 ? "(керуючий термінал ВІДСУТНІЙ)" : "(прив'язаний до пристрою)");

    if (st.dev_tty_fd >= 0) {
        printf("open(\"/dev/tty\"): УСПІХ (отримано fd %d)\n", st.dev_tty_fd);
        close(st.dev_tty_fd);
    } else {
        printf("open(\"/dev/tty\"): ПОМИЛКА errno=%d (%s)\n",
               st.dev_tty_errno, strerror(st.dev_tty_errno));
        if (st.dev_tty_errno == ENXIO) {
            printf("  -> Підтверджено ENXIO: процес виконується у фоні / без сеансу TTY.\n");
        }
    }

    printf("\n--- ТЕСТ ВВЕДЕННЯ ПАРОЛЯ ---\n");
    char secret[64] = {0};
    if (read_secret_safe(secret, sizeof(secret), "Введіть пароль: ") == 0) {
        printf("Секрет успішно отримано (довжина: %zu байтів).\n", strlen(secret));
    } else {
        fprintf(stderr, "Помилка читання секрету!\n");
        return 1;
    }

    return 0;
}
