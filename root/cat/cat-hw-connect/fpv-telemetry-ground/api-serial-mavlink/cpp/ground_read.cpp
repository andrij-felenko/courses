// ground_read.cpp — відкрити наземний модуль і читати прозорий потік (POSIX termios).
// Це «сирий UART» боку: так порт відкривають у прошивці/на мікроконтролері поряд.
// Збірка:  g++ ground_read.cpp -o ground_read
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <fcntl.h>
#include <unistd.h>
#include <termios.h>

int open_serial(const char *dev, speed_t baud) {
    int fd = open(dev, O_RDWR | O_NOCTTY);   // O_NOCTTY — порт нам не керівний термінал
    if (fd < 0) { perror("open"); return -1; }

    struct termios tio;
    if (tcgetattr(fd, &tio) != 0) { perror("tcgetattr"); close(fd); return -1; }

    cfmakeraw(&tio);              // «сирий» режим: без обробки рядків, без ехо — чиста труба
    cfsetispeed(&tio, baud);      // швидкість читання
    cfsetospeed(&tio, baud);      // швидкість запису
    tio.c_cflag &= ~PARENB;       // без парності          ┐
    tio.c_cflag &= ~CSTOPB;       // 1 стоп-біт             ├ разом це «8N1»
    tio.c_cflag &= ~CSIZE;        //                        │
    tio.c_cflag |=  CS8;          // 8 біт даних            ┘
    tio.c_cflag |= (CLOCAL | CREAD);   // ігнорувати лінії модему, дозволити читання
    tio.c_cc[VMIN]  = 0;          // read() не блокує назавжди…
    tio.c_cc[VTIME] = 10;         // …а чекає щонайбільше 1.0 с (VTIME у децисекундах)

    if (tcsetattr(fd, TCSANOW, &tio) != 0) { perror("tcsetattr"); close(fd); return -1; }
    return fd;
}

int main() {
    // Linux: "/dev/ttyUSB0" (міст CP210x/CH340) або "/dev/ttyACM0".
    int fd = open_serial("/dev/ttyUSB0", B57600);   // 57600 — локальна швидкість, не ефір!
    if (fd < 0) return 1;

    printf("порт відкрито на 57600 бод — читаю прозорий потік…\n");
    uint8_t buf[256];
    for (;;) {
        ssize_t n = read(fd, buf, sizeof buf);   // до 256 байтів або поки не спливе VTIME
        if (n > 0) {
            for (ssize_t i = 0; i < n; i++) printf("%02X ", buf[i]);
            printf("\n"); fflush(stdout);
        }
        // щоб ЩОСЬ послати на дрон — пишемо в той самий fd, байти летять в ефір прозоро:
        // write(fd, data, len);
    }
    close(fd);
    return 0;
}
