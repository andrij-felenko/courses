// button.c — читаємо кнопку на GPIO27 з внутрішньою підтяжкою до плюса.
// Кнопка: один контакт на GPIO27, другий на GND. Натиснуто = 0, відпущено = 1.
// Збірка:  gcc button.c -o button -lgpiod
#include <gpiod.h>
#include <stdio.h>
#include <unistd.h>

#define BTN_OFFSET   27        // GPIO27 = фізичний штир 13

int main(void) {
    struct gpiod_chip *chip = open_header_chip();   // з blink.c
    if (!chip) { fprintf(stderr, "немає контролера гребінки\n"); return 1; }

    // Вхід + внутрішня підтяжка до плюса (PULL_UP).
    struct gpiod_line_settings *settings = gpiod_line_settings_new();
    gpiod_line_settings_set_direction(settings, GPIOD_LINE_DIRECTION_INPUT);
    gpiod_line_settings_set_bias(settings, GPIOD_LINE_BIAS_PULL_UP);

    struct gpiod_line_config *line_cfg = gpiod_line_config_new();
    unsigned int offset = BTN_OFFSET;
    gpiod_line_config_add_line_settings(line_cfg, &offset, 1, settings);

    struct gpiod_request_config *req_cfg = gpiod_request_config_new();
    gpiod_request_config_set_consumer(req_cfg, "button");

    struct gpiod_line_request *request =
        gpiod_chip_request_lines(chip, req_cfg, line_cfg);
    if (!request) { fprintf(stderr, "не вдалося запросити GPIO%d\n", BTN_OFFSET); return 1; }

    // Опитуємо кнопку й друкуємо лише ЗМІНИ стану (щоб не залити термінал).
    enum gpiod_line_value prev = GPIOD_LINE_VALUE_ACTIVE;   // відпущено на старті
    for (;;) {
        enum gpiod_line_value v = gpiod_line_request_get_value(request, offset);
        if (v != prev) {
            // ACTIVE = високий = 3.3 В = відпущено; INACTIVE = 0 = натиснуто.
            printf("%s\n", (v == GPIOD_LINE_VALUE_INACTIVE) ? "натиснуто" : "відпущено");
            prev = v;
        }
        usleep(5000);   // опитувати раз на 5 мс
    }

    gpiod_line_request_release(request);
    gpiod_chip_close(chip);   // (до сюди не дійде — цикл вічний; для повноти)
    return 0;
}
