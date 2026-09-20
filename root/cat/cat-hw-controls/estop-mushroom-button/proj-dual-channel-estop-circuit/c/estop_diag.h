#ifndef ESTOP_DIAG_H
#define ESTOP_DIAG_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Стани кінцевого автомата (FSM) неблокувального драйвера аварійної кнопки.
 */
typedef enum {
    ESTOP_STATE_NORMAL = 0,  /**< Нормальний режим: NC-контакти замкнені, контур цілий */
    ESTOP_STATE_DEBOUNCE,    /**< Фільтрація брязкоту контактів (дебаунс) */
    ESTOP_STATE_TRIPPED      /**< Аварійний стан: грибок натиснуто або розрив траси */
} estop_state_t;

/**
 * @brief Події, що повертаються при зміні стану драйвера.
 */
typedef enum {
    ESTOP_EVENT_NONE = 0,    /**< Змін стану не відбулося */
    ESTOP_EVENT_TRIPPED,     /**< Зафіксовано спрацьовування аварійного стопу */
    ESTOP_EVENT_RESET        /**< Аварійний контур відновлено (грибок розблоковано) */
} estop_event_t;

/**
 * @brief Структура контексту драйвера зчитування діагностичного сигналу.
 */
typedef struct {
    estop_state_t state;            /**< Поточний стан кінцевого автомата FSM */
    bool last_raw_level;            /**< Попереднє значення сигналу на вхідному GPIO */
    bool is_tripped;                /**< Прапорець аварійного відключення */
    uint32_t last_state_change_ms;  /**< Часова мітка останньої зміни рівня сигналу */
    uint32_t debounce_delay_ms;     /**< Затримка фільтрації дребезгу контактів в мс */
    uint32_t total_trips_count;     /**< Лічильник кількості спрацьовувань грибка */
    bool (*read_gpio_fn)(void);     /**< Вказівник на функцію зчитування вхідної GPIO-лінії */
} estop_diag_t;

/**
 * @brief Ініціалізація неблокувального драйвера аварійної кнопки.
 * 
 * @param diag Вказівник на структуру контексту драйвера.
 * @param read_gpio_fn Функція для опитування GPIO-входу від оптопари.
 * @param debounce_ms Затримка фільтрації дребезгу (зазвичай 10..50 мс).
 */
void estop_diag_init(estop_diag_t *diag, bool (*read_gpio_fn)(void), uint32_t debounce_ms);

/**
 * @brief Неблокувальне оновлення стану драйвера (викликається у кожному циклі).
 * 
 * @param diag Вказівник на структуру контексту драйвера.
 * @param current_time_ms Поточний системний час у мілісекундах.
 * @return estop_event_t Подія зміни стану драйвера.
 */
estop_event_t estop_diag_update(estop_diag_t *diag, uint32_t current_time_ms);

/**
 * @brief Перевірка, чи перебуває система в аварійному стані.
 * 
 * @param diag Вказівник на структуру контексту драйвера.
 * @return true Якщо контур безпеки розімкнено.
 * @return false Якщо контур у нормі.
 */
bool estop_diag_is_tripped(const estop_diag_t *diag);

#endif /* ESTOP_DIAG_H */
