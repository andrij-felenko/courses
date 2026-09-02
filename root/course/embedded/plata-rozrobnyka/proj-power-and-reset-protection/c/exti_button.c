#include "exti_button.h"
#include "board.h"
#include "stm32f1_regs.h"

#define BTN_PIN      0U
#define BTN_LINE     (1UL << BTN_PIN)
#define DEBOUNCE_MS  20U

static volatile button_event_t s_event = BUTTON_EVENT_NONE;
static volatile uint8_t s_stable_level = 1U;

/* Обробник і головний цикл ділять дві змінні. На Cortex-M3 запис 8-бітного
   слова атомарний, але пара «прочитати й обнулити» — ні, тож на два такти
   гасимо переривання. */
static inline void irq_disable(void) { __asm volatile ("cpsid i" ::: "memory"); }
static inline void irq_enable(void)  { __asm volatile ("cpsie i" ::: "memory"); }

static void timer_start_oneshot(void)
{
    TIM3_CNT = 0UL;
    TIM3_SR &= ~TIM_SR_UIF;
    TIM3_CR1 |= TIM_CR1_CEN;  /* завдяки OPM таймер зупиниться сам */
}

void exti_button_init(void)
{
    /* --- Таймер блокування: 1 тик = 1 мс, один прохід на 20 мс --- */
    RCC_APB1ENR |= RCC_APB1ENR_TIM3EN;
    TIM3_PSC = (F_CPU / 1000UL) - 1UL;
    TIM3_ARR = DEBOUNCE_MS - 1UL;
    TIM3_CR1 = TIM_CR1_OPM | TIM_CR1_URS;
    TIM3_EGR = TIM_EGR_UG;      /* переносимо PSC і ARR у тіньові регістри */
    TIM3_SR &= ~TIM_SR_UIF;     /* подія UG підняла прапорець — знімаємо його */
    TIM3_DIER |= TIM_DIER_UIE;
    NVIC_ISER0 = (1UL << TIM3_IRQn);

    /* --- Лінія EXTI0 --- */
    AFIO_EXTICR1 &= ~0xFUL;     /* джерело лінії 0 — порт A */
    EXTI_FTSR |= BTN_LINE;      /* натискання: фронт униз  */
    EXTI_RTSR |= BTN_LINE;      /* відпускання: фронт угору */
    EXTI_PR = BTN_LINE;         /* скидаємо сміття, накопичене при налаштуванні */

    s_stable_level = board_button_level();
    s_event = BUTTON_EVENT_NONE;

    EXTI_IMR |= BTN_LINE;
    NVIC_ISER0 = (1UL << EXTI0_IRQn);
}

/* Імена обробників беруться з таблиці векторів стандартного startup-файлу. */
void EXTI0_IRQHandler(void)
{
    EXTI_PR = BTN_LINE;        /* прапорець знімається записом одиниці */
    EXTI_IMR &= ~BTN_LINE;     /* глушимо лінію на час брязкоту */
    timer_start_oneshot();
}

void TIM3_IRQHandler(void)
{
    if ((TIM3_SR & TIM_SR_UIF) == 0UL) {
        return;  /* не наше джерело: інші канали таймера лишаємо їхнім власникам */
    }
    TIM3_SR &= ~TIM_SR_UIF;

    const uint8_t level = board_button_level();
    if (level != s_stable_level) {
        s_stable_level = level;
        s_event = (level == 0U) ? BUTTON_EVENT_PRESSED : BUTTON_EVENT_RELEASED;
    }
    /* Якщо рівень повернувся до попереднього, події немає взагалі: спрацював
       не контакт, а завада, і вона щойно коштувала нам двох переривань. */

    /* Поки лінія була замаскована, EXTI устиг записати в PR десятки фронтів.
       Знімаємо їх ДО зняття маски, інакше контролер миттєво викличе обробник
       ще раз — і весь антибрязкіт піде намарне. */
    EXTI_PR = BTN_LINE;
    EXTI_IMR |= BTN_LINE;
}

button_event_t exti_button_take_event(void)
{
    irq_disable();
    const button_event_t ev = s_event;
    s_event = BUTTON_EVENT_NONE;
    irq_enable();
    return ev;
}
