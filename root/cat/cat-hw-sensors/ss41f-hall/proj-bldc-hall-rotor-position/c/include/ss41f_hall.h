#ifndef SS41F_HALL_H
#define SS41F_HALL_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Заборонені 3-бітові комбінації стану давачів Холла.
 * 
 * Комбінація 000 (0b000) означає відсутність сигналу від усіх трьох давачів
 * (обрив лінії живлення VCC, маси GND або усіх трьох сигнальних ліній з підтяжкою до GND).
 * 
 * Комбінація 111 (0b111) означає високий рівень на всіх трьох лініях
 * (коротке замикання на VCC або обрив усіх ліній з вхідною підтяжкою до VCC).
 */
#define HALL_CODE_INVALID_LOW   0b000U
#define HALL_CODE_INVALID_HIGH  0b111U

/**
 * @brief Перерахований тип електричних секторів ротора BLDC двигуна.
 * 
 * Для трьох цифрових біполярних давачів SS41F, розміщених під кутом 120 град.,
 * один електричний оборот 360 град. ділиться на 6 секторів по 60 град.
 */
typedef enum {
    HALL_SECTOR_INVALID = 0, /**< Некоректний або невизначений сектор */
    HALL_SECTOR_1       = 1, /**< Сектор 1 (60 град) */
    HALL_SECTOR_2       = 2, /**< Сектор 2 (120 град) */
    HALL_SECTOR_3       = 3, /**< Сектор 3 (180 град) */
    HALL_SECTOR_4       = 4, /**< Сектор 4 (240 град) */
    HALL_SECTOR_5       = 5, /**< Сектор 5 (300 град) */
    HALL_SECTOR_6       = 6  /**< Сектор 6 (360 град) */
} hall_sector_t;

/**
 * @brief Напрямок обертання ротора.
 */
typedef enum {
    HALL_DIR_UNKNOWN = 0, /**< Напрямок ще не визначений (початковий стан) */
    HALL_DIR_CW      = 1, /**< За годинниковою стрілкою (Clockwise: 1->2->3->4->5->6->1) */
    HALL_DIR_CCW     = 2  /**< Проти годинникової стрілки (Counter-Clockwise: 1->6->5->4->3->2->1) */
} hall_dir_t;

/**
 * @brief Перерахований тип апаратних та логічних помилок давачів Холла.
 */
typedef enum {
    HALL_ERR_NONE               = 0, /**< Помилки відсутні */
    HALL_ERR_INVALID_CODE_000   = 1, /**< Виявлено заборонений код 000 (обрив VCC/GND/сигналів) */
    HALL_ERR_INVALID_CODE_111   = 2, /**< Виявлено заборонений код 111 (коротке на VCC або обрив з pull-up) */
    HALL_ERR_ILLEGAL_TRANSITION = 3  /**< Неприпустимий перехід між секторами (пропуск сектора/брязкіт) */
} hall_error_t;

/**
 * @brief Структура телеметрії та поточного стану системи давачів Холла.
 */
typedef struct {
    uint8_t         raw_code;          /**< Поточний 3-бітовий код стан-триплета (Bit 2: A, Bit 1: B, Bit 0: C) */
    hall_sector_t   current_sector;    /**< Поточний електричний сектор (1..6) */
    hall_sector_t   previous_sector;   /**< Попередній електричний сектор */
    hall_dir_t      direction;         /**< Поточний визначений напрямок обертання */
    uint32_t        transition_count;  /**< Загальна кількість успішних фазових переходів */
    uint32_t        error_count;       /**< Загальна кількість виявлених помилок */
    hall_error_t    last_error;        /**< Код останньої зафіксованої помилки */
} hall_telemetry_t;

/**
 * @brief Таблиця декодування (LUT) 3-бітового коду давачів у номер сектора.
 * 
 * Індексом є 3-бітове число (0..7), сформоване як (A << 2) | (B << 1) | C.
 */
extern const hall_sector_t hall_lut[8];

/**
 * @brief Типи зворотних викликів (callbacks) для подій драйвера.
 */
typedef void (*hall_sector_change_cb_t)(hall_sector_t new_sector, hall_sector_t old_sector, uint8_t raw_code);
typedef void (*hall_error_cb_t)(hall_error_t error, uint8_t raw_code);

/**
 * @brief Ініціалізація драйвера давачів Холла SS41F.
 */
void hall_init(void);

/**
 * @brief Декодування 3-бітового коду у номер електричного сектора за LUT.
 * 
 * @param raw_code 3-бітовий код (0..7)
 * @return hall_sector_t Номер сектора (1..6) або HALL_SECTOR_INVALID
 */
hall_sector_t hall_decode_code(uint8_t raw_code);

/**
 * @brief Перевірка припустимості переходу між двома секторами.
 * 
 * @param prev Попередній сектор
 * @param curr Поточний сектор
 * @return true Якщо перехід відповідає нормальному обертанню ротора
 * @return false Якщо перехід скачкоподібний або містить некоректний сектор
 */
bool hall_is_valid_transition(hall_sector_t prev, hall_sector_t curr);

/**
 * @brief Обробка нового 3-бітового стану давачів (викликається з ISR або драйвера EXTI).
 * 
 * @param raw_code Новий 3-бітовий код стану (0..7)
 * @return hall_error_t Результат обробки (HALL_ERR_NONE або код помилки)
 */
hall_error_t hall_process_state(uint8_t raw_code);

/**
 * @brief Реєстрація зворотного виклику для зміни сектора.
 * 
 * @param cb Вказівник на функцію обробки зміни сектора
 */
void hall_register_sector_callback(hall_sector_change_cb_t cb);

/**
 * @brief Реєстрація зворотного виклику для обробки помилок.
 * 
 * @param cb Вказівник на функцію обробки помилок
 */
void hall_register_error_callback(hall_error_cb_t cb);

/**
 * @brief Отримання поточної телеметрії драйвера давачів.
 * 
 * @param telemetry Вказівник на структуру для копіювання даних
 */
void hall_get_telemetry(hall_telemetry_t *telemetry);

/**
 * @brief Скидання лічильників телеметрії та помилок.
 */
void hall_reset_telemetry(void);

#ifdef __cplusplus
}
#endif

#endif /* SS41F_HALL_H */
