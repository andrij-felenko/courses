#include <stdint.h>
#include <stdbool.h>

/* Структура конфігурації та стану силового каналу */
typedef struct {
    volatile uint32_t *port_bsrr;  /* Регістр атомарного встановлення/скидання порту (GPIOx->BSRR) */
    uint32_t pin_mask;             /* Бітова маска піна (1 << PIN) */
    volatile uint32_t *timer_ccr;  /* Регістр порівняння таймера ШІМ (TIMx->CCRx) */
    uint32_t timer_arr;            /* Максимальне значення лічильника таймера (TIMx->ARR) */
    uint32_t current_duty;         /* Поточне заповнення (0..1000 = 0.0..100.0%) */
    uint32_t target_duty;          /* Цільове значення заповнення */
    uint32_t step_increment;       /* Крок зміни шпаруватості за 1 мс */
    uint32_t safety_timeout_ms;    /* Залишок часу безпечної роботи каналу */
    bool is_enabled;               /* Прапорець дозволу роботи */
} load_switch_t;

/* Безпечна ініціалізація каналу: скидаємо вихід перед конфігурацією порту */
void load_switch_init(load_switch_t *sw, volatile uint32_t *bsrr, uint32_t pin, 
                      volatile uint32_t *ccr, uint32_t arr, uint32_t step) {
    sw->port_bsrr = bsrr;
    sw->pin_mask = (1UL << pin);
    sw->timer_ccr = ccr;
    sw->timer_arr = arr;
    sw->current_duty = 0;
    sw->target_duty = 0;
    sw->step_increment = (step > 0) ? step : 10;
    sw->safety_timeout_ms = 0;
    sw->is_enabled = false;

    /* Атомарно записуємо логічний нуль у регістр скидання BSRR (старші 16 біт) */
    *(sw->port_bsrr) = (sw->pin_mask << 16U);
    if (sw->timer_ccr != 0) {
        *(sw->timer_ccr) = 0;
    }
}

/* Встановлення цільової потужності з таймаутом безпеки */
void load_switch_set_power(load_switch_t *sw, uint32_t duty_permille, uint32_t timeout_ms) {
    if (duty_permille > 1000) {
        duty_permille = 1000;
    }
    sw->target_duty = duty_permille;
    sw->safety_timeout_ms = timeout_ms;
    sw->is_enabled = (duty_permille > 0);
}

/* Аварійне миттєве знеструмлення каналу */
void load_switch_emergency_stop(load_switch_t *sw) {
    sw->target_duty = 0;
    sw->current_duty = 0;
    sw->is_enabled = false;
    sw->safety_timeout_ms = 0;

    if (sw->timer_ccr != 0) {
        *(sw->timer_ccr) = 0;
    }
    *(sw->port_bsrr) = (sw->pin_mask << 16U);
}

/* Періодичний обробник (викликається щомілісекунди з SysTick або таймера) */
void load_switch_tick_1ms(load_switch_t *sw) {
    /* Перевірка таймауту безпеки */
    if (sw->safety_timeout_ms > 0) {
        sw->safety_timeout_ms--;
        if (sw->safety_timeout_ms == 0) {
            load_switch_emergency_stop(sw);
            return;
        }
    }

    /* Алгоритм плавного пуску та гальмування (Soft-Start / Soft-Stop) */
    if (sw->current_duty < sw->target_duty) {
        sw->current_duty += sw->step_increment;
        if (sw->current_duty > sw->target_duty) {
            sw->current_duty = sw->target_duty;
        }
    } else if (sw->current_duty > sw->target_duty) {
        if (sw->current_duty <= sw->step_increment) {
            sw->current_duty = 0;
        } else {
            sw->current_duty -= sw->step_increment;
        }
    }

    /* Запис нового значення шпаруватості в апаратний регістр порівняння */
    if (sw->timer_ccr != 0) {
        uint32_t compare_val = (sw->current_duty * sw->timer_arr) / 1000U;
        *(sw->timer_ccr) = compare_val;
    }
}
