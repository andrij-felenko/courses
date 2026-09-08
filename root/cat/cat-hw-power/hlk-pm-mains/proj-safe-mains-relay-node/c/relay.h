#ifndef RELAY_H
#define RELAY_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Стани кінцевого автомата релейного силового каналу
 */
typedef enum {
    RELAY_STATE_OFF = 0,       /* Навантаження знеструмлене, реле розімкнене */
    RELAY_STATE_ON,            /* Навантаження увімкнене, котушка під напругою */
    RELAY_STATE_DEADTIME       /* Захисна пауза (запобігання швидкому повторному пуску) */
} relay_state_t;

/**
 * @brief Структура контролера сиfilterрового реле з захисними таймерами
 */
typedef struct {
    relay_state_t state;            /* Поточний стан автомата */
    bool pending_on;                /* Відкладений запит на увімкнення після завершення паузи */
    uint32_t last_switch_time_ms;   /* Часова мітка останнього перемикання реле */
    uint32_t deadtime_duration_ms;  /* Тривалість мертвого часу (anti-cycling), наприклад 3000-5000 мс */
    
    /* Параметри фільтрації брязкання контактів вхідного вимикача */
    bool last_raw_button;           /* Попередній необроблений стан входу */
    bool debounced_button;          /* Стабільний відфільтрований стан кнопки */
    uint32_t last_debounce_time_ms; /* Часова мітка зміни сирого сигналу */
    uint32_t debounce_delay_ms;     /* Затримка фільтрації брязкання (зазвичай 30-50 мс) */
} relay_controller_t;

/**
 * @brief Ініціалізація структури контролера реле та параметрів безпеки
 * @param ctrl Вказівник на екземпляр контролера
 * @param deadtime_ms Захисна пауза між розмиканням і замиканням контактів (мс)
 * @param debounce_ms Час фільтрації брязкання кнопки (мс)
 */
void relay_init(relay_controller_t *ctrl, uint32_t deadtime_ms, uint32_t debounce_ms);

/**
 * @brief Запит на зміну стану реле (з перевіркою дозволу та мертвого часу)
 * @param ctrl Вказівник на контролер
 * @param target_on true для ввімкнення, false для негайного вимкнення
 * @param now_ms Поточний системний час у мілісекундах
 */
void relay_set_target(relay_controller_t *ctrl, bool target_on, uint32_t now_ms);

/**
 * @brief Перемикання логічного стану навантаження (інверсія)
 */
void relay_toggle(relay_controller_t *ctrl, uint32_t now_ms);

/**
 * @brief Оновлення стану фізичної кнопки з усуненням брязкання
 * @param ctrl Вказівник на контролер
 * @param raw_input Сирий рівень на піні входу (true - замкнуто/натиснуто)
 * @param now_ms Поточний системний час
 */
void relay_update_button(relay_controller_t *ctrl, bool raw_input, uint32_t now_ms);

/**
 * @brief Періодичний диспетчер станів (виклик у головному неблокуючому циклі)
 * @param ctrl Вказівник на контролер
 * @param now_ms Поточний системний час у мілісекундах
 */
void relay_process(relay_controller_t *ctrl, uint32_t now_ms);

/**
 * @brief Перевірка активності сиfilterрового виходу
 */
bool relay_is_active(const relay_controller_t *ctrl);

#endif /* RELAY_H */
