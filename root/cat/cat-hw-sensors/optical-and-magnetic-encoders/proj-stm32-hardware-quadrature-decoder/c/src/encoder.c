#include "../include/encoder.h"
#include <stddef.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846f
#endif

bool encoder_init(encoder_t *encoder, const encoder_config_t *config) {
    if (encoder == NULL || config == NULL || config->ppr == 0) {
        return false;
    }

    encoder->config = *config;
    encoder->overflow_count = 0;
    encoder->zero_offset_counts = 0;
    encoder->is_calibrated = false;
    encoder->last_velocity_position = 0;
    encoder->angular_velocity_rad_s = 0.0f;
    encoder->speed_rpm = 0.0f;
    encoder->current_direction = ENCODER_DIR_STOPPED;

    /* Ініціалізація апаратних регістрів таймера STM32 */
    if (!stm32_timer_encoder_init(&config->hal_config)) {
        return false;
    }

    /* Налаштування переривання Z, якщо вказано лінію EXTI */
    if (config->hal_config.exti_line != 0U) {
        stm32_timer_exti_z_init(&config->hal_config);
    }

    return true;
}

void encoder_handle_overflow_isr(encoder_t *encoder) {
    if (encoder == NULL || encoder->config.hal_config.timer == NULL) {
        return;
    }

    TIM_TypeDef *timer = encoder->config.hal_config.timer;

    /* Перевіряємо, чи переривання викликано оновленням лічильника (UIF) */
    if (stm32_timer_check_and_clear_update_flag(timer)) {
        /* Напрямок підрахунку в момент переповнення визначено в регістрі CR1_DIR:
           - Якщо DIR = 0: рахували вгору -> відбулося переповнення (overflow 65535 -> 0)
           - Якщо DIR = 1: рахували вниз -> відбулося підповнення (underflow 0 -> 65535) */
        if (stm32_timer_get_direction_down(timer)) {
            encoder->overflow_count--;
        } else {
            encoder->overflow_count++;
        }
    }
}

void encoder_handle_index_z_isr(encoder_t *encoder) {
    if (encoder == NULL) {
        return;
    }

    /* Зчитуємо поточну абсолютну позицію у відліках для фіксації нульової точки Z */
    int64_t current_raw = encoder_get_position_raw(encoder);
    encoder->zero_offset_counts = current_raw;
    encoder->is_calibrated = true;
}

int64_t encoder_get_position_raw(encoder_t *encoder) {
    if (encoder == NULL || encoder->config.hal_config.timer == NULL) {
        return 0;
    }

    TIM_TypeDef *timer = encoder->config.hal_config.timer;

    int32_t ovf1, ovf2;
    uint16_t cnt;

    /* Захист від гонки даних при зчитуванні лічильника під час переривання:
       Повторюємо зчитування, доки значення overflow_count до і після читання CNT не збіжуться */
    do {
        ovf1 = encoder->overflow_count;
        cnt = stm32_timer_get_counter(timer);
        ovf2 = encoder->overflow_count;
    } while (ovf1 != ovf2);

    /* Перевірка граничного випадку: якщо CNT оновився, але обробник ISR ще не встиг виконатися */
    if ((timer->SR & TIM_SR_UIF) != 0U) {
        cnt = stm32_timer_get_counter(timer);
        if (stm32_timer_get_direction_down(timer)) {
            if (cnt > 32768U) { /* Підповнення відбулося, лічильник стрибнув до 65535 */
                ovf1--;
            }
        } else {
            if (cnt < 32768U) { /* Переповнення відбулося, лічильник скинувся до 0 */
                ovf1++;
            }
        }
    }

    /* Обчислення повної розширеної позиції: P_32 = (overflow_count * 65536) + TIMx->CNT */
    int64_t raw_counts = ((int64_t)ovf1 * 65536LL) + (int64_t)cnt;

    if (encoder->config.invert_direction) {
        raw_counts = -raw_counts;
    }

    return raw_counts;
}

int64_t encoder_get_position_calibrated(encoder_t *encoder) {
    if (encoder == NULL) {
        return 0;
    }

    int64_t raw = encoder_get_position_raw(encoder);
    return raw - encoder->zero_offset_counts;
}

float encoder_get_angle_radians(encoder_t *encoder) {
    if (encoder == NULL || encoder->config.ppr == 0) {
        return 0.0f;
    }

    int64_t calibrated_counts = encoder_get_position_calibrated(encoder);

    /* Сукупна кількість відліків на 1 оборот у режимі x4 з урахуванням редуктора:
       Total_Counts_Per_Rev = 4 * PPR * gear_ratio */
    float total_cpr = 4.0f * (float)encoder->config.ppr * encoder->config.gear_ratio;

    /* Обчислення кута: theta = (2 * PI * counts) / total_cpr */
    return (2.0f * (float)M_PI * (float)calibrated_counts) / total_cpr;
}

void encoder_reset_zero(encoder_t *encoder) {
    if (encoder == NULL) {
        return;
    }

    encoder->zero_offset_counts = encoder_get_position_raw(encoder);
    encoder->is_calibrated = true;
}

void encoder_update_velocity(encoder_t *encoder, float delta_time_sec) {
    if (encoder == NULL || delta_time_sec <= 0.00001f || encoder->config.ppr == 0) {
        return;
    }

    int64_t current_position = encoder_get_position_raw(encoder);
    int64_t delta_counts = current_position - encoder->last_velocity_position;
    encoder->last_velocity_position = current_position;

    /* Визначення напрямку руху */
    if (delta_counts > 0) {
        encoder->current_direction = ENCODER_DIR_CW;
    } else if (delta_counts < 0) {
        encoder->current_direction = ENCODER_DIR_CCW;
    } else {
        encoder->current_direction = ENCODER_DIR_STOPPED;
    }

    /* Відліки на один оборот вихідного вала */
    float total_cpr = 4.0f * (float)encoder->config.ppr * encoder->config.gear_ratio;

    /* Кутова швидкість w = (2 * PI * delta_N) / (total_cpr * delta_t) [рад/с] */
    float rad_per_sec = (2.0f * (float)M_PI * (float)delta_counts) / (total_cpr * delta_time_sec);
    encoder->angular_velocity_rad_s = rad_per_sec;

    /* Швидкість у RPM: RPM = (w * 60) / (2 * PI) = (delta_N * 60) / (total_cpr * delta_t) */
    encoder->speed_rpm = (rad_per_sec * 60.0f) / (2.0f * (float)M_PI);
}
