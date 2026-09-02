#include "tty_input.h"

#include <errno.h>
#include <fcntl.h>
#include <termios.h>
#include <unistd.h>

ssize_t tty_drain(int fd, tty_chunk_fn on_chunk, void *user)
{
    unsigned char buf[4096];
    ssize_t total = 0;

    /* Патерн повного спустошення. Без нього epoll у режимі EPOLLET
       більше ніколи не розбудить процес: сповіщення прийшло на ЗМІНУ
       стану, а не на наявність даних. */
    for (;;) {
        ssize_t n = read(fd, buf, sizeof buf);

        if (n > 0) {
            if (on_chunk != NULL)
                on_chunk(buf, (size_t)n, user);
            total += n;
            continue;
        }
        if (n == 0)
            return TTY_DRAIN_EOF;          /* дескриптор закрито з того боку */
        if (errno == EINTR)
            continue;                      /* сигнал — просто пробуємо ще раз */
        if (errno == EAGAIN || errno == EWOULDBLOCK)
            return total;                  /* усе, буфер ядра порожній */
        return TTY_READ_ERROR;
    }
}

int tty_read_byte(int fd, unsigned char *out)
{
    ssize_t n = read(fd, out, 1);

    if (n == 1)
        return 1;
    if (n == 0)
        return 0;
    if (errno == EINTR)
        return TTY_READ_INTERRUPTED;
    return TTY_READ_ERROR;
}

int tty_write_all(int fd, const void *buf, size_t len)
{
    const char *p = buf;

    while (len > 0) {
        ssize_t n = write(fd, p, len);
        if (n < 0) {
            if (errno == EINTR)
                continue;
            return -1;
        }
        p   += n;
        len -= (size_t)n;
    }
    return 0;
}

int tty_set_nonblock(int fd, int on)
{
    int flags = fcntl(fd, F_GETFL, 0);

    if (flags < 0)
        return -1;
    /* O_NONBLOCK старший за VMIN/VTIME: із ним read() на порожньому
       буфері одразу віддає -1/EAGAIN і не запускає жодного таймера. */
    flags = on ? (flags | O_NONBLOCK) : (flags & ~O_NONBLOCK);
    return fcntl(fd, F_SETFL, flags);
}

int tty_set_vmin_vtime(int fd, unsigned vmin, unsigned vtime)
{
    struct termios t;

    if (tcgetattr(fd, &t) < 0)
        return -1;
    t.c_cc[VMIN]  = (cc_t)vmin;
    t.c_cc[VTIME] = (cc_t)vtime;
    return tcsetattr(fd, TCSANOW, &t);
}
