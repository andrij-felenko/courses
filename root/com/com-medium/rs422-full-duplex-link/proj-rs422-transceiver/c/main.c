#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <termios.h>

// Відкриття та налаштування порту RS-422 на задану швидкість
int rs422_open(const char *port_path, speed_t baud_rate) {
    int fd = open(port_path, O_RDWR | O_NOCTTY | O_NDELAY);
    if (fd < 0) {
        perror("Помилка відкриття порту RS-422");
        return -1;
    }

    // Скидаємо прапорець неблокуючого доступу для штатних операцій читання
    fcntl(fd, F_SETFL, 0);

    struct termios tty;
    if (tcgetattr(fd, &tty) != 0) {
        perror("Помилка отримання атрибутів termios");
        close(fd);
        return -1;
    }

    // Встановлення швидкості прийому та передачі
    cfsetispeed(&tty, baud_rate);
    cfsetospeed(&tty, baud_rate);

    // Формат кадру: 8 біт даних, 1 стоп-біт, без контролю парності (8N1)
    tty.c_cflag &= ~PARENB;         // Без біта парності
    tty.c_cflag &= ~CSTOPB;         // 1 стоп-біт (не 2)
    tty.c_cflag &= ~CSIZE;          // Скидання маски розміру символу
    tty.c_cflag |= CS8;             // 8 бітів на байт
    tty.c_cflag &= ~CRTSCTS;        // Без апаратного керування RTS/CTS
    tty.c_cflag |= (CLOCAL | CREAD);// Дозвіл прийому, ігнорування ліній модему

    // Сирий режим вводу (Raw input): відключення трансляції спецсимволів
    tty.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
    tty.c_iflag &= ~(IXON | IXOFF | IXANY); // Без програмного керування XON/XOFF
    tty.c_iflag &= ~(IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL);

    // Сирий режим виводу (Raw output)
    tty.c_oflag &= ~OPOST;

    // Тайм-аути читання: блокування до приходу хоча б 1 байта або тайм-аут 100 мс
    tty.c_cc[VMIN] = 0;   // Мінімальна кількість байтів для завершення read()
    tty.c_cc[VTIME] = 1;  // Тайм-аут читання в децисекундах (1 = 100 мс)

    // Застосування налаштувань негайно
    if (tcsetattr(fd, TCSANOW, &tty) != 0) {
        perror("Помилка застосування налаштувань termios");
        close(fd);
        return -1;
    }

    // Очищення черг вхідного та вихідного буферів
    tcflush(fd, TCIOFLUSH);
    return fd;
}

// Повнодуплексна відправка блоку даних у лінію RS-422
ssize_t rs422_write_all(int fd, const uint8_t *data, size_t len) {
    size_t total_written = 0;
    while (total_written < len) {
        ssize_t written = write(fd, data + total_written, len - total_written);
        if (written < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        total_written += (size_t)written;
    }
    return (ssize_t)total_written;
}
