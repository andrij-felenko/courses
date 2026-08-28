#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <termios.h>
#include <unistd.h>

char *safe_read_passphrase(const char *prompt, char *buf, size_t buf_size) {
    /* 1. Відкриваємо безпосередньо керівний термінал сеансу */
    int tty_fd = open("/dev/tty", O_RDWR | O_NOCTTY);
    if (tty_fd < 0) {
        return NULL; /* Немає керівного термінала (ENXIO) */
    }

    struct termios orig_termios;
    if (tcgetattr(tty_fd, &orig_termios) < 0) {
        close(tty_fd);
        return NULL;
    }

    /* 2. Вимикаємо прапорець відлуння ECHO */
    struct termios no_echo = orig_termios;
    no_echo.c_lflag &= ~(ECHO | ECHOE | ECHOK | ECHONL);
    if (tcsetattr(tty_fd, TCSAFLUSH, &no_echo) < 0) {
        close(tty_fd);
        return NULL;
    }

    /* 3. Виводимо підказку прямо на термінал */
    write(tty_fd, prompt, strlen(prompt));

    /* 4. Зчитуємо пароль */
    size_t i = 0;
    char ch;
    while (i + 1 < buf_size && read(tty_fd, &ch, 1) == 1) {
        if (ch == '\n' || ch == '\r') {
            break;
        }
        buf[i++] = ch;
    }
    buf[i] = '\0';
    write(tty_fd, "\n", 1);

    /* 5. Обов'язково відновлюємо початковий стан термінала */
    tcsetattr(tty_fd, TCSAFLUSH, &orig_termios);
    close(tty_fd);

    return buf;
}
