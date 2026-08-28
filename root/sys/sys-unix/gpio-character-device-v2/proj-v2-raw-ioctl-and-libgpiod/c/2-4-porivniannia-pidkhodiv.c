/* Приклад використання libgpiod v2 мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <gpiod.h>

int main(void) {
    int rc = EXIT_SUCCESS;
    struct gpiod_chip *chip = gpiod_chip_open("/dev/gpiochip0");
    if (!chip) {
        perror("Не вдалося відкрити чип через libgpiod");
        return EXIT_FAILURE;
    }

    /* Створення налаштувань для вихідної лінії */
    struct gpiod_line_settings *out_settings = gpiod_line_settings_new();
    gpiod_line_settings_set_direction(out_settings, GPIOD_LINE_DIRECTION_OUTPUT);
    gpiod_line_settings_set_bias(out_settings, GPIOD_LINE_BIAS_PULL_UP);

    /* Створення налаштувань для вхідної лінії з моніторингом подій */
    struct gpiod_line_settings *in_settings = gpiod_line_settings_new();
    gpiod_line_settings_set_direction(in_settings, GPIOD_LINE_DIRECTION_INPUT);
    gpiod_line_settings_set_edge_detection(in_settings, GPIOD_LINE_EDGE_BOTH);
    gpiod_line_settings_set_debounce_period_us(in_settings, 5000);

    /* Збирання загальної конфігурації ліній */
    struct gpiod_line_config *line_cfg = gpiod_line_config_new();
    unsigned int out_offsets[] = {17};
    unsigned int in_offsets[] = {27};

    gpiod_line_config_add_line_settings(line_cfg, out_offsets, 1, out_settings);
    gpiod_line_config_add_line_settings(line_cfg, in_offsets, 1, in_settings);

    /* Конфігурація запиту */
    struct gpiod_request_config *req_cfg = gpiod_request_config_new();
    gpiod_request_config_set_consumer(req_cfg, "libgpiod-c-demo");

    /* Виконання запиту на захоплення ліній */
    struct gpiod_line_request *request = gpiod_chip_request_lines(chip, req_cfg, line_cfg);
    if (!request) {
        perror("Помилка захоплення ліній через gpiod");
        rc = EXIT_FAILURE;
        goto cleanup;
    }

    printf("Лінії успішно захоплено через libgpiod v2! Встановлюємо HIGH на лінії 17...\n");
    gpiod_line_request_set_value(request, 17, GPIOD_LINE_VALUE_ACTIVE);

    /* Буфер для зчитування подій */
    struct gpiod_edge_event_buffer *event_buf = gpiod_edge_event_buffer_new(16);
    printf("Очікування події переривання на лінії 27...\n");

    int ret = gpiod_line_request_read_edge_events(request, event_buf, 16);
    if (ret > 0) {
        struct gpiod_edge_event *event = gpiod_edge_event_buffer_get_event(event_buf, 0);
        enum gpiod_edge_event_type type = gpiod_edge_event_get_event_type(event);
        uint64_t ts = gpiod_edge_event_get_timestamp_ns(event);

        printf("Отримано подію від libgpiod! Timestamp: %llu нс, Тип: %s\n",
               (unsigned long long)ts,
               (type == GPIOD_EDGE_EVENT_RISING_EDGE) ? "RISING" : "FALLING");
    }

    gpiod_edge_event_buffer_free(event_buf);
    gpiod_line_request_release(request);

cleanup:
    gpiod_request_config_free(req_cfg);
    gpiod_line_config_free(line_cfg);
    gpiod_line_settings_free(out_settings);
    gpiod_line_settings_free(in_settings);
    gpiod_chip_close(chip);
    return rc;
}
