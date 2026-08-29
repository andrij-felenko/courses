/* Фаза 2: генератор контрольних сигналів.
   Меандр на діагностичних майданчиках — найдешевший спосіб за секунду
   побачити осцилографом, чи ціла доріжка й чи працює двотактний буфер. */
#include "bringup.h"
#include "stm32f4_regs.h"

#define TP_PORT           GPIOA_BASE
#define TP_HALF_PERIOD_US 5U   /* половина періоду → меандр ~100 кГц */

/* Контрольні майданчики плати: PA5, PA6, PA7 (гребінка біля краю). */
static const uint8_t tp_pins[] = { 5U, 6U, 7U };
#define TP_COUNT (sizeof tp_pins / sizeof tp_pins[0])

void bringup_gpio_toggle_testpoints(uint32_t iterations)
{
    uint32_t set_mask = 0U;
    uint32_t reset_mask = 0U;
    uint32_t i;

    RCC_AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    (void)RCC_AHB1ENR;  /* читання назад: такт затримки шини після вмикання */

    for (i = 0U; i < TP_COUNT; ++i) {
        uint32_t pin = tp_pins[i];
        uint32_t two = pin * 2U;

        GPIO_OTYPER(TP_PORT) &= ~(1U << pin);                 /* Push-Pull */
        GPIO_PUPDR(TP_PORT) &= ~(3U << two);                  /* без підтяжок */
        GPIO_OSPEEDR(TP_PORT) = (GPIO_OSPEEDR(TP_PORT) & ~(3U << two))
                              | (GPIO_SPEED_HIGH << two);     /* круті фронти */
        GPIO_MODER(TP_PORT) = (GPIO_MODER(TP_PORT) & ~(3U << two))
                            | (GPIO_MODE_OUTPUT << two);

        set_mask |= (1U << pin);
        reset_mask |= (1U << (pin + 16));  /* верхня половина BSRR скидає */
    }

    for (i = 0U; i < iterations; ++i) {
        GPIO_BSRR(TP_PORT) = set_mask;
        bringup_delay_us(TP_HALF_PERIOD_US);
        GPIO_BSRR(TP_PORT) = reset_mask;
        bringup_delay_us(TP_HALF_PERIOD_US);
    }

    /* Лишаємо майданчики в нулі: постійний високий рівень на непідключеному
       піні легко сплутати з результатом перевірки. */
    GPIO_BSRR(TP_PORT) = reset_mask;
}
