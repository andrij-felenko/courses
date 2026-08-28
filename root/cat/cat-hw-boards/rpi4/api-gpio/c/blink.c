// blink.c — блимаємо світлодіодом на GPIO17. libgpiod v2.
// Збірка:  gcc blink.c -o blink -lgpiod
#include <gpiod.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>     // usleep()
#include <dirent.h>
#include <string.h>

#define LED_OFFSET   17        // GPIO17 = фізичний штир 11 (номер BCM, не штир!)

// Знайти символьний пристрій контролера гребінки за міткою pinctrl-*.
// Повертає відкритий chip або NULL. Так код не залежить від номера gpiochipN.
static struct gpiod_chip *open_header_chip(void) {
    DIR *d = opendir("/dev");
    if (!d) return NULL;
    struct dirent *e;
    struct gpiod_chip *chip = NULL;
    while ((e = readdir(d)) != NULL) {
        if (strncmp(e->d_name, "gpiochip", 8) != 0) continue;
        char path[64];
        snprintf(path, sizeof path, "/dev/%s", e->d_name);
        struct gpiod_chip *c = gpiod_chip_open(path);
        if (!c) continue;
        struct gpiod_chip_info *info = gpiod_chip_get_info(c);
        if (info) {
            const char *label = gpiod_chip_info_get_label(info);
            // Контролер гребінки має мітку pinctrl-* (bcm2711 на Pi4, rp1 на Pi5).
            if (label && strncmp(label, "pinctrl", 7) == 0) {
                gpiod_chip_info_free(info);
                chip = c;
                break;
            }
            gpiod_chip_info_free(info);
        }
        gpiod_chip_close(c);
    }
    closedir(d);
    return chip;
}

int main(void) {
    struct gpiod_chip *chip = open_header_chip();
    if (!chip) {
        fprintf(stderr, "не знайшов контролер гребінки (pinctrl-*)\n");
        return 1;
    }

    // 1. Налаштування лінії: напрям — вихід, початкове значення — 0 (згашено).
    struct gpiod_line_settings *settings = gpiod_line_settings_new();
    gpiod_line_settings_set_direction(settings, GPIOD_LINE_DIRECTION_OUTPUT);
    gpiod_line_settings_set_output_value(settings, GPIOD_LINE_VALUE_INACTIVE);

    // 2. Конфіг: прив'язати ці налаштування до нашого зсуву (offset = 17).
    struct gpiod_line_config *line_cfg = gpiod_line_config_new();
    unsigned int offset = LED_OFFSET;
    gpiod_line_config_add_line_settings(line_cfg, &offset, 1, settings);

    // 3. Запит на володіння: лишаємо мітку-ім'я "blink" (її покаже gpioinfo).
    struct gpiod_request_config *req_cfg = gpiod_request_config_new();
    gpiod_request_config_set_consumer(req_cfg, "blink");

    struct gpiod_line_request *request =
        gpiod_chip_request_lines(chip, req_cfg, line_cfg);
    if (!request) {
        fprintf(stderr, "не вдалося запросити GPIO%d (зайнято?)\n", LED_OFFSET);
        return 1;
    }

    // 4. Блимаємо: 10 разів, по 0.5 с у кожному стані.
    for (int i = 0; i < 10; i++) {
        gpiod_line_request_set_value(request, offset, GPIOD_LINE_VALUE_ACTIVE);
        usleep(500000);   // 500 000 мкс = 0.5 с
        gpiod_line_request_set_value(request, offset, GPIOD_LINE_VALUE_INACTIVE);
        usleep(500000);
    }

    // 5. Прибираємо за собою (ядро зробило б це й само при виході).
    gpiod_line_request_release(request);
    gpiod_request_config_free(req_cfg);
    gpiod_line_config_free(line_cfg);
    gpiod_line_settings_free(settings);
    gpiod_chip_close(chip);
    return 0;
}
