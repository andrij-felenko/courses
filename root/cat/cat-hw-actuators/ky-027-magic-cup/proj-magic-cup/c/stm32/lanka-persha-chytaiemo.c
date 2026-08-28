#include "stm32f4xx_hal.h"
#include <stdbool.h>

// Стан згасання брязкоту для однієї лінії вимикача.
typedef struct {
    GPIO_TypeDef *port;      // порт, у якому сидить ніжка S
    uint16_t      pin;       // сама ніжка (GPIO_PIN_x)
    bool          stable;    // чистий, уже прийнятий рівень
    bool          last_raw;  // що прочитали минулого разу (для лову зміни)
    uint32_t      changed_at;// коли сире читання востаннє змінилось (HAL_GetTick)
} Debounced;

#define DEBOUNCE_MS 25u      // скільки треба протриматись, щоб повірити

// Ніжку вже налаштовано входом БЕЗ підтяжки в MX_GPIO_Init() — підтяжка на платі.
void DebounceBegin(Debounced *d, GPIO_TypeDef *port, uint16_t pin) {
    d->port = port;
    d->pin  = pin;
    d->stable = (HAL_GPIO_ReadPin(port, pin) == GPIO_PIN_SET);  // що зараз на ніжці
    d->last_raw = d->stable;
    d->changed_at = HAL_GetTick();
}

// Оновити згасання; повертає ЧИСТИЙ рівень ніжки (уже без брязкоту).
bool DebounceRead(Debounced *d) {
    bool raw = (HAL_GPIO_ReadPin(d->port, d->pin) == GPIO_PIN_SET);
    if (raw != d->last_raw) {          // сире читання щойно змінилось —
        d->last_raw = raw;             //   запам'ятали нове й засікли час,
        d->changed_at = HAL_GetTick(); //   але ПОКИ не віримо йому
    }
    // Якщо нове читання протрималось усю витримку — приймаємо його за правду.
    if (raw != d->stable && (HAL_GetTick() - d->changed_at) >= DEBOUNCE_MS) {
        d->stable = raw;
    }
    return d->stable;
}
