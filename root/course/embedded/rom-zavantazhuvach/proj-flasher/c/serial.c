#define _POSIX_C_SOURCE 200809L
#define _DEFAULT_SOURCE

#include "serial.h"

#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <string.h>
#include <sys/ioctl.h>
#include <termios.h>
#include <time.h>
#include <unistd.h>

static uint64_t now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000u + (uint64_t)(ts.tv_nsec / 1000000L);
}

static void sleep_ms(unsigned ms)
{
    struct timespec ts;
    ts.tv_sec = (time_t)(ms / 1000u);
    ts.tv_nsec = (long)(ms % 1000u) * 1000000L;
    /* nanosleep може урватися сигналом — досипаємо залишок */
    while (nanosleep(&ts, &ts) != 0 && errno == EINTR) {
    }
}

bool serial_open(serial_port *port, const char *path)
{
    port->fd = open(path, O_RDWR | O_NOCTTY);
    if (port->fd < 0) {
        return false;
    }
    if (!isatty(port->fd)) {
        close(port->fd);
        port->fd = -1;
        errno = ENOTTY;
        return false;
    }

    struct termios tty;
    memset(&tty, 0, sizeof tty);
    if (tcgetattr(port->fd, &tty) != 0) {
        close(port->fd);
        port->fd = -1;
        return false;
    }

    cfsetispeed(&tty, B115200);
    cfsetospeed(&tty, B115200);

    tty.c_cflag = (tty.c_cflag & ~(tcflag_t)CSIZE) | CS8; /* 8 бітів даних */
    tty.c_cflag |= PARENB;                                /* парність увімкнена */
    tty.c_cflag &= ~(tcflag_t)PARODD;                     /* саме Even: кадр 8E1 */
    tty.c_cflag &= ~(tcflag_t)CSTOPB;                     /* рівно 1 стоп-біт */
    tty.c_cflag &= ~(tcflag_t)CRTSCTS;                    /* DTR/RTS нам потрібні як GPIO */
    tty.c_cflag |= (CLOCAL | CREAD);

    /* Жодної інтерпретації байтів: прошивка — двійковий потік.
       Знімаємо XON/XOFF, інакше байт 0x13 усередині образу зупинить передачу. */
    tty.c_iflag &= ~(tcflag_t)(IXON | IXOFF | IXANY | INLCR | ICRNL | IGNCR | ISTRIP | BRKINT);
    tty.c_iflag |= INPCK; /* перевіряти парність на прийомі */
    tty.c_oflag = 0;
    tty.c_lflag = 0; /* не канонічний режим, без ECHO і без ISIG */

    tty.c_cc[VMIN] = 0;
    tty.c_cc[VTIME] = 10; /* 1.0 с посимвольно — read() не зависає назавжди */

    if (tcsetattr(port->fd, TCSANOW, &tty) != 0) {
        close(port->fd);
        port->fd = -1;
        return false;
    }

    tcflush(port->fd, TCIOFLUSH);
    return true;
}

void serial_close(serial_port *port)
{
    if (port->fd >= 0) {
        close(port->fd);
        port->fd = -1;
    }
}

void serial_flush(const serial_port *port)
{
    tcflush(port->fd, TCIOFLUSH);
}

bool serial_write_all(const serial_port *port, const uint8_t *data, size_t len)
{
    size_t sent = 0;
    while (sent < len) {
        ssize_t n = write(port->fd, data + sent, len - sent);
        if (n > 0) {
            sent += (size_t)n;
            continue;
        }
        if (n < 0 && errno == EINTR) {
            continue;
        }
        return false;
    }
    /* Чекаємо, поки байти справді підуть у лінію: далі ми одразу слухаємо відповідь */
    return tcdrain(port->fd) == 0;
}

bool serial_read_exact(const serial_port *port, uint8_t *buf, size_t len, unsigned timeout_ms)
{
    const uint64_t deadline = now_ms() + timeout_ms;
    size_t got = 0;

    while (got < len) {
        const uint64_t now = now_ms();
        if (now >= deadline) {
            return false;
        }

        struct pollfd pfd;
        pfd.fd = port->fd;
        pfd.events = POLLIN;
        pfd.revents = 0;

        int pr = poll(&pfd, 1, (int)(deadline - now));
        if (pr < 0) {
            if (errno == EINTR) {
                continue;
            }
            return false;
        }
        if (pr == 0) {
            return false; /* завантажувач мовчить */
        }

        ssize_t n = read(port->fd, buf + got, len - got);
        if (n > 0) {
            got += (size_t)n;
            continue;
        }
        if (n < 0 && (errno == EINTR || errno == EAGAIN)) {
            continue;
        }
        if (n == 0) {
            continue; /* спрацював VTIME, час іще лишився */
        }
        return false;
    }
    return true;
}

/* DTR і RTS керують двома транзисторами: Q1 тримає NRST, Q2 — BOOT0. */
static bool set_lines(int fd, bool dtr, bool rts)
{
    int bits = 0;
    if (ioctl(fd, TIOCMGET, &bits) < 0) {
        return false;
    }
    if (dtr) {
        bits |= TIOCM_DTR;
    } else {
        bits &= ~TIOCM_DTR;
    }
    if (rts) {
        bits |= TIOCM_RTS;
    } else {
        bits &= ~TIOCM_RTS;
    }
    return ioctl(fd, TIOCMSET, &bits) == 0;
}

bool serial_enter_bootloader(const serial_port *port)
{
    /* DTR = 0, RTS = 1 — відкривається Q2, BOOT0 підтягується до VCC
       і конденсатор на цьому піні встигає набрати заряд */
    if (!set_lines(port->fd, false, true)) {
        return false;
    }
    sleep_ms(20);

    /* DTR = 1, RTS = 0 — відкривається Q1, NRST притиснуто до землі */
    if (!set_lines(port->fd, true, false)) {
        return false;
    }
    sleep_ms(80);

    /* Обидві лінії в нуль: скидання відпущено, BOOT0 ще високий за рахунок заряду */
    if (!set_lines(port->fd, false, false)) {
        return false;
    }

    /* Ядру треба час на HSI і старт System Memory. Раніший 0x7F просто пропаде. */
    sleep_ms(100);
    serial_flush(port);
    return true;
}
