#ifndef QUAD_ENCODER_TYPES_H
#define QUAD_ENCODER_TYPES_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Події, які може генерувати модуль квадратурного енкодера.
 */
typedef enum {
    ENCODER_EVENT_NONE = 0,      ///< Подій немає
    ENCODER_EVENT_ROTATE_CW,     ///< Обертання за годинниковою стрілкою
    ENCODER_EVENT_ROTATE_CCW,    ///< Обертання проти годинникової стрілки
    BUTTON_EVENT_SHORT_PRESS,    ///< Коротке натискання кнопки
    BUTTON_EVENT_LONG_PRESS      ///< Довге натискання кнопки (утримання)
} quad_encoder_event_t;

/**
 * @brief Контекст автомата станів (FSM) обробки фаз A та B енкодера.
 */
typedef struct {
    uint8_t prev_state;          ///< Попередній 2-бітний стан фаз (A << 1 | B)
    int32_t position;            ///< Атомарний накопичувальний лічильник позиції
    int8_t step_accumulator;     ///< Накопичувач мікрокроків для фіксації кліка (detent)
} quad_encoder_fsm_t;

/**
 * @brief Стан та таймери обробки кнопки із програмним антидребезгом.
 */
typedef struct {
    uint8_t raw_state;           ///< Сирий стан входу (1 - натиснуто, 0 - відпущено)
    uint8_t debounced_state;     ///< Відфільтрований стан кнопки
    uint32_t last_debounce_ms;   ///< Час останньої зміни сирого стану
    uint32_t press_start_ms;     ///< Час початку поточного натискання
    bool long_press_handled;     ///< Прапор, що довге натискання вже опрацьовано
} button_state_t;

/**
 * @brief Головна структура контексту квадратурного енкодера з кнопкою.
 */
typedef struct {
    quad_encoder_fsm_t fsm;      ///< Автомат станів обертання
    button_state_t button;       ///< Модуль кнопки з антидребезгом
    int32_t last_read_position;  ///< Останнє зчитане значення позиції
} quad_encoder_t;

#endif // QUAD_ENCODER_TYPES_H
