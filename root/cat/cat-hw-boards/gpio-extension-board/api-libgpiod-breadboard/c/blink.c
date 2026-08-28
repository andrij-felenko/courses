// blink.c — блимаємо світлодіодом на GPIO17, виведеному платою на макетку
// збірка:  gcc blink.c -o blink -lgpiod
#include <gpiod.h>
#include <stdio.h>
#include <unistd.h>      // usleep
#include <string.h>
#include <errno.h>

#define CHIP_PATH  "/dev/gpiochip0"   // гребінка Pi у свіжому ядрі
#define LED_LINE   17                 // BCM-ім'я, надруковане на платі біля штиря

int main(void)
{
    struct gpiod_chip *chip = gpiod_chip_open(CHIP_PATH);
    if (!chip) { fprintf(stderr, "чип: %s\n", strerror(errno)); return 1; }

    // напрямок — вихід, початковий рівень — низький (світлодіод згаслий)
    struct gpiod_line_settings *st = gpiod_line_settings_new();
    gpiod_line_settings_set_direction(st, GPIOD_LINE_DIRECTION_OUTPUT);
    gpiod_line_settings_set_output_value(st, GPIOD_LINE_VALUE_INACTIVE);

    // прив'язуємо ці налаштування до зсуву 17
    struct gpiod_line_config *lc = gpiod_line_config_new();
    unsigned int off = LED_LINE;
    gpiod_line_config_add_line_settings(lc, &off, 1, st);

    // підпис споживача — щоб gpioinfo показував, хто зайняв лінію
    struct gpiod_request_config *rc = gpiod_request_config_new();
    gpiod_request_config_set_consumer(rc, "blink");

    struct gpiod_line_request *req = gpiod_chip_request_lines(chip, rc, lc);
    if (!req) { fprintf(stderr, "запит лінії 17: %s\n", strerror(errno)); return 1; }

    for (int i = 0; i < 20; i++) {
        gpiod_line_request_set_value(req, LED_LINE, GPIOD_LINE_VALUE_ACTIVE);
        usleep(500000);                              // горить 0.5 с
        gpiod_line_request_set_value(req, LED_LINE, GPIOD_LINE_VALUE_INACTIVE);
        usleep(500000);                              // згас 0.5 с
    }

    gpiod_line_request_release(req);                 // прибираємо за собою
    gpiod_line_settings_free(st);
    gpiod_line_config_free(lc);
    gpiod_request_config_free(rc);
    gpiod_chip_close(chip);
    return 0;
}
