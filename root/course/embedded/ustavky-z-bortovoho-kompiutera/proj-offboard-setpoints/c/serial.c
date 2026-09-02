#include "serial.h"

#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

static int64_t mono_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (int64_t)ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
}

int serial_open(const char *port, speed_t baud) {
    int fd = open(port, O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (fd < 0) {
        return -1;
    }

    struct termios tty;
    memset(&tty, 0, sizeof(tty));
    if (tcgetattr(fd, &tty) != 0) {
        int saved = errno;
        close(fd);
        errno = saved;
        return -1;
    }

    cfmakeraw(&tty);
    if (cfsetispeed(&tty, baud) != 0 || cfsetospeed(&tty, baud) != 0) {
        int saved = errno;
        close(fd);
        errno = saved;
        return -1;
    }

    tty.c_cflag |= (CLOCAL | CREAD);  /* лінія локальна, приймач увімкнено */
    tty.c_cflag &= ~CRTSCTS;          /* телеметричний джгут без RTS/CTS */
    tty.c_cc[VMIN] = 0;               /* read() ніколи не чекає на байти */
    tty.c_cc[VTIME] = 0;

    if (tcsetattr(fd, TCSANOW, &tty) != 0) {
        int saved = errno;
        close(fd);
        errno = saved;
        return -1;
    }

    /* Сміття, що накопичилось у драйвері до нашого старту: недорозібраний
     * хвіст кадру збив би синхронізацію парсера на перших пакетах. */
    tcflush(fd, TCIOFLUSH);
    return fd;
}

int serial_write_all(int fd, const uint8_t *data, size_t len, int timeout_ms) {
    size_t sent = 0;
    int64_t deadline = mono_ms() + timeout_ms;

    while (sent < len) {
        ssize_t n = write(fd, data + sent, len - sent);
        if (n > 0) {
            sent += (size_t)n;
            continue;
        }
        if (n < 0 && errno == EINTR) {
            continue;
        }
        if (n < 0 && errno != EAGAIN && errno != EWOULDBLOCK) {
            return -1;
        }

        /* Буфер драйвера повний — чекаємо на місце, але не довше дедлайну. */
        int left = (int)(deadline - mono_ms());
        if (left <= 0) {
            errno = ETIMEDOUT;
            return -1;
        }
        struct pollfd pfd;
        pfd.fd = fd;
        pfd.events = POLLOUT;
        pfd.revents = 0;
        int r = poll(&pfd, 1, left);
        if (r < 0) {
            if (errno == EINTR) {
                continue;
            }
            return -1;
        }
        if (r == 0) {
            errno = ETIMEDOUT;
            return -1;
        }
    }
    return 0;
}

ssize_t serial_read_available(int fd, uint8_t *buf, size_t cap) {
    for (;;) {
        ssize_t n = read(fd, buf, cap);
        if (n >= 0) {
            return n;
        }
        if (errno == EINTR) {
            continue;
        }
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            return 0;
        }
        return -1;
    }
}

void serial_close(int fd) {
    if (fd >= 0) {
        close(fd);
    }
}
