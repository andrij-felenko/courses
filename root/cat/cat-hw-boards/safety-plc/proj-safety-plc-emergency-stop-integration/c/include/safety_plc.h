#ifndef SAFETY_PLC_H
#define SAFETY_PLC_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @file safety_plc.h
 * @brief Заголовний файл низькорівневого C-драйвера функціональної безпеки для Safety PLC (SIL2/SIL3).
 * @details Оголошення бітових масок цілісності сигналів, типів апаратних помилок,
 *          детермінованого автомата безпеки та структур каналів F-DI і F-DO.
 */

/* Кількість вхідних (F-DI) та вихідних (F-DO) безпекових каналів у системі */
#define SAFETY_DI_COUNT            2U
#define SAFETY_DO_COUNT            2U

/* Поріг інтегруючого фільтра завад вхідного сигналу (у циклах опитування) */
#define SAFETY_DI_FILTER_THRESHOLD 3U

/* Часові обмеження таймаутів (у мілісекундах) */
#define SAFETY_DISCREPANCY_MAX_MS  50U   /* Ліміт часової розбіжності каналів F-DI */
#define SAFETY_EDM_MAX_DELAY_MS    100U  /* Ліміт затримки зворотного зв'язку EDM F-DO */

/* Фази генератора тестових діагностичних імпульсів (Phase Impulse Sensing) */
#define SAFETY_PHASE_0             0U  /* Фаза 0: T1 = HIGH (24V), T2 = LOW (0V) */
#define SAFETY_PHASE_1             1U  /* Фаза 1: T1 = LOW (0V),  T2 = HIGH (24V) */
#define SAFETY_PHASE_COUNT         2U  /* Загальна кількість фаз у повній діагностичній послідовності */

/**
 * @brief Бітова маска апаратних помилок функціональної безпеки (safety_fault_t).
 */
typedef enum {
    SAFETY_FAULT_NONE            = 0x0000U, /* Помилок не виявлено */
    SAFETY_FAULT_SHORT_VCC       = 0x0001U, /* Коротке замикання лінії F-DI на VCC (+24V) */
    SAFETY_FAULT_SHORT_GND       = 0x0002U, /* Коротке замикання лінії F-DI на GND (0V) */
    SAFETY_FAULT_CROSS_CHANNEL   = 0x0004U, /* Перехресне коротке замикання між тестовими каналами/лініями */
    SAFETY_FAULT_DISCREPANCY     = 0x0008U, /* Часова розбіжність сигналів каналу A і B (1oo2 logic) */
    SAFETY_FAULT_DO_HS_DRIVER    = 0x0010U, /* Невідповідність ключа High-Side виходу F-DO */
    SAFETY_FAULT_DO_LS_DRIVER    = 0x0020U, /* Невідповідність ключа Low-Side виходу F-DO */
    SAFETY_FAULT_DO_FEEDBACK     = 0x0040U, /* Несправність зворотного зв'язку EDM (зварено contacts/реле) */
    SAFETY_FAULT_SYSTEM_FAILSAFE = 0x0080U  /* Примусовий блокуючий безпечний стан */
} safety_fault_t;

/**
 * @brief Стани детермінованого автомата функціональної безпеки (safety_state_t).
 */
typedef enum {
    SAFETY_STATE_INIT     = 0, /* Ініціалізація та первинне самотестування (POST) */
    SAFETY_STATE_RUN      = 1, /* Нормальний детермінований робочий режим */
    SAFETY_STATE_FAILSAFE = 2  /* Апаратний безпечний стан (усі силові виходи знеструмлені) */
} safety_state_t;

/**
 * @brief Структура двоканального безпекового входу F-DI (f_di_channel_t).
 */
typedef struct {
    uint8_t channel_id;              /* Номер каналу F-DI */
    
    /* Сирі фізичні рівні входів */
    bool raw_a;                      /* Сирий сигнал каналу A (опитується під тестовим виходом T1) */
    bool raw_b;                      /* Сирий сигнал каналу B (опитується під тестовим виходом T2) */
    
    /* Інтегруючі фільтри дебаунсингу завад */
    uint8_t filter_cnt_a;            /* Лічильник фільтраційного накопичувача A */
    uint8_t filter_cnt_b;            /* Лічильник фільтраційного накопичувача B */
    bool filtered_a;                 /* Відфільтроване логічне значення каналу A */
    bool filtered_b;                 /* Відфільтроване логічне значення каналу B */
    
    /* Маски накопичених фазових відгуків (Phase Impulse Sensing) */
    uint8_t history_a;               /* Зафіксовані біти відгуку Ch A за фазами [bit0: P0, bit1: P1] */
    uint8_t history_b;               /* Зафіксовані біти відгуку Ch B за фазами [bit0: P0, bit1: P1] */
    
    /* Контроль часової розбіжності каналів A/B (1oo2 logic) */
    uint32_t discrepancy_timer_ms;   /* Поточний лічильник тривалості розбіжності (мс) */
    uint32_t max_discrepancy_ms;     /* Допустимий таймаут розбіжності (мс) */
    
    /* Фінальний розрахований безпековий стан входу */
    bool safe_value;                 /* Валідований логічний стан (true = безпечно / кнопочний контакт замкнено) */
    uint16_t faults;                 /* Бітова маска апаратних помилок каналу F-DI */
} f_di_channel_t;

/**
 * @brief Структура двоканального безпекового виходу F-DO (f_do_channel_t).
 */
