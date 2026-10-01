/**
 * main.c :: Утиліта керування лініями DTR та RTS мосту CH340 у POSIX Linux
 * 
 * Програма демонструє відкриття послідовного порту /dev/ttyUSB0, конфігурацію 
 * термінала termios та прямого керування станами сигналів DTR i RTS за допомогою 
 * системних викликів ioctl() з прапорцями TIOCMBIS та TIOCMBIC.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <termios.h>
#include <sys/ioctl.h>

/**
 * Налаштовує сирий режим (raw mode) та швидкість обміну послідовного порту.
 */
static int configure_serial_port(int fd, speed_t baud_rate) {
    struct termios options;

    if (tcgetattr(fd, &options) < 0) {
        perror("Помилка зчитування атрибутів termios (tcgetattr)");
        return -1;
    }

    /* Встановлення швидкості прийому та передачі */
    cfsetispeed(&options, baud_rate);
    cfsetospeed(&options, baud_rate);

    /* Конфігурація сирого режиму (Raw mode): 8 біт даних, без парності, 1 стоп-біт */
    options.c_cflag &= ~PARENB;        /* Без біта парності */
    options.c_cflag &= ~CSTOPB;        /* 1 стоп-біт */
    options.c_cflag &= ~CSIZE;
    options.c_cflag |= CS8;            /* 8 бітів даних */
    options.c_cflag &= ~CRTSCTS;       /* Вимкнення апаратного керування потоком */
    options.c_cflag |= CREAD | CLOCAL; /* Увімкнути приймач, ігнорувати лінії модему */

    /* Вимкнення канонічного режиму та луна-сигналів */
    options.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
    options.c_iflag &= ~(IXON | IXOFF | IXANY | IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL);
    options.c_oflag &= ~OPOST;

    /* Налаштування таймаутів: неблокуюче зчитування */
    options.c_cc[VMIN] = 0;
    options.c_cc[VTIME] = 10; /* Таймаут 1 секунда (10 * 0.1 с) */

    if (tcsetattr(fd, TCSANOW, &options) < 0) {
        perror("Помилка застосування конфігурації termios (tcsetattr)");
        return -1;
    }

    return 0;
}

/**
 * Встановлює або скидає високий/низький рівень на лініях DTR та RTS через ioctl.
 */
static int set_line_state(int fd, int dtr, int rts) {
    int flags = 0;

    /* Отримання поточних прапорців модемних ліній */
    if (ioctl(fd, TIOCMGET, &flags) < 0) {
        perror("Помилка зчитування стану ліній (TIOCMGET)");
        return -1;
    }

    /* Керування лінією DTR */
    if (dtr) {
        int bit = TIOCM_DTR;
        if (ioctl(fd, TIOCMBIS, &bit) < 0) {
            perror("Помилка встановлення DTR (TIOCMBIS)");
            return -1;
        }
    } else {
        int bit = TIOCM_DTR;
        if (ioctl(fd, TIOCMBIC, &bit) < 0) {
            perror("Помилка скидання DTR (TIOCMBIC)");
            return -1;
        }
    }

    /* Керування лінією RTS */
    if (rts) {
        int bit = TIOCM_RTS;
        if (ioctl(fd, TIOCMBIS, &bit) < 0) {
            perror("Помилка встановлення RTS (TIOCMBIS)");
            return -1;
        }
    } else {
        int bit = TIOCM_RTS;
        if (ioctl(fd, TIOCMBIC, &bit) < 0) {
            perror("Помилка скидання RTS (TIOCMBIC)");
            return -1;
        }
    }

    return 0;
}

/**
 * Демонструє послідовність сигналів автоскидання (Auto-reset pulse)
 * для переведення мікроконтролерів серії ESP8266/ESP32 у режим Bootloader.
 */
static void generate_esp_auto_reset(int fd) {
    printf("--- Генерація імпульсу автоскидання ESP8266/ESP32 ---\n");

    /* Крок 1: Встановлення початкового стану (DTR=0, RTS=0) -> EN=1, IO0=1 */
    printf("[1/4] Початковий стан: DTR=0, RTS=0 (Нормальний режим)...\n");
    set_line_state(fd, 0, 0);
    usleep(100000); /* Затримка 100 мс */

    /* Крок 2: Активація режиму програмування (DTR=0, RTS=1) -> EN=1, IO0=0 */
    printf("[2/4] Режим завантажника: DTR=0, RTS=1 (IO0 заземлено)...\n");
    set_line_state(fd, 0, 1);
    usleep(100000);

    /* Крок 3: Імпульс скидання ядра (DTR=1, RTS=0) -> EN=0, IO0=1 */
    printf("[3/4] Апаратне скидання: DTR=1, RTS=0 (EN притиснуто до GND)...\n");
    set_line_state(fd, 1, 0);
    usleep(100000);

    /* Крок 4: Відновлення роботи (DTR=0, RTS=0) -> EN=1, IO0=1 */
    printf("[4/4] Завершення скидання: DTR=0, RTS=0 (Запуск прошивки)...\n");
    set_line_state(fd, 0, 0);
    usleep(100000);

    printf("Послідовність сигналів скидання успішно сформована.\n");
}

int main(int argc, char *argv[]) {
    const char *device_path = "/dev/ttyUSB0";

    if (argc > 1) {
        device_path = argv[1];
    }

    printf("Відкриття пристрою послідовного порту CH340: %s\n", device_path);

    /* Відкриття порту у неблокуючому режимі без присвоєння керівного термінала */
    int fd = open(device_path, O_RDWR | O_NOCTTY | O_NDELAY);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s\n", device_path, strerror(errno));
        return EXIT_FAILURE;
    }

    /* Скидання прапорця неблокуючого вводу-виводу після відкриття */
    fcntl(fd, F_SETFL, 0);

    /* Конфігурація параметрів порту (115200 бод, 8N1) */
    if (configure_serial_port(fd, B115200) < 0) {
        fprintf(stderr, "Не вдалося налаштувати термінал termios\n");
        close(fd);
        return EXIT_FAILURE;
    }

    printf("Порт %s успішно відкрито та налаштовано на швидкість 115200 біт/с.\n", device_path);

    /* Генерація тестової послідовності сигналів */
    generate_esp_auto_reset(fd);

    /* Очищення та відновлення початкового стану ліній */
    set_line_state(fd, 0, 0);

    close(fd);
    printf("Файловий дескриптор закрито. Завершення роботи.\n");
    return EXIT_SUCCESS;
}
