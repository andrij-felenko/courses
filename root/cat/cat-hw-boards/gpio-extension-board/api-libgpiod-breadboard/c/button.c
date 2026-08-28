// button.c — читаємо кнопку на GPIO27 із внутрішньою підтяжкою до плюса
// збірка:  gcc button.c -o button -lgpiod
#include <gpiod.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>

#define CHIP_PATH  "/dev/gpiochip0"
#define BTN_LINE   27

int main(void)
{
    struct gpiod_chip *chip = gpiod_chip_open(CHIP_PATH);
    if (!chip) { perror("chip"); return 1; }

    struct gpiod_line_settings *st = gpiod_line_settings_new();
    gpiod_line_settings_set_direction(st, GPIOD_LINE_DIRECTION_INPUT);
    // внутрішня підтяжка до 3.3 В: у спокої лінія читається як ACTIVE
    gpiod_line_settings_set_bias(st, GPIOD_LINE_BIAS_PULL_UP);

    struct gpiod_line_config *lc = gpiod_line_config_new();
    unsigned int off = BTN_LINE;
    gpiod_line_config_add_line_settings(lc, &off, 1, st);

    struct gpiod_request_config *rc = gpiod_request_config_new();
    gpiod_request_config_set_consumer(rc, "button");

    struct gpiod_line_request *req = gpiod_chip_request_lines(chip, rc, lc);
    if (!req) { perror("request"); return 1; }

    printf("натисніть кнопку (Ctrl+C — вихід)\n");
    int prev = -1;
    for (;;) {
        enum gpiod_line_value v = gpiod_line_request_get_value(req, BTN_LINE);
        // ПІДТЯЖКА ДО ПЛЮСА: ACTIVE (3.3 В) — відпущено, INACTIVE (0) — натиснуто
        int pressed = (v == GPIOD_LINE_VALUE_INACTIVE);
        if (pressed != prev) {              // друкуємо лише коли стан змінився
            printf("%s\n", pressed ? "натиснуто" : "відпущено");
            prev = pressed;
        }
        usleep(20000);                      // 20 мс — заразом гасить дребезг
    }
    // сюди не доходимо; у реальному коді — release + close
}
