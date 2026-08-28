// blink.c — блимаємо світлодіодом на GPIO 17 через libgpiod v2
// збірка:  gcc blink.c -o blink -lgpiod
#include <gpiod.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>      // usleep
#include <string.h>
#include <errno.h>

#define CHIP_PATH  "/dev/gpiochip0"   // гребінка на Pi 5 у свіжому ядрі
#define LED_LINE   17                 // BCM-зсув, а НЕ фізичний штирок

int main(void)
{
    struct gpiod_chip *chip = gpiod_chip_open(CHIP_PATH);
    if (!chip) {
        fprintf(stderr, "не відкрив %s: %s\n", CHIP_PATH, strerror(errno));
        return 1;
    }

    // 1. Налаштування лінії: напрямок — вихід, старт — низький рівень
    struct gpiod_line_settings *settings = gpiod_line_settings_new();
    gpiod_line_settings_set_direction(settings, GPIOD_LINE_DIRECTION_OUTPUT);
    gpiod_line_settings_set_output_value(settings, GPIOD_LINE_VALUE_INACTIVE);

    // 2. Конфіг ліній: прив'язуємо ці налаштування до зсуву 17
    struct gpiod_line_config *lcfg = gpiod_line_config_new();
    unsigned int offset = LED_LINE;
    gpiod_line_config_add_line_settings(lcfg, &offset, 1, settings);

    // 3. Конфіг запиту: підпис — щоб інші бачили, хто зайняв лінію
    struct gpiod_request_config *rcfg = gpiod_request_config_new();
    gpiod_request_config_set_consumer(rcfg, "blink");

    // 4. Власне запит лінії в ядра
    struct gpiod_line_request *req =
        gpiod_chip_request_lines(chip, rcfg, lcfg);
    if (!req) {
        fprintf(stderr, "не вдалось узяти лінію 17: %s\n", strerror(errno));
        return 1;
    }

    // 5. Блимаємо: 1 → горить, 0 → згас, пауза 500 мс
    for (int i = 0; i < 20; i++) {
        gpiod_line_request_set_value(req, LED_LINE, GPIOD_LINE_VALUE_ACTIVE);
        usleep(500000);
        gpiod_line_request_set_value(req, LED_LINE, GPIOD_LINE_VALUE_INACTIVE);
        usleep(500000);
    }

    // 6. Прибираємо за собою — звільняємо лінію й закриваємо чип
    gpiod_line_request_release(req);
    gpiod_line_settings_free(settings);
    gpiod_line_config_free(lcfg);
    gpiod_request_config_free(rcfg);
    gpiod_chip_close(chip);
    return 0;
}
