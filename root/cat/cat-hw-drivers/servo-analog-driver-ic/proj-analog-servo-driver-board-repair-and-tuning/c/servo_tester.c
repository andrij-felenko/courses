#include "servo_tester.h"
#include <stddef.h>

// Біти регістрів керування таймером
#define TIM_CR1_CEN     (1U << 0)  // Counter Enable
#define TIM_CCER_CC1E   (1U << 0)  // Capture/Compare 1 Output Enable

// Допоміжна функція обмеження значення діапазоном [min, max]
static uint16_t clamp_u16(uint16_t val, uint16_t min_val, uint16_t max_val) {
    if (val < min_val) return min_val;
    if (val > max_val) return max_val;
    return val;
}

bool servo_tester_init(servo_tester_t *tester, servo_timer_regs_t *timer_hardware, uint32_t system_clk_hz) {
    if (tester == NULL || timer_hardware == NULL || system_clk_hz < 1000000U) {
        return false;
    }

    tester->timer = timer_hardware;
    tester->timer_clk_hz = system_clk_hz;
    tester->current_pulse_us = SERVO_NEUTRAL_PULSE_US;
    tester->is_active = false;

    // Обчислюємо значення переддільника PSC для отримання кванту таймера 1 мікросекунда (1 МГц)
    // PSC = (F_sys / 1_000_000) - 1
    uint32_t prescaler = (system_clk_hz / 1000000U) - 1U;
    tester->timer->PSC = prescaler;

    // Встановлюємо період таймера ARR = 20000 мкс - 1 (для кадру 50 Гц / 20 мс)
    tester->timer->ARR = SERVO_PERIOD_US - 1U;

    // Початкове значення високого рівня — нейтральна позиція 1500 мкс
    tester->timer->CCR1 = SERVO_NEUTRAL_PULSE_US;

    // Вимикаємо вихід до виклику servo_tester_start
    tester->timer->CR1 &= ~TIM_CR1_CEN;
    tester->timer->CCER &= ~TIM_CCER_CC1E;

    return true;
}

void servo_tester_set_pulse_us(servo_tester_t *tester, uint16_t pulse_us) {
    if (tester == NULL || tester->timer == NULL) {
        return;
    }

    // Захист аналогового підсилювача AA5188 / KC0032 від виходу за межі механічного упору
    uint16_t safe_pulse = clamp_u16(pulse_us, SERVO_MIN_PULSE_US, SERVO_MAX_PULSE_US);
    tester->current_pulse_us = safe_pulse;

    // Запис у регістр порівняння таймера (визначення тривалості імпульсу в мкс)
    tester->timer->CCR1 = safe_pulse;
}

void servo_tester_set_angle(servo_tester_t *tester, uint8_t angle_deg) {
    if (tester == NULL) {
        return;
    }

    if (angle_deg > SERVO_MAX_ANGLE_DEG) {
        angle_deg = SERVO_MAX_ANGLE_DEG;
    }

    // Лінійний перерахунок кута 0..180 градусів у тривалість імпульсу 1000..2000 мкс
    // pulse = MIN_PULSE + (angle * (MAX_PULSE - MIN_PULSE)) / 180
    uint16_t pulse_us = SERVO_MIN_PULSE_US + 
        (uint16_t)(((uint32_t)angle_deg * (SERVO_MAX_PULSE_US - SERVO_MIN_PULSE_US)) / SERVO_MAX_ANGLE_DEG);

    servo_tester_set_pulse_us(tester, pulse_us);
}

uint16_t servo_tester_get_pulse_us(const servo_tester_t *tester) {
    if (tester == NULL) {
        return 0;
    }
    return tester->current_pulse_us;
}

uint8_t servo_tester_get_angle(const servo_tester_t *tester) {
    if (tester == NULL) {
        return 0;
    }

    // Зворотний перерахунок імпульсу в кут градусів
    uint32_t pulse = tester->current_pulse_us;
    if (pulse < SERVO_MIN_PULSE_US) pulse = SERVO_MIN_PULSE_US;
    
    uint32_t angle = ((pulse - SERVO_MIN_PULSE_US) * SERVO_MAX_ANGLE_DEG) / 
                     (SERVO_MAX_PULSE_US - SERVO_MIN_PULSE_US);

    return (uint8_t)angle;
}

void servo_tester_start(servo_tester_t *tester) {
    if (tester == NULL || tester->timer == NULL) {
        return;
    }

    // Вмикаємо вихідний канал ШІМ і сам таймер
    tester->timer->CCER |= TIM_CCER_CC1E;
    tester->timer->CR1 |= TIM_CR1_CEN;
    tester->is_active = true;
}

void servo_tester_stop(servo_tester_t *tester) {
    if (tester == NULL || tester->timer == NULL) {
        return;
    }

    // Вимикаємо таймер і вихід генерації
    tester->timer->CR1 &= ~TIM_CR1_CEN;
    tester->timer->CCER &= ~TIM_CCER_CC1E;
    tester->is_active = false;
}

void servo_tester_calibrate_neutral(servo_tester_t *tester) {
    // Для аналогових серводрайверів AA5188/KC0032 встановити 1500 мкс необхідно
    // для механічного підлаштування вала потенціометра у точний центр
    servo_tester_set_pulse_us(tester, SERVO_NEUTRAL_PULSE_US);
}
