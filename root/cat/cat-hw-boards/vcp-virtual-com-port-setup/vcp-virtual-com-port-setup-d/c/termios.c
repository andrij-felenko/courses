#include <termios.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>

int configure_vcp_port(const char *port_path) {
    int fd = open(port_path, O_RDWR | O_NOCTTY | O_NDELAY);
    if (fd == -1) return -1;

    struct termios options;
    tcgetattr(fd, &options);

    /* Встановлення швидкості прийому та передачі 115200 baud */
    cfsetispeed(&options, B115200);
    cfsetospeed(&options, B115200);

    /* Формат кадру 8N1: 8 бітів даних, без парності, 1 стоповий біт */
    options.c_cflag &= ~PARENB;        /* Вимкнути біт парності */
    options.c_cflag &= ~CSTOPB;        /* 1 стоповий біт */
    options.c_cflag &= ~CSIZE;
    options.c_cflag |= CS8;            /* 8 бітів даних */
    options.c_cflag |= (CLOCAL | CREAD); /* Увімкнути приймач */

    /* Вимкнення апаратного та програмного керування потоком */
    options.c_cflag &= ~CRTSCTS;
    options.c_iflag &= ~(IXON | IXOFF | IXANY);

    /* Неканонічний режим вводу (сирі дані) */
    options.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);

    /* Трансляція LF у CRLF при виводі */
    options.c_oflag |= ONLCR;

    tcsetattr(fd, TCSANOW, &options);
    return fd;
}
