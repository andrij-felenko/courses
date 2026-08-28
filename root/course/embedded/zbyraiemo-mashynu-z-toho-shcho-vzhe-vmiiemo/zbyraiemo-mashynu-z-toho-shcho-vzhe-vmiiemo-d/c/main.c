#include <stdint.h>
#include <stdbool.h>

/* Фізичні адреси регістрів у карті пам'яті MMIO */
#define REG_GPIO_OUT (*(volatile uint8_t *)0x8000)
#define REG_GPIO_IN  (*(volatile uint8_t *)0x8001)

#define LED_PIN_MASK (1U << 0)
#define BTN_PIN_MASK (1U << 0)

void led_set(bool state) {
    if (state) {
        REG_GPIO_OUT |= LED_PIN_MASK;   /* Запис 1 у біт 0: світлодіод спалахує */
    } else {
        REG_GPIO_OUT &= ~LED_PIN_MASK;  /* Запис 0 у біт 0: світлодіод гасне */
    }
}

bool button_is_pressed(void) {
    /* Кнопка підтягнута до живлення: при натисканні замикає пін на 0 В */
    return (REG_GPIO_IN & BTN_PIN_MASK) == 0;
}
