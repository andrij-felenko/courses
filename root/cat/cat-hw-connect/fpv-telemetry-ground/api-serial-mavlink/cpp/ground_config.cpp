// ground_config.cpp — командний режим і S-регістри через сирий UART.
// Використовує open_serial() з ground_read.cpp (termios, 8N1, B57600).
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <unistd.h>
#include <termios.h>

int open_serial(const char *dev, speed_t baud);   // з ground_read.cpp

static void sleep_ms(int ms) { usleep(ms * 1000); }

// Прочитати все, що є на лінії, у buf; повертає кількість байтів.
static int drain(int fd, char *buf, int cap, int settle_ms) {
    sleep_ms(settle_ms);
    ssize_t n = read(fd, buf, cap - 1);
    if (n < 0) n = 0;
    buf[n] = '\0';
    return (int)n;
}

// Надіслати AT-команду з CRLF і повернути відповідь у buf.
static void at(int fd, const char *cmd, char *buf, int cap, int wait_ms) {
    tcflush(fd, TCIFLUSH);                 // викинути старе з вхідного буфера
    dprintf(fd, "%s\r\n", cmd);            // сама команда
    drain(fd, buf, cap, wait_ms);
}

int main() {
    int fd = open_serial("/dev/ttyUSB0", B57600);
    if (fd < 0) return 1;

    char buf[512];

    // УВІЙТИ В КОМАНДНИЙ РЕЖИМ: тиша 1 с — "+++" (без CRLF!) — тиша 1 с.
    sleep_ms(1100);                        // 1 с тиші ДО
    tcflush(fd, TCIFLUSH);
    write(fd, "+++", 3);                   // саме три плюси, БЕЗ переводу рядка
    sleep_ms(1100);                        // 1 с тиші ПІСЛЯ
    drain(fd, buf, sizeof buf, 50);
    if (!strstr(buf, "OK")) {
        printf("не ввійшов у командний режим (не той порт/швидкість?)\n");
        return 1;
    }
    printf("у командному режимі\n");

    at(fd, "ATI5", buf, sizeof buf, 300);          // усі параметри
    printf("%s", buf);
    at(fd, "ATS3?", buf, sizeof buf, 300);          // прочитати NetID
    printf("NetID зараз: %s\n", buf);

    // ЗМІНИТИ NetID + зберегти + перезавантажити — три кроки, жоден не пропустити:
    at(fd, "ATS3=42", buf, sizeof buf, 300);        // 1) у живу пам'ять
    at(fd, "AT&W",   buf, sizeof buf, 300);         // 2) у EEPROM — інакше відкотиться
    at(fd, "ATZ",    buf, sizeof buf, 1000);        // 3) перезавантаження
    printf("NetID записано в EEPROM і модуль перезавантажено\n");

    close(fd);
    return 0;
}
