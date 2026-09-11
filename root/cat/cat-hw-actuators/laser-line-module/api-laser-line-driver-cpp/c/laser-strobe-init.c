#include <stdint.h>
#include <stdbool.h>

/* Базові структури регістрів таймера мікроконтролера ARM Cortex-M */
typedef struct {
    volatile uint32_t CR1;      /* Регістр керування 1 */
    volatile uint32_t CR2;      /* Регістр керування 2 */
    volatile uint32_t SMCR;     /* Регістр конфігурації підлеглого режиму (Slave Mode) */
    volatile uint32_t DIER;     /* Регістр дозволу переривань та запитів DMA */
    volatile uint32_t SR;       /* Регістр статусу */
    volatile uint32_t EGR;      /* Регістр генерації подій */
    volatile uint32_t CCMR1;    /* Регістр вибору режиму каналів 1 та 2 */
    volatile uint32_t CCMR2;    /* Регістр вибору режиму каналів 3 та 4 */
    volatile uint32_t CCER;     /* Регістр дозволу роботи виходів захоплення/порівняння */
    volatile uint32_t CNT;      /* Лічильник таймера */
    volatile uint32_t PSC;      /* Дільник частоти (Prescaler) */
    volatile uint32_t ARR;      /* Регістр автоперезавантаження (Auto-Reload) */
    volatile uint32_t RCR;      /* Регістр повторення відліків */
    volatile uint32_t CCR[4];   /* Регістри захоплення/порівняння (CCR1-CCR4) */
} timer_registers_t;

typedef struct {
    timer_registers_t *timer;   /* Базова адреса таймера (наприклад, TIM2 або TIM3) */
    uint32_t timer_clock_hz;    /* Вхідна частота тактування шини таймера (наприклад, 84000000) */
    uint32_t channel_index;     /* Індекс каналу (0 для CCR1) */
} laser_strobe_driver_t;

/**
 * @brief Ініціалізація апаратного таймера в режимі одиничного імпульсу (One-Pulse Mode).
 */
void laser_strobe_init(laser_strobe_driver_t *drv) {
    if (!drv || !drv->timer) {
        return;
    }

    timer_registers_t *tim = drv->timer;

    /* 1. Зупиняємо таймер і скидаємо конфігурацію */
    tim->CR1 = 0;
    tim->CR2 = 0;
    tim->SMCR = 0;

    /* 2. Налаштовуємо дільник так, щоб один такт лічильника дорівнював 1 мкс:
       PSC = (частота шини / 1 000 000) - 1 */
    tim->PSC = (drv->timer_clock_hz / 1000000U) - 1U;

    /* 3. Вмикаємо режим одиничного імпульсу: біт OPM (біт 3) у регістрі CR1.
       Також вмикаємо буферизацію регістра ARR (ARPE, біт 7). */
    tim->CR1 |= (1U << 3) | (1U << 7);

    /* 4. Конфігурація каналу 1 у режим вихідного порівняння (PWM mode 2 або PWM mode 1).
       Вибираємо PWM Mode 2 (111b у бітах OC1M):
       - Вихід неактивний, поки CNT < CCR1;
       - Вихід активний, коли CCR1 <= CNT < ARR.
       Також вмикаємо буферизацію регістра порівняння (OC1PE, біт 3). */
    tim->CCMR1 &= ~((0x7U << 4) | (0x3U << 0));
    tim->CCMR1 |= (0x7U << 4) | (1U << 3);

    /* 5. Дозволяємо вихід сигналу на зовнішній пін: біт CC1E (біт 0) у CCER.
       Полярність пряма: активна логічна одиниця (біт CC1P = 0). */
    tim->CCER &= ~(1U << 1);    /* Пряма полярність (активний високий) */
    tim->CCER |= (1U << 0);     /* Активація виходу каналу */
}

/**
 * @brief Налаштування параметрів стробу: затримки старту та тривалості імпульсу в мікросекундах.
 */
void laser_strobe_set_timing(laser_strobe_driver_t *drv, uint32_t delay_us, uint32_t duration_us) {
    if (!drv || !drv->timer) {
        return;
    }

    timer_registers_t *tim = drv->timer;

    /* Захисна затримка від фронту тригера до початку спалаху */
    tim->CCR[drv->channel_index] = delay_us;

    /* Повне значення лічби до вимкнення імпульсу */
    tim->ARR = delay_us + duration_us;

    /* Оновлюємо тіньові регістри генерацією програмної події UG */
    tim->EGR = (1U << 0);
}

/**
 * @brief Прив'язка запуску стробу до зовнішнього вхідного тригера камери (TI1FP1 або ETR).
 */
void laser_strobe_attach_external_trigger(laser_strobe_driver_t *drv) {
    if (!drv || !drv->timer) {
        return;
    }

    timer_registers_t *tim = drv->timer;

    /* Налаштування вхідного тригера в регістрі SMCR:
       - TS = 101b (тригер від входу TI1FP1 — лінія Exposure Active від камери);
       - SMS = 110b (Trigger Mode: за висхідним фронтом тригера лічильник автоматично запускається). */
    tim->SMCR &= ~((0x7U << 4) | (0x7U << 0));
    tim->SMCR |= (0x5U << 4) | (0x6U << 0);
}

/**
 * @brief Програмний запуск одиночного строб-імпульсу (для тестування або ручної експозиції).
 */
void laser_strobe_fire_software(laser_strobe_driver_t *drv) {
    if (!drv || !drv->timer) {
        return;
    }

    /* Скидаємо лічильник у нуль і активуємо біт лічби CEN */
    drv->timer->CNT = 0;
    drv->timer->CR1 |= (1U << 0);
}
