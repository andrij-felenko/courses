// button.c — читаємо кнопку на GPIO 27 із внутрішньою підтяжкою до плюса
// збірка:  gcc button.c -o button -lgpiod
#include <gpiod.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>

#define CHIP_PATH  "/dev/gpiochip0"
#define BTN_LINE   27

int main(void)
{
    struct gpiod_chip *chip = gpiod_chip_open(CHIP_PATH);
    if (!chip) { perror("gpiod_chip_open"); return 1; }

    struct gpiod_line_settings *settings = gpiod_line_settings_new();
    gpiod_line_settings_set_direction(settings, GPIOD_LINE_DIRECTION_INPUT);
    // внутрішня підтяжка до 3.3 В: у спокої лінія читається як ACTIVE
    gpiod_line_settings_set_bias(settings, GPIOD_LINE_BIAS_PULL_UP);

    struct gpiod_line_config *lcfg = gpiod_line_config_new();
    unsigned int offset = BTN_LINE;
    gpiod_line_config_add_line_settings(lcfg, &offset, 1, settings);

    struct gpiod_request_config *rcfg = gpiod_request_config_new();
    gpiod_request_config_set_consumer(rcfg, "button");

    struct gpiod_line_request *req =
        gpiod_chip_request_lines(chip, rcfg, lcfg);
    if (!req) { perror("request_lines"); return 1; }

    printf("натисніть кнопку (Ctrl+C — вихід)\n");
    int prev = -1;
    for (;;) {
        enum gpiod_line_value v = gpiod_line_request_get_value(req, BTN_LINE);
        // ПІДТЯЖКА ДО ПЛЮСА: ACTIVE (=3.3 В) — відпущено, INACTIVE (=0) — натиснуто
        int pressed = (v == GPIOD_LINE_VALUE_INACTIVE);
        if (pressed != prev) {             // друкуємо лише коли стан змінився
            printf("%s\n", pressed ? "натиснуто" : "відпущено");
            prev = pressed;
        }
        usleep(20000);                     // 20 мс — заразом гасить дребезг
    }
    // сюди не доходимо, але в реальному коді — release + close
}