typedef struct {
    uint8_t channel_id;              /* Номер каналу F-DO */
    bool command;                    /* Логічна команда на активацію виходу (true = увімкнути) */
    
    /* Силові ключі з подвійним розмиканням (High-Side / Low-Side) */
    bool hs_output;                  /* Стан High-Side ключа (підтяжка силового плюса +24V) */
    bool ls_output;                  /* Стан Low-Side ключа (підтяжка силового мінуса GND) */
    
    /* Зворотний зв'язок моніторингу стану ключів та виконавчого контактора */
    bool hs_readback;                /* Фізичний зворотний зв'язок напруги High-Side ключа */
    bool ls_readback;                /* Фізичний зворотний зв'язок напруги Low-Side ключа */
    bool edm_feedback;               /* Сигнал EDM (External Device Monitoring) від NC-контактів реле */
    
    /* Таймер моніторингу часу спрацьовування EDM */
    uint32_t edm_timer_ms;           /* Лічильник тривалості затримки EDM (мс) */
    uint32_t max_edm_delay_ms;       /* Максимально дозволений час затримки перемикання EDM (мс) */
    
    uint16_t faults;                 /* Бітова маска помилок каналу F-DO */
} f_do_channel_t;

/**
 * @brief Головна контекстна структура контролера Safety PLC.
 */
typedef struct {
    safety_state_t state;            /* Стан детермінованого автомата безпеки */
    uint16_t global_faults;          /* Глобальний бітовий регістр помилок системи */
    
    /* Апаратний генератор фазових тестових імпульсів T1 / T2 */
    uint8_t current_phase;           /* Поточна фаза імпульсного зондування (0 або 1) */
    bool t1_generator;               /* Фізичний вихід тестової лінії T1 */
    bool t2_generator;               /* Фізичний вихід тестової лінії T2 */
    
    /* Масиви каналів F-DI та F-DO */
    f_di_channel_t di[SAFETY_DI_COUNT];
    f_do_channel_t do_out[SAFETY_DO_COUNT];
    
    uint32_t cycle_count;            /* Лічильник виконаних циклів контролера */
} safety_plc_t;

/* --- Прототипи функцій драйвера Safety PLC --- */

/**
 * @brief Ініціалізація підсистеми Safety PLC, скидання внутрішнього стану та налаштування каналів.
 * @param plc Вказівник на контекстну структуру Safety PLC.
 */
void safety_plc_init(safety_plc_t *plc);

/**
 * @brief Оновлення фізичних станів генераторів фазових тестових імпульсів T1 та T2.
 * @param plc Вказівник на контекстну структуру Safety PLC.
 */
void safety_plc_update_test_pulses(safety_plc_t *plc);

/**
 * @brief Зчитування та збереження сирих апаратних рівнів входів F-DI.
 * @param plc Вказівник на контекстну структуру Safety PLC.
 * @param di_idx Індекс вхідного каналу F-DI.
 * @param raw_a Фізичний рівень сигналу лінії A.
 * @param raw_b Фізичний рівень сигналу лінії B.
 */
void safety_plc_read_f_di(safety_plc_t *plc, uint8_t di_idx, bool raw_a, bool raw_b);

/**
 * @brief Виконання фазового зондування, дебаунсингу, оцінки цілісності та контролю розбіжності F-DI.
 * @param plc Вказівник на контекстну структуру Safety PLC.
 * @param di_idx Індекс вхідного каналу F-DI.
 * @param delta_time_ms Час, що минув з попереднього кроку обробки (в мс).
 */
void safety_plc_evaluate_f_di_diagnostics(safety_plc_t *plc, uint8_t di_idx, uint32_t delta_time_ms);

/**
 * @brief Оновлення силових ключів F-DO, контроль зворотного зв'язку High/Low-Side та EDM.
 * @param plc Вказівник на контекстну структуру Safety PLC.
 * @param do_idx Індекс вихідного каналу F-DO.
 * @param command Логічна команда на увімкнення/вимкнення.
 * @param hs_fb Зворотний зв'язок High-Side ключа.
 * @param ls_fb Зворотний зв'язок Low-Side ключа.
 * @param edm_fb Сигнал зворотного зв'язку контактора EDM.
 * @param delta_time_ms Час, що минув з попереднього кроку (в мс).
 */
void safety_plc_update_f_do(safety_plc_t *plc, uint8_t do_idx, bool command, bool hs_fb, bool ls_fb, bool edm_fb, uint32_t delta_time_ms);

/**
 * @brief Головний детермінований крок обробки автомата безпеки та генератора фаз.
 * @param plc Вказівник на контекстну структуру Safety PLC.
 * @param delta_time_ms Крок часу виконання (в мс).
 */
void safety_plc_process_step(safety_plc_t *plc, uint32_t delta_time_ms);

/**
 * @brief Негайний примусовий перехід у безпечний стан Fail-Safe зі знеструмленням усіх виходів.
 * @param plc Вказівник на контекстну структуру Safety PLC.
 * @param fault_reason Бітова маска помилки, що викликала перехід.
 */
void safety_plc_force_failsafe(safety_plc_t *plc, uint16_t fault_reason);

/**
 * @brief Безпечне скидання помилок та повернення в робочий режим RUN після усунення несправностей.
 * @param plc Вказівник на контекстну структуру Safety PLC.
 * @param reset_button_pressed Натискання фізичної кнопки RESET.
 * @return true Якщо скидання виконано успішно, false якщо відхилено через активні помилки.
 */
bool safety_plc_reset_faults(safety_plc_t *plc, bool reset_button_pressed);

/**
 * @brief Повертає текстовий рядок опису апаратних помилок безпеки.
 * @param fault_code Бітова маска помилок.
 * @return Текстовий опис українською мовою.
 */
const char* safety_fault_to_string(uint16_t fault_code);

/**
 * @brief Повертає текстовий рядок почного стану автомата безпеки.
 * @param state Стан автомата.
 * @return Текстовий опис українською мовою.
 */
const char* safety_state_to_string(safety_state_t state);

#endif /* SAFETY_PLC_H */
