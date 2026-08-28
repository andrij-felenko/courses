/* main.c — Читання датчика TMP102 (hwmon) та керування LED утилітою C */
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <gpiod.h>

#define TEMP_HWMON_PATH "/sys/class/hwmon/hwmon0/temp1_input"
#define GPIO_CHIP "/dev/gpiochip0"
#define FAULT_LED_LINE 26

int read_temperature_milli_celsius(long *temp_mc) {
    int fd = open(TEMP_HWMON_PATH, O_RDONLY);
    if (fd < 0) {
        perror("Не вдалося відкрити sysfs вузол температури");
        return -1;
    }

    char buf[32];
    ssize_t bytes = read(fd, buf, sizeof(buf) - 1);
    close(fd);

    if (bytes <= 0) {
        return -1;
    }

    buf[bytes] = '\0';
    *temp_mc = strtol(buf, NULL, 10);
    return 0;
}

int main(void) {
    long temp_mc = 0;
    if (read_temperature_milli_celsius(&temp_mc) != 0) {
        fprintf(stderr, "Помилка зчитування даних із TMP102\n");
        return EXIT_FAILURE;
    }

    double temp_c = temp_mc / 1000.0;
    printf("Поточна температура плати: %.2f °C\n", temp_c);

    /* Якщо температура перевищує поріг 60 °C, запалюємо аварійний світлодіод */
    struct gpiod_chip *chip = gpiod_chip_open(GPIO_CHIP);
    if (!chip) {
        perror("Помилка відкриття gpiochip");
        return EXIT_FAILURE;
    }

    struct gpiod_line *led_line = gpiod_chip_get_line(chip, FAULT_LED_LINE);
    if (!led_line) {
        perror("Помилка отримання лінії GPIO");
        gpiod_chip_close(chip);
        return EXIT_FAILURE;
    }

    if (gpiod_line_request_output(led_line, "carrier-monitor", 0) < 0) {
        perror("Не вдалося налаштувати лінію LED на вихід");
        gpiod_chip_close(chip);
        return EXIT_FAILURE;
    }

    if (temp_c > 60.0) {
        printf("УВАГА: Перегрів! Активація аварійного світлодіода (GPIO%d)\n", FAULT_LED_LINE);
        gpiod_line_set_value(led_line, 1);
    } else {
        printf("Температурний режим у нормі.\n");
        gpiod_line_set_value(led_line, 0);
    }

    gpiod_line_release(led_line);
    gpiod_chip_close(chip);
    return EXIT_SUCCESS;
}
