#include "driver/gpio.h"
#include "esp_timer.h"

// Стан згасання брязкоту для однієї лінії вимикача.
typedef struct {
    gpio_num_t pin;          // до якого GPIO під'єднано S
    bool       stable;       // чистий, уже прийнятий рівень
    bool       last_raw;     // що прочитали минулого разу (для лову зміни)
    int64_t    changed_us;   // коли сире читання востаннє змінилось (мкс)
} debounced_t;

#define DEBOUNCE_US 25000    // 25 мс — скільки треба протриматись, щоб повірити

void debounce_begin(debounced_t *d, gpio_num_t pin) {
    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << pin,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,     // підтяжка вже на платі
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&cfg));
    d->pin = pin;
    d->stable = gpio_get_level(pin);   // початковий стан — те, що зараз на ніжці
    d->last_raw = d->stable;
    d->changed_us = esp_timer_get_time();
}

// Оновити згасання; повертає ЧИСТИЙ рівень ніжки (уже без брязкоту).
bool debounce_read(debounced_t *d) {
    bool raw = gpio_get_level(d->pin);
    if (raw != d->last_raw) {              // сире читання щойно змінилось —
        d->last_raw = raw;                 //   запам'ятали нове й засікли час,
        d->changed_us = esp_timer_get_time();  //   але ПОКИ не віримо йому
    }
    // Якщо нове читання протрималось усю витримку — приймаємо його за правду.
    if (raw != d->stable && esp_timer_get_time() - d->changed_us >= DEBOUNCE_US) {
        d->stable = raw;
    }
    return d->stable;
}
