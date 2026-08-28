/* serial.c — кадри змінної довжини з послідовного порту.
 * gcc -O2 -Wall -o serial serial.c        запуск: ./serial /dev/ttyUSB0
 */
#define _DEFAULT_SOURCE          /* cfmakeraw і CRTSCTS — розширення поза POSIX */
#include <termios.h>
#include <fcntl.h>
#include <unistd.h>
#include <signal.h>
#include <errno.h>
#include <time.h>
#include <stdio.h>
#include <string.h>

#define CHUNK     128            /* = VMIN; c_cc — масив cc_t, стеля 255 */
#define FRAME_MAX 4096

static volatile sig_atomic_t stop = 0;

static void on_stop(int sig)
{
    (void) sig;
    stop = 1;                    /* більше нічого: решту зробить головний цикл */
}

/* Сирий 8N1 на заданій швидкості; вихідний стан лягає в *saved. */
static int port_setup(int fd, speed_t baud, struct termios *saved)
{
    const tcflag_t want_c = CLOCAL | CREAD;
    struct termios tio, back;

    if (tcgetattr(fd, saved) < 0)          /* знімок ДО будь-яких змін */
        return -1;
    tio = *saved;

    cfmakeraw(&tio);                       /* ICANON, ECHO, ISIG, OPOST, IXON — геть */
    cfsetispeed(&tio, baud);
    cfsetospeed(&tio, baud);

    tio.c_cflag |=  want_c;                /* саме цих двох cfmakeraw НЕ чіпає */
    tio.c_cflag &= ~(CSTOPB | CRTSCTS);    /* один стоповий біт, без RTS/CTS   */
    tio.c_cc[VMIN]  = CHUNK;               /* стільки ж просимо в read()       */
    tio.c_cc[VTIME] = 1;                   /* пауза 100 мс = кінець кадру      */

    if (tcsetattr(fd, TCSAFLUSH, &tio) < 0)
        return -1;

    /* tcsetattr каже «успіх», застосувавши ХОЧ ЩОСЬ. Звіряємо саме замовлене. */
    if (tcgetattr(fd, &back) < 0)
        return -1;
    if ((back.c_lflag & (ICANON | ECHO | ISIG))          != 0      ||
        (back.c_iflag & (IXON | ICRNL | INLCR | ISTRIP)) != 0      ||
        (back.c_oflag &  OPOST)                          != 0      ||
        (back.c_cflag & (PARENB | CSTOPB | CRTSCTS))     != 0      ||
        (back.c_cflag &  CSIZE)                          != CS8    ||
        (back.c_cflag &  want_c)                         != want_c ||
        back.c_cc[VMIN] != CHUNK || back.c_cc[VTIME] != 1          ||
        cfgetospeed(&back) != baud) {
        errno = EINVAL;                    /* драйвер узяв не все */
        return -1;
    }
    return 0;
}

/* Один кадр: діждатися початку й добирати, доки не буде паузи.
 * > 0 — довжина, 0 — пристрій зник, -1 — помилка в errno. */
static ssize_t read_frame(int fd, unsigned char *buf, size_t cap)
{
    size_t len = 0;

    for (;;) {
        ssize_t n;

        if (cap - len < CHUNK) {           /* коротший запит зіпсував би ознаку */
            errno = EMSGSIZE;
            return -1;
        }
        n = read(fd, buf + len, CHUNK);
        if (n < 0)
            return -1;                     /* зокрема EINTR — розбереться той, хто кликав */
        if (n == 0)                        /* перехідник від'єднали */
            return (ssize_t) len;
        len += (size_t) n;
        if (n < CHUNK)                     /* спрацював міжбайтовий таймер */
            return (ssize_t) len;
    }
}

int main(int argc, char **argv)
{
    const char *dev = (argc > 1) ? argv[1] : "/dev/ttyUSB0";
    struct timespec settle = { 1, 500L * 1000 * 1000 };   /* 1.5 с */
    unsigned char frame[FRAME_MAX];
    struct termios saved;
    struct sigaction sa;
    int fd, rc = 0;

    fd = open(dev, O_RDWR | O_NOCTTY);     /* порт не стає керуючим терміналом */
    if (fd < 0) {
        perror(dev);
        return 1;
    }
    if (port_setup(fd, B115200, &saved) < 0) {
        perror("port_setup");
        close(fd);
        return 1;
    }

    memset(&sa, 0, sizeof sa);
    sa.sa_handler = on_stop;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;                       /* без SA_RESTART: хай read() вертає EINTR */
    sigaction(SIGINT,  &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);

    nanosleep(&settle, NULL);              /* DTR на відкритті міг перезапустити плату */
    tcflush(fd, TCIFLUSH);                 /* усе, що встигло прийти дорогою, — геть */

    while (!stop) {
        ssize_t len = read_frame(fd, frame, sizeof frame);
        ssize_t i;

        if (len < 0) {
            if (errno == EINTR)
                continue;                  /* прапорець перевірить умова циклу */
            perror("read");
            rc = 1;
            break;
        }
        if (len == 0) {
            fprintf(stderr, "%s: пристрій зник\n", dev);
            rc = 1;
            break;
        }
        printf("кадр %4zd Б:", len);
        for (i = 0; i < len && i < 8; i++)
            printf(" %02X", frame[i]);
        printf("%s\n", len > 8 ? " …" : "");
    }

    tcsetattr(fd, TCSANOW, &saved);        /* один вихід — одне відновлення */
    close(fd);
    return rc;
}
