#ifndef SERVO_CALIBRATION_H
#define SERVO_CALIBRATION_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file servo_calibration.h
 * @brief Модуль програмного калібрування нейтралі та обробки мертвої зони.
 *
 * Сервоприводи постійного обертання мають зміщення нейтральної точки через розкид
 * параметрів внутрішнього потенціометра або резистивного дільника.
 * Цей модуль надає інструменти для програмної компенсації дрейфу (Trim)
 * та визначення зони нечутливості (Deadband) для надійного зупинення двигуна.
 */

/* Межі калібрувальних параметрів */
#define SERVO_TRIM_MIN_US     (-200)  /**< Мінімально допустимий зсув нейтралі (мкс) */
#define SERVO_TRIM_MAX_US     (200)   /**< Максимально допустимий зсув нейтралі (мкс) */
#define SERVO_DEADBAND_MAX_US (100U)  /**< Максимальна півширина мертвої зони (мкс) */

/**
 * @brief Структура параметрів калібрування нейтралі
 */
typedef struct {
    int16_t trim_offset_us;  /**< Зсув точки нуля в мкс (наприклад, +15 мкс для компенсації апаратного дрейфу) */
    uint16_t deadband_us;    /**< Півширина мертвої зони в мкс навколо нейтралі (наприклад, 20 мкс) */
    uint16_t min_pulse_us;   /**< Калібрований мінімальний імпульс реверсу (за замовчуванням 1000 мкс) */
    uint16_t max_pulse_us;   /**< Калібрований максимальний імпульс прямого ходу (за замовчуванням 2000 мкс) */
} servo_calibration_params_t;

/**
 * @brief Ініціалізація параметрів калібрування значеннями за замовчуванням.
 * @param params Вказівник на структуру параметрів калібрування.
 */
void servo_calibration_init_default(servo_calibration_params_t *params);

/**
 * @brief Встановлення зсуву нейтралі (Trim Offset).
 * @param params Вказівник на структуру калібрування.
 * @param trim_offset_us Зсув нейтралі в мкс (від -200 до +200).
 * @return 0 при успіху, -1 при некоректному значенні.
 */
int servo_calibration_set_trim(servo_calibration_params_t *params, int16_t trim_offset_us);

/**
 * @brief Встановлення ширини мертвої зони (Deadband).
 * @param params Вказівник на структуру калібрування.
 * @param deadband_us Півширина нечутливої зони в мкс (від 0 до 100).
 * @return 0 при успіху, -1 при некоректному значенні.
 */
int servo_calibration_set_deadband(servo_calibration_params_t *params, uint16_t deadband_us);

/**
 * @brief Застосування калібрування: перетворення нормованої швидкості у точну тривалість імпульсу.
 *
 * Алгоритм враховує зсув триммінгу, а також придушує будь-які команди у межах
 * нечутливої зони (Deadband), повертаючи точний сигнал зупину.
 *
 * @param params Вказівник на структуру параметрів калібрування.
 * @param requested_speed_pct Запитувана швидкість (-100.0% .. +100.0%).
 * @return Обчислена тривалість імпульсу в мкс.
 */
uint16_t servo_calibration_apply(const servo_calibration_params_t *params, float requested_speed_pct);

/**
 * @brief Перевірка, чи потрапляє сформований імпульс у мертву зону нейтралі.
 * @param params Вказівник на структуру параметрів калібрування.
 * @param pulse_us Тривалість імпульсу в мкс.
 * @return true якщо імпульс знаходиться в мертвій зоні (двигун зупинений), інакше false.
 */
bool servo_calibration_is_in_deadband(const servo_calibration_params_t *params, uint16_t pulse_us);

#endif /* SERVO_CALIBRATION_H */
