/* c_mmio_driver.h / c_mmio_driver.c — Класичний підхід мовою C */
#include <stdint.h>
#include <stdbool.h>

#define GPIOA_BASE          (0x40020000UL)
#define GPIOA_MODER_OFFSET  (0x00UL)
#define GPIOA_IDR_OFFSET    (0x10UL)
#define GPIOA_ODR_OFFSET    (0x14UL)

/* Нетипізовані макроси розіменування адрес */
#define GPIOA_MODER (*(volatile uint32_t*)(GPIOA_BASE + GPIOA_MODER_OFFSET))
#define GPIOA_IDR   (*(volatile uint32_t*)(GPIOA_BASE + GPIOA_IDR_OFFSET))
#define GPIOA_ODR   (*(volatile uint32_t*)(GPIOA_BASE + GPIOA_ODR_OFFSET))

#define PIN_5_MASK        (1U << 5)
#define PIN_5_MODE_OUTPUT (1U << (5 * 2))

/* Функція налаштування режиму піна */
void gpioa_pin5_set_output(void) {
    /* Немає захисту від стану гонитви з перериваннями */
    /* Немає перевірки коректності зміщення бітів */
    GPIOA_MODER |= PIN_5_MODE_OUTPUT;
}

/* Функція запису стану виводу */
void gpioa_pin5_write(bool high) {
    if (high) {
        GPIOA_ODR |= PIN_5_MASK;
    } else {
        GPIOA_ODR &= ~PIN_5_MASK;
    }
}

/* Функція читання вхідного стану */
bool gpioa_pin5_read(void) {
    return (GPIOA_IDR & PIN_5_MASK) != 0;
}

/* Приклад помилкового коду, який компілятор C пропускає */
void dangerous_c_usage(void) {
    /* Помилка: спроба запису у вхідний регістр IDR */
    GPIOA_IDR = 0x1234; 
}
