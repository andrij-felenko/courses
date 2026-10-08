#ifndef ENCODER_H
#define ENCODER_H

#include "stm32_timer_hal.h"
#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Перелік напрямків обертання вала енкодера
 */
typedef enum {
    ENCODER_DIR_STOPPED = 0, /**< Рух відсутній */
    ENCODER_DIR_CW      = 1, /**< За годинниковою стрілкою (Clockwise) */
    ENCODER_DIR_CCW     = -1 /**< Проти годинникової стрілки (Counter-clockwise) */
} encoder_dir_t;

/**
 * @brief Структура конфігурації високорівневого драйвера енкодера
 */
typedef struct {
    uint16_t ppr;                    /**< Роздільна здатність енкодера в імпульсах на оборот (PPR) */
    float gear_ratio;                /**< Передавальне число редуктора (1.0f якщо прямо приєднано) */
    bool invert_direction;           /**< Інвертувати знаки позиції та швидкості */
    stm32_timer_config_t hal_config; /**< Низькорівневі налаштування апаратного таймера STM32 */
} encoder_config_t;

/**
 * @brief Контекст драйвера квадратурного енкодера (об'єкт стану)
 */
typedef struct {
    encoder_config_t config;              /**< Конфігурація енкодера */
    volatile int32_t overflow_count;      /**< Акумулятор 16-бітних переповнень (overflow / underflow) */
    int64_t zero_offset_counts;           /**< Калібрувальний зсув нульової точки (Index Z offset) */
    volatile bool is_calibrated;          /**< Прапорець успішного калібрування за індексом Z */
    int64_t last_velocity_position;       /**< Позиція у відліках на попередньому кроці розрахунку швидкості */
    float angular_velocity_rad_s;         /**< Поточна кутова швидкість (рад/с) */
    float speed_rpm;                      /**< Поточна швидкість у обертах за хвилину (RPM) */
    encoder_dir_t current_direction;      /**< Поточний напрямок руху */
} encoder_t;

/**
 * @brief Ініціалізація драйвера квадратурного енкодера
 * @param encoder Вказівник на структуру стану енкодера
 * @param config Вказівник на параметри конфігурації
 * @return true якщо ініціалізація успішна
 */
bool encoder_init(encoder_t *encoder, const encoder_config_t *config);

/**
 * @brief Обробник переривання оновлення 16-бітного таймера (TIM Update ISR)
 * Викликається при переповненні (overflow) або підповненні (underflow) лічильника.
 * @param encoder Вказівник на структуру енкодера
 */
void encoder_handle_overflow_isr(encoder_t *encoder);

/**
 * @brief Обробник зовнішнього переривання індексного імпульсу Z (EXTI ISR)
 * Здійснює калібрувальну прив'язку абсолютного нуля позиції.
 * @param encoder Вказівник на структуру енкодера
 */
void encoder_handle_index_z_isr(encoder_t *encoder);

/**
 * @brief Атомарне зчитування повної 32/64-бітної позиції енкодера у відліках P_32
 * @param encoder Вказівник на структуру енкодера
 * @return Повна позиція у відліках з урахуванням акумулятора переповнень
 */
int64_t encoder_get_position_raw(encoder_t *encoder);

/**
 * @brief Отримання відкаліброваної позиції з урахуванням нульової точки Z
 * @param encoder Вказівник на структуру енкодера
 * @return Відкалібрована позиція у відліках (P_cal = P_32 - P_zero)
 */
int64_t encoder_get_position_calibrated(encoder_t *encoder);

/**
 * @brief Отримання відкаліброваного кута повороту вихідного вала в радіанах
 * @param encoder Вказівник на структуру енкодера
 * @return Кут у радіанах
 */
float encoder_get_angle_radians(encoder_t *encoder);

/**
 * @brief Примусове скидання поточного положення в нуль (ручне калібрування)
 * @param encoder Вказівник на структуру енкодера
 */
void encoder_reset_zero(encoder_t *encoder);

/**
 * @brief Періодичний розрахунок кутової швидкості (omega та RPM) за квант часу delta_t
 * @param encoder Вказівник на структуру енкодера
 * @param delta_time_sec Проміжок часу delta_t у секундах (наприклад, 0.01f для 10 мс)
 */
void encoder_update_velocity(encoder_t *encoder, float delta_time_sec);

#endif /* ENCODER_H */
