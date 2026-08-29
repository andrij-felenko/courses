/* ports/stm32f4/stm32_exti_isr.c — обробник зовнішнього переривання кнопки.
 * Взірцевий приклад межі: обробник не малює на дисплеї, не пише у флеш і
 * не рахує нічого. Він скидає прапорець, ставить подію в чергу й виходить —
 * два-три десятки тактів. Уся змістовна робота відбувається згодом, у
 * головному циклі, де її не жаль перервати наступним перериванням. */
#include "hal/hal_time.h"
#include "include/board.h"
#include "include/event_types.h"
#include "ports/stm32f4/stm32_port.h"
#include "services/event_queue.h"

#include "stm32f4xx.h"

#define BUTTON_PIN            0u    /* PA0 */
#define BUTTON_DEBOUNCE_MS    50u

static volatile uint32_t g_last_click_ms;

void EXTI0_IRQHandler(void)
{
    if ((EXTI->PR & (1u << BUTTON_PIN)) == 0u) {
        return;
    }
    EXTI->PR = (1u << BUTTON_PIN);   /* прапорець скидається записом одиниці */

    const uint32_t now = hal_time_now_ms();

    /* Механічний контакт деренчить кілька мілісекунд і дає десятки
     * переривань на один натиск. Відсіюємо їх тут, найдешевшим способом:
     * порівнянням двох чисел, без таймерів і без затримок в обробнику. */
    if ((now - g_last_click_ms) < BUTTON_DEBOUNCE_MS) {
        return;
    }
    g_last_click_ms = now;

    event_queue_t *queue = board_event_queue();
    if (queue == 0) {
        return;   /* черга ще не прив'язана: подію нема куди класти */
    }

    sys_event_t evt = sys_event_make(EVT_ID_BUTTON_CLICK, now);
    evt.data.button_pin = (uint8_t)BUTTON_PIN;

    /* Черга сама бере критичну секцію й сама рахує переповнення, тож
     * навіть коли головний цикл захлинувся, обробник не заклякне. */
    (void)event_queue_post_from_isr(queue, &evt);
}

void stm32_button_exti_init(void)
{
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    RCC->APB2ENR |= RCC_APB2ENR_SYSCFGEN;

    /* PA0 — вхід із підтяжкою до живлення, кнопка замикає на землю. */
    GPIOA->MODER &= ~(3u << (BUTTON_PIN * 2u));
    GPIOA->PUPDR &= ~(3u << (BUTTON_PIN * 2u));
    GPIOA->PUPDR |=  (1u << (BUTTON_PIN * 2u));

    SYSCFG->EXTICR[0] &= ~SYSCFG_EXTICR1_EXTI0;   /* джерело — порт A */

    EXTI->IMR  |=  (1u << BUTTON_PIN);   /* переривання дозволено */
    EXTI->FTSR |=  (1u << BUTTON_PIN);   /* спад: натиск */
    EXTI->RTSR &= ~(1u << BUTTON_PIN);

    /* Пріоритет нижчий за системний таймер: кнопка терпить, час — ні. */
    NVIC_SetPriority(EXTI0_IRQn, 2u);
    NVIC_EnableIRQ(EXTI0_IRQn);
}
