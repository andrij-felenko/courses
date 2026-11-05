#include <stdint.h>
#include <stdbool.h>

#define DIGIMATIC_NIBBLES     13
#define DIGIMATIC_TOTAL_BITS  52
#define PREAMBLE_EXPECTED     0xFFFFU

typedef enum {
    DIGIMATIC_UNIT_MM   = 0,
    DIGIMATIC_UNIT_INCH = 1
} digimatic_unit_t;

typedef enum {
    DIGIMATIC_OK = 0,
    DIGIMATIC_ERR_BUSY,
    DIGIMATIC_ERR_PREAMBLE,
    DIGIMATIC_ERR_TIMEOUT,
    DIGIMATIC_ERR_BCD
} digimatic_status_t;

typedef struct {
    int32_t value_um;       /* Значення у мікрометрах (фіксована кома) */
    digimatic_unit_t unit;  /* Одиниця виміру (мм або дюйми) */
    bool is_negative;       /* Знак виміряної величини */
} digimatic_reading_t;

typedef struct {
    uint8_t nibbles[DIGIMATIC_NIBBLES];
    volatile uint8_t bit_index;
    volatile bool rx_complete;
} digimatic_driver_t;

static digimatic_driver_t g_driver;

/* Викликається в обробнику переривання EXTI за спадним фронтом лінії CK */
void digimatic_on_clock_falling_isr(bool data_pin_level) {
    if (g_driver.rx_complete) return;

    uint8_t nibble_idx = g_driver.bit_index >> 2;
    uint8_t bit_pos = g_driver.bit_index & 0x03;

    if (nibble_idx < DIGIMATIC_NIBBLES) {
        if (data_pin_level) {
            g_driver.nibbles[nibble_idx] |= (uint8_t)(1U << bit_pos);
        }
        g_driver.bit_index++;
    }

    if (g_driver.bit_index >= DIGIMATIC_TOTAL_BITS) {
        g_driver.rx_complete = true;
    }
}

/* Декодування 52-бітного буфера з перевіркою BCD та преамбули */
digimatic_status_t digimatic_decode(const digimatic_driver_t *drv, digimatic_reading_t *out) {
    if (!drv->rx_complete) return DIGIMATIC_ERR_BUSY;

    /* Перевірка 16-бітної преамбули d1..d4 (має бути 0xFFFF) */
    uint16_t preamble = drv->nibbles[0] | (drv->nibbles[1] << 4) |
                        (drv->nibbles[2] << 8) | (drv->nibbles[3] << 12);
    if (preamble != PREAMBLE_EXPECTED) return DIGIMATIC_ERR_PREAMBLE;

    /* Знак: нібл d5 (0x0 = плюс, 0x8 = мінус) */
    out->is_negative = (drv->nibbles[4] & 0x08) != 0;

    /* Розпакування мантиси d6..d11 у двійково-десятковому коді */
    int32_t mantissa = 0;
    for (int i = 5; i <= 10; i++) {
        uint8_t digit = drv->nibbles[i] & 0x0F;
        if (digit > 9) return DIGIMATIC_ERR_BCD;
        mantissa = (mantissa * 10) + digit;
    }

    /* Позиція коми d12 та одиниці d13 */
    uint8_t decimal_places = drv->nibbles[11] & 0x07;
    out->unit = (drv->nibbles[12] & 0x01) ? DIGIMATIC_UNIT_INCH : DIGIMATIC_UNIT_MM;

    /* Нормалізація у мікрометри: при 2 знаках (0.01 мм) множимо на 10 */
    if (out->unit == DIGIMATIC_UNIT_MM) {
        out->value_um = (decimal_places == 2) ? (mantissa * 10) : mantissa;
    } else {
        out->value_um = mantissa;
    }

    if (out->is_negative) out->value_um = -out->value_um;
    return DIGIMATIC_OK;
}
