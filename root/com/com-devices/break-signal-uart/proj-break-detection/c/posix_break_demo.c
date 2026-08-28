/* posix_break_demo.c - Керування та виявлення Break у Linux */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>
#include <sys/ioctl.h>
#include <errno.h>

int open_and_configure_port(const char *device) {
    int fd = open(device, O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (fd < 0) {
        perror("open failed");
        return -1;
    }

    struct termios tty;
    if (tcgetattr(fd, &tty) != 0) {
        perror("tcgetattr failed");
        close(fd);
        return -1;
    }

    /* Налаштування швидкості 115200 8N1 у сирому (raw) режимі */
    cfsetospeed(&tty, B115200);
    cfsetispeed(&tty, B115200);

    tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8;
    tty.c_cflag |= (CLOCAL | CREAD);
    tty.c_cflag &= ~(PARENB | PARODD | CSTOPB | CRTSCTS);

    /* 
     * Вхідні прапорці:
     * - Вимикаємо IGNBRK (щоб НЕ викидати Break)
     * - Вимикаємо BRKINT (щоб НЕ генерувати SIGINT)
     * - Вмикаємо PARMRK (щоб закодувати Break як \377 \0 \0)
     */
    tty.c_iflag &= ~(IGNBRK | BRKINT | IGNPAR | INLCR | ICRNL | IXON | IXOFF);
    tty.c_iflag |= PARMRK;
    tty.c_lflag = 0; /* Raw режим без канонічної обробки */
    tty.c_oflag = 0;

    if (tcsetattr(fd, TCSANOW, &tty) != 0) {
        perror("tcsetattr failed");
        close(fd);
        return -1;
    }

    return fd;
}

int main(int argc, char *argv[]) {
    const char *port_name = (argc > 1) ? argv[1] : "/dev/ttyUSB0";
    int fd = open_and_configure_port(port_name);
    if (fd < 0) return EXIT_FAILURE;

    printf("Порт %s відкрито. Відправляємо довгий Break (250 мс)...\n", port_name);

    /* 1. Відправка апаратного розриву лінії */
    if (tcsendbreak(fd, 0) != 0) {
        perror("tcsendbreak failed");
    } else {
        printf("Сигнал Break успішно надіслано в лінію.\n");
    }

    printf("Слухаємо лінію... (Очікування маркера Break: 0xFF 0x00 0x00)\n");
    uint8_t buf[256];
    for (int iter = 0; iter < 100; ++iter) {
        ssize_t n = read(fd, buf, sizeof(buf));
        if (n > 0) {
            for (ssize_t i = 0; i < n; ++i) {
                /* Перевірка трьохбайтової екранованої послідовності PARMRK */
                if (i + 2 < n && buf[i] == 0xFF && buf[i + 1] == 0x00 && buf[i + 2] == 0x00) {
                    printf(">>> [ВИЯВЛЕНО BREAK CONDITION НА ЛІНІЇ RX!]\n");
                    i += 2;
                } else {
                    printf("Байт даних: 0x%02X\n", buf[i]);
                }
            }
        }
        usleep(50000); /* 50 мс */
    }

    close(fd);
    return EXIT_SUCCESS;
}
