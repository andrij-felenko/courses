#include "readpass.h"

#include "tty_input.h"

#include <errno.h>
#include <string.h>
#include <termios.h>
#include <unistd.h>

ssize_t tty_read_password(int fd, const char *prompt, char *buf, size_t size)
{
    struct termios saved, quiet;
    size_t len = 0;
    int overflow = 0;
    ssize_t rc = -1;
    int saved_errno;

    if (size == 0) {
        errno = EINVAL;
        return -1;
    }
    if (tcgetattr(fd, &saved) < 0)
        return -1;

    quiet = saved;
    /* Гасимо саме відлуння, а канонічний режим лишаємо: рядок редагує
       ядро, тож Backspace і Ctrl+U працюють як завжди. */
    quiet.c_lflag &= ~(tcflag_t)(ECHO | ECHOE | ECHOK | ECHONL);
    /* І одразу ECHONL назад: інакше не буде видно навіть переводу рядка
       по Enter — а користувачеві треба знати, що ввід прийнято. */
    quiet.c_lflag |= ECHONL;

    /* TCSAFLUSH викидає все, що вже набрано до цієї миті: інакше воно
       потрапить у пароль, хоч набирали його зовсім не для нас. */
    if (tcsetattr(fd, TCSAFLUSH, &quiet) < 0)
        return -1;

    if (prompt != NULL && tty_write_all(fd, prompt, strlen(prompt)) < 0)
        goto out;

    for (;;) {
        char ch;
        ssize_t n = read(fd, &ch, 1);

        if (n < 0) {
            if (errno == EINTR)
                continue;
            goto out;
        }
        if (n == 0)                 /* ^D на порожньому рядку */
            break;
        if (ch == '\n' || ch == '\r')
            break;
        if (len + 1 < size)
            buf[len++] = ch;
        else
            overflow = 1;           /* дочитуємо рядок до кінця, але не беремо */
    }

    buf[len] = '\0';
    if (overflow) {
        errno = ENOBUFS;
        rc = -1;
    } else {
        rc = (ssize_t)len;
    }

out:
    /* Відлуння повертаємо за будь-якого виходу — навіть аварійного.
       TCSAFLUSH і тут: недочитані байти пароля в буфері нікому не потрібні. */
    saved_errno = errno;
    tcsetattr(fd, TCSAFLUSH, &saved);
    errno = saved_errno;

    if (rc < 0)
        memset(buf, 0, size);
    return rc;
}
