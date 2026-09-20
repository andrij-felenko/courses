#include <stdint.h>
#include <stdbool.h>

// Коди статусів повернення драйвера
typedef enum {
    THUMBWHEEL_OK                  =  0,
    THUMBWHEEL_ERR_INVALID_BCD     = -1,
    THUMBWHEEL_ERR_BUSY            = -2
} thumbwheel_status_t;

// Структура конфігурації апаратних пінів
typedef struct {
    uint8_t pin_pl;          // Пін паралельного завантаження PL
    uint8_t pin_clk;         // Пін тактування CLK
    uint8_t pin_data;        // Пін послідовних даних DATA (Q7)
    uint8_t decades_count;   // Кількість барабанних розрядів (наприклад, 4)
    bool active_low_logic;   // true, якщо виходи інверсні
} thumbwheel_config_t;

// Внутрішній стан драйвера
typedef struct {
    thumbwheel_config_t config;
    uint16_t raw_latch;      // Сирий зчитаний кадр бітів
    uint8_t  nibbles[4];     // Відфільтровані BCD-тетради
    uint8_t  debounce_cnt[4];// Лічильники часової стабілізації
    uint8_t  prev_nibbles[4]; // Попередні заміри тетрад
    uint16_t validated_value;// Фінальне підтверджене ціле число
} thumbwheel_driver_t;

// Сигнатура функції ініціалізації
thumbwheel_status_t thumbwheel_init(thumbwheel_driver_t *drv, const thumbwheel_config_t *cfg);
