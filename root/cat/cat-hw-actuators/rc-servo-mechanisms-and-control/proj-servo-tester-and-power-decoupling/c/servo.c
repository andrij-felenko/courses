#include "servo.h"
#include <stdio.h>

/**
 * @file servo.c
 * @brief Реалізація драйвера сервомеханізму радіокерованих моделей.
 *
 * Фізичні принципи:
 * Сервомеханізм складається з електродвигуна постійного струму, понижувального
 * редуктора для підвищення крутного моменту, потенціометра зворотного зв'язку
 * на вихідному валу та плати керування (компаратор/мікроконтролер + H-міст).
 *
 * Керуючий сигнал є широтно-імпульсно модульованим (ШІМ) з часом кадру 20 мс (50 Гц).
 * Кут повороту вала пропорційний ширині високого рівня імпульсу:
 *  - 0.5 мс (500 мкс)   -> мінімальний кут (0°)
 *  - 1.5 мс (1500 мкс)  -> нейтральне положення (90°)
 *  - 2.5 мс (2500 мкс)  -> максимальний кут (180°)
 */

/* Симуляція регістрів апаратного таймера мікроконтролера */
static volatile uint32_t s_hardware_timer_icr = 0;  /*!< Регістр періоду (Top Value / Input Capture Register) */
static volatile uint32_t s_hardware_timer_ocr = 0;  /*!< Регістр порівняння (Output Compare Register) */
static volatile bool     s_hardware_timer_enabled = false;

/**
 * @brief Внутрішня функція обмежувача діапазону (clamping).
 */
static float clamp_float(float val, float min_val, float max_val)
{
    if (val < min_val) return min_val;
    if (val > max_val) return max_val;
    return val;
}

/**
 * @brief Внутрішня функція обмежувача для цілих чисел.
 */
static uint16_t clamp_uint16(uint16_t val, uint16_t min_val, uint16_t max_val)
{
    if (val < min_val) return min_val;
    if (val > max_val) return max_val;
    return val;
}

/**
 * @brief Апаратне оновлення регістрів порівняння таймера.
 */
static void update_hardware_compare_register(uint32_t ticks)
{
    /* Запис у теневий (shadow) регістр порівняння таймера для запобігання сплескам (glitches) */
    s_hardware_timer_ocr = ticks;
}

bool servo_init(servo_t *servo, uint8_t channel_id, uint16_t min_pulse_us, uint16_t max_pulse_us)
{
    if (servo == NULL) {
        return false;
    }

    if (min_pulse_us >= max_pulse_us || min_pulse_us < 200 || max_pulse_us > 4000) {
        /* Некоректні межі тривалості імпульсів */
        return false;
    }

    servo->channel_id = channel_id;
    servo->min_pulse_us = min_pulse_us;
    servo->max_pulse_us = max_pulse_us;
    servo->is_enabled = false;

    /* Розрахунок регістру періоду таймера на 20 мс (SERVO_FRAME_PERIOD_US = 20000 мкс)
     * При F_CPU = 16 МГц та Prescaler = 8:
     * Частота таймера = 16 000 000 / 8 = 2 000 000 Гц (2 тики на мікросекунду).
     * Період 20 000 мкс * 2 = 40 000 тактів таймера.
     */
    s_hardware_timer_icr = (uint32_t)SERVO_FRAME_PERIOD_US * (SERVO_CPU_FREQ_HZ / SERVO_TIMER_PRESCALER / 1000000UL);

    /* Встановлення за замовчуванням нейтрального положення (90°) */
    servo_set_angle(servo, 90.0f);

    return true;
}

uint32_t servo_pulse_us_to_timer_ticks(uint16_t pulse_us)
{
    /* Перетворення тривалості у мікросекундах у відліки апаратного таймера:
     * Ticks = pulse_us * (F_CPU / PRESCALER / 1 000 000)
     */
    uint32_t ticks_per_us = SERVO_CPU_FREQ_HZ / SERVO_TIMER_PRESCALER / 1000000UL;
    return (uint32_t)pulse_us * ticks_per_us;
}

void servo_set_pulse_us(servo_t *servo, uint16_t pulse_us)
{
    if (servo == NULL) {
        return;
    }

    /* Обмеження безпечними рамками конфігурації даної серви */
    uint16_t clamped_pulse = clamp_uint16(pulse_us, servo->min_pulse_us, servo->max_pulse_us);
    servo->current_pulse_us = clamped_pulse;

    /* Мапування ширини імпульсу в кут повороту 0..180° для інформаційного стану */
    float pulse_range = (float)(servo->max_pulse_us - servo->min_pulse_us);
    float pulse_offset = (float)(clamped_pulse - servo->min_pulse_us);
    servo->current_angle_deg = (pulse_offset / pulse_range) * SERVO_MAX_ANGLE_DEG;

    /* Перетворення у відліки апаратного таймера */
    servo->timer_ticks = servo_pulse_us_to_timer_ticks(clamped_pulse);

    if (servo->is_enabled) {
        update_hardware_compare_register(servo->timer_ticks);
    }
}

void servo_set_angle(servo_t *servo, float angle_deg)
{
    if (servo == NULL) {
        return;
    }

    /* Обмеження кута діапазоном 0°..180° */
    float clamped_angle = clamp_float(angle_deg, SERVO_MIN_ANGLE_DEG, SERVO_MAX_ANGLE_DEG);

    /* Лінійне мапування кута у тривалість імпульсу у мікросекундах:
     * pulse_us = min_pulse + (angle / 180.0) * (max_pulse - min_pulse)
     */
    float pulse_range = (float)(servo->max_pulse_us - servo->min_pulse_us);
    uint16_t pulse_us = (uint16_t)(servo->min_pulse_us + (clamped_angle / SERVO_MAX_ANGLE_DEG) * pulse_range);

    servo->current_angle_deg = clamped_angle;
    servo->current_pulse_us = pulse_us;
    servo->timer_ticks = servo_pulse_us_to_timer_ticks(pulse_us);

    if (servo->is_enabled) {
        update_hardware_compare_register(servo->timer_ticks);
    }
}

void servo_update_from_adc(servo_t *servo, uint16_t adc_value, uint16_t adc_max_value)
{
    if (servo == NULL || adc_max_value == 0) {
        return;
    }

    /* Обмеження вхідного відліку АЦП */
    if (adc_value > adc_max_value) {
        adc_value = adc_max_value;
    }

    /* Лінійне мапування відліків АЦП у тривалість керуючого імпульсу (від 0.5 мс до 2.5 мс):
     * pulse_us = min_pulse + (adc_value / adc_max_value) * (max_pulse - min_pulse)
     */
    uint32_t pulse_range = (uint32_t)(servo->max_pulse_us - servo->min_pulse_us);
    uint16_t calculated_pulse_us = (uint16_t)(servo->min_pulse_us + ((uint32_t)adc_value * pulse_range) / adc_max_value);

    /* Оновлення тривалості імпульсу та регістру порівняння */
    servo_set_pulse_us(servo, calculated_pulse_us);
}

void servo_enable(servo_t *servo, bool enable)
{
    if (servo == NULL) {
        return;
    }

    servo->is_enabled = enable;
    s_hardware_timer_enabled = enable;

    if (enable) {
        update_hardware_compare_register(servo->timer_ticks);
    } else {
        update_hardware_compare_register(0);
    }
}
