#include "board.h"
#include "stm32f1_regs.h"

#define LED_PIN 13U  /* PC13: анод на 3.3 В, катод через 330 Ом до ніжки        */
#define BTN_PIN 0U   /* PA0:  кнопка на землю, зовнішня підтяжка вгору          */

void board_init(void)
{
    /* Тактування портів A і C та блоку AFIO (без нього не працюють лінії EXTI). */
    RCC_APB2ENR |= RCC_APB2ENR_IOPAEN | RCC_APB2ENR_IOPCEN | RCC_APB2ENR_AFIOEN;

    /* Кнопка: вхід із підтяжкою, тетрада 0 регістра CRL. */
    GPIO_CRL(GPIOA_BASE) = (GPIO_CRL(GPIOA_BASE) & ~(0xFUL << (BTN_PIN * 4U))) |
                           (GPIO_CFG_IN_PULL << (BTN_PIN * 4U));
    /* Напрям внутрішньої підтяжки задає ODR: одиниця — угору. Зовнішні R1 і C
       від цього не стають зайвими: внутрішні 40 кОм заряджали б 100 нФ близько
       4 мс, і кнопка відповідала б із помітною затримкою. */
    GPIO_ODR(GPIOA_BASE) |= (1UL << BTN_PIN);

    /* Світлодіод: вихід push-pull 2 МГц, тетрада 5 регістра CRH (вивід 13).
       Схема Active-LOW дозволяє замість GPIO_CFG_OUT_PP_2M поставити
       GPIO_CFG_OUT_OD_2M: верхній P-MOSFET вимикається, у логічній одиниці
       вивід іде в Hi-Z, і світлодіод можна живити від 5 В на 5V-толерантній
       ніжці, не подаючи цих 5 В на шину 3.3 В. */
    GPIO_CRH(GPIOC_BASE) = (GPIO_CRH(GPIOC_BASE) & ~(0xFUL << ((LED_PIN - 8U) * 4U))) |
                           (GPIO_CFG_OUT_PP_2M << ((LED_PIN - 8U) * 4U));

    board_led_set(false);
}

uint8_t board_button_level(void)
{
    return (uint8_t)((GPIO_IDR(GPIOA_BASE) >> BTN_PIN) & 1UL);
}

void board_led_set(bool on)
{
    /* Активний нуль: світиться, коли ніжка притягнута до землі. BSRR/BRR
       перемикають один біт без читання ODR, тож обробник переривання не може
       затерти сусідній вивід порту. */
    if (on) {
        GPIO_BRR(GPIOC_BASE) = (1UL << LED_PIN);
    } else {
        GPIO_BSRR(GPIOC_BASE) = (1UL << LED_PIN);
    }
}

bool board_led_is_on(void)
{
    return (GPIO_ODR(GPIOC_BASE) & (1UL << LED_PIN)) == 0UL;
}

void board_led_toggle(void)
{
    board_led_set(!board_led_is_on());
}

void board_systick_start_10ms(void)
{
    /* 8 МГц / 100 = 80000 тактів на 10 мс; у регістрі лежить N-1, і 79999
       вміщається у 24 біти лічильника. */
    SYSTICK_LOAD = (F_CPU / 100UL) - 1UL;
    SYSTICK_VAL = 0UL;  /* запис будь-якого значення скидає лічильник і прапорець */
    SYSTICK_CTRL = SYSTICK_CTRL_CLKSOURCE | SYSTICK_CTRL_TICKINT | SYSTICK_CTRL_ENABLE;
}
