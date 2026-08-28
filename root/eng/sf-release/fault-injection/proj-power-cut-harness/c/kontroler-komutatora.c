#include <stdint.h>
#include <stdbool.h>

/* Базові константи та порти комутатора */
#define PIN_HS_GATE      (1U << 4)   /* P-MOSFET верхнього плеча (Active LOW) */
#define PIN_CROWBAR_GATE (1U << 5)   /* N-MOSFET активного розряду (Active HIGH) */
#define PIN_TRIG_INPUT   (1U << 0)   /* Вхід апаратного тригера з DUT */

typedef struct {
    volatile uint32_t delay_us;       /* Затримка від тригера до обриву (мкс) */
    volatile uint32_t cut_duration_ms;/* Тривалість фази знеструмлення (мс) */
    volatile bool     armed;          /* Прапорець готовності до перехоплення */
    volatile bool     cycle_completed;/* Прапорець завершення циклу */
    uint32_t          total_cycles;   /* Загальний лічильник виконаних циклів */
} harness_state_t;

static harness_state_t g_harness = {
    .delay_us = 100,
    .cut_duration_ms = 50,
    .armed = false,
    .cycle_completed = false,
    .total_cycles = 0
};

/* Апаратне вмикання живлення цільового пристрою */
static inline void power_rail_enable(void) {
    /* 1. Закриваємо розрядний N-MOSFET */
    /* GPIO_PORT->BSRR = (PIN_CROWBAR_GATE << 16); */
    
    /* Захисна пауза (dead-time) для запобігання наскрізного струму: 50 нс */
    __asm volatile("nop; nop; nop; nop;");
    
    /* 2. Відкриваємо силовий P-MOSFET верхнього плеча (подаємо LOW на затвор) */
    /* GPIO_PORT->BSRR = (PIN_HS_GATE << 16); */
}

/* Апаратне екстремальне знеструмлення шини живлення з активним розрядом */
static inline void power_rail_emergency_cut(void) {
    /* 1. Миттєво закриваємо P-MOSFET верхнього плеча (подаємо HIGH на затвор) */
    /* GPIO_PORT->BSRR = PIN_HS_GATE; */
    
    /* Захисний інтервал dead-time перед розрядом: 50 нс */
    __asm volatile("nop; nop; nop; nop;");
    
    /* 2. Відкриваємо активний N-MOSFET Crowbar (скидаємо заряд ємностей DUT на GND) */
    /* GPIO_PORT->BSRR = PIN_CROWBAR_GATE; */
}

/* Обробник переривання апаратного таймера точної затримки */
void TIM2_IRQHandler(void) {
    /* Очищення прапорця переривання таймера */
    /* TIM2->SR = ~TIM_SR_UIF; */

    if (g_harness.armed) {
        /* Фаза точного обриву живлення */
        power_rail_emergency_cut();
        g_harness.armed = false;
        g_harness.cycle_completed = true;
        g_harness.total_cycles++;
        
        /* Запуск таймера тривалості знеструмлення */
        /* timer_start_ms(g_harness.cut_duration_ms); */
    }
}

/* Обробник зовнішнього переривання від GPIO-тригера цільового пристрою */
void EXTI0_IRQHandler(void) {
    /* Очищення прапорця переривання EXTI */
    /* EXTI->PR = PIN_TRIG_INPUT; */

    if (g_harness.armed) {
        if (g_harness.delay_us == 0) {
            /* Миттєвий обрив без затримки */
            power_rail_emergency_cut();
            g_harness.armed = false;
            g_harness.cycle_completed = true;
            g_harness.total_cycles++;
        } else {
            /* Завантаження мікросекундного зміщення в лічильник таймера */
            /* TIM2->CNT = 0; */
            /* TIM2->ARR = g_harness.delay_us; */
            /* TIM2->CR1 |= TIM_CR1_CEN; */
        }
    }
}

/* Ініціалізація та армування нового циклу випробування */
void harness_arm_cycle(uint32_t target_delay_us, uint32_t power_off_ms) {
    g_harness.delay_us = target_delay_us;
    g_harness.cut_duration_ms = power_off_ms;
    g_harness.cycle_completed = false;
    
    /* Подаємо живлення на DUT перед очікуванням тригера */
    power_rail_enable();
    
    /* Дозволяємо перехоплення фронту сигналу */
    g_harness.armed = true;
}
