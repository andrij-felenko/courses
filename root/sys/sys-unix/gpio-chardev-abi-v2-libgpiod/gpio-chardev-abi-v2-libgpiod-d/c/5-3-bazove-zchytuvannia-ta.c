#include <gpiod.h>
#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    struct gpiod_chip *chip;
    struct gpiod_line_config *line_cfg;
    struct gpiod_line_settings *settings_in, *settings_out;
    struct gpiod_request_config *req_cfg;
    struct gpiod_line_request *request;
    enum gpiod_line_value val;

    /* Відкриття контролера GPIO */
    chip = gpiod_chip_open("/dev/gpiochip1");
    if (!chip) {
        perror("Не вдалося відкрити /dev/gpiochip1");
        return EXIT_FAILURE;
    }

    /* Створення об'єктів конфігурації */
    line_cfg = gpiod_line_config_new();
    req_cfg = gpiod_request_config_new();
    settings_in = gpiod_line_settings_new();
    settings_out = gpiod_line_settings_new();

    if (!line_cfg || !req_cfg || !settings_in || !settings_out) {
        fprintf(stderr, "Помилка виділення пам'яті під конфігурацію\n");
        goto out_free;
    }

    /* Налаштування вхідної лінії (Кнопка, offset 12) з PULL_UP та Debounce */
    gpiod_line_settings_set_direction(settings_in, GPIOD_LINE_DIRECTION_INPUT);
    gpiod_line_settings_set_bias(settings_in, GPIOD_LINE_BIAS_PULL_UP);
    gpiod_line_settings_set_debounce_period_us(settings_in, 15000); // 15 мс

    /* Налаштування вихідної лінії (Світлодіод, offset 16) */
    gpiod_line_settings_set_direction(settings_out, GPIOD_LINE_DIRECTION_OUTPUT);
    gpiod_line_settings_set_output_value(settings_out, GPIOD_LINE_VALUE_INACTIVE);

    /* Додавання налаштувань у конфігуратор ліній */
    gpiod_line_config_add_line_settings(line_cfg, (const unsigned int[]){12}, 1, settings_in);
    gpiod_line_config_add_line_settings(line_cfg, (const unsigned int[]){16}, 1, settings_out);

    gpiod_request_config_set_consumer(req_cfg, "button_led_app");

    /* Атомарний запит ліній у ядра */
    request = gpiod_chip_request_lines(chip, req_cfg, line_cfg);
    if (!request) {
        perror("Не вдалося отримати доступ до ліній GPIO");
        goto out_free;
    }

    /* Читання значення кнопки */
    val = gpiod_line_request_get_value(request, 12);
    printf("Стан кнопки (офсет 12): %s\n",
           val == GPIOD_LINE_VALUE_ACTIVE ? "НАТИСНУТО (ACTIVE)" : "ВІДПУЩЕНО");

    /* Перемикання світлодіода у стан ACTIVE */
    gpiod_line_request_set_value(request, 16, GPIOD_LINE_VALUE_ACTIVE);

    /* Звільнення запиту */
    gpiod_line_request_release(request);

out_free:
    gpiod_line_settings_free(settings_in);
    gpiod_line_settings_free(settings_out);
    gpiod_line_config_free(line_cfg);
    gpiod_request_config_free(req_cfg);
    gpiod_chip_close(chip);
    return EXIT_SUCCESS;
}
