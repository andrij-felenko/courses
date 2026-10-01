#include <fcntl.h>
#include <unistd.h>
#include <termios.h>
#include <stdio.h>

int open_ch340_port(const char *port_path) {
    int fd = open(port_path, O_RDWR | O_NOCTTY | O_NDELAY);
    if (fd < 0) {
        perror("Помилка відкриття файлового дескриптора CH340");
        return -1;
    }
    fcntl(fd, F_SETFL, 0);

    struct termios options;
    if (tcgetattr(fd, &options) == 0) {
        options.c_cc[VMIN] = 0;   // Не чекати мінімальної кількості байтів
        options.c_cc[VTIME] = 10; // Таймаут 1.0 секунда (10 * 100 мс)
        tcsetattr(fd, TCSANOW, &options);
    }
    return fd;
}
