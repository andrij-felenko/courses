#ifndef ALARM_TYPES_H
#define ALARM_TYPES_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define MAX_ALARMS               64
#define MAX_ALARM_TAG_LEN        32
#define MAX_ACTION_TEXT_LEN      64
#define MAX_CONSEQUENCE_LEN      64
#define ALARM_RATE_WINDOW_MS     600000U /* 10 хвилин за стандартом ISA-18.2 */
#define ALARM_FLOOD_THRESHOLD    10U     /* >10 активних тривог за 10 хв = лавина */

/**
 * @brief Стани життєвого циклу тривоги за стандартом ISA-18.2 / IEC 62682.
 */
typedef enum {
    ALARM_STATE_NORMAL = 0,             /* Параметр у межах норми, сигналізація пасивна */
    ALARM_STATE_UNACK_ALARM,            /* Вихід за межі, вимагає уваги та квитування */
    ALARM_STATE_ACK_ALARM,              /* Підтверджена активна тривога (оператор поінформований) */
    ALARM_STATE_RTN_UNACK,              /* Повернуто в норму до підтвердження оператором */
    ALARM_STATE_SHELVED,                /* Тимчасово відкладена оператором на фіксований час */
    ALARM_STATE_SUPPRESSED_BY_DESIGN,   /* Автоматично пригнічена поточною логікою/режимом системи */
    ALARM_STATE_OUT_OF_SERVICE          /* Виведена з експлуатації для ТО чи калібрування */
} AlarmState_t;

/**
 * @brief Пріоритети тривог за стандартом ISA-18.2.
 */
typedef enum {
    ALARM_PRIO_DIAGNOSTIC = 0,          /* Інженерна діагностика, без термінової загрози */
    ALARM_PRIO_LOW,                     /* Низький: час реакції > 30 хв, локальний наслідок */
    ALARM_PRIO_MEDIUM,                  /* Середній: час реакції 5..30 хв, можлива втрата ефективності */
    ALARM_PRIO_HIGH,                    /* Високий: час реакції 1..5 хв, ризик пошкодження обладнання */
    ALARM_PRIO_CRITICAL                 /* Критичний: негайна реакція < 1 хв, загроза життю/катастрофи */
} AlarmPriority_t;

/**
 * @brief Категорія тривоги за природою виникнення.
 */
typedef enum {
    ALARM_CAT_PROCESS = 0,
    ALARM_CAT_SAFETY,
    ALARM_CAT_SENSOR_HEALTH,
    ALARM_CAT_ACTUATOR_FAULT,
    ALARM_CAT_COMMUNICATION
} AlarmCategory_t;

/**
 * @brief Експлуатаційний стан системи для динамічного пригнічення (State-based suppression).
 */
typedef enum {
    SYS_STATE_COLD_BOOT = (1U << 0),
    SYS_STATE_STANDBY   = (1U << 1),
    SYS_STATE_ARMED     = (1U << 2),
    SYS_STATE_MISSION   = (1U << 3),
    SYS_STATE_FAILSAFE  = (1U << 4),
    SYS_STATE_MAINTENANCE = (1U << 5)
} SystemStateMask_t;

/**
 * @brief Конфігурація тривоги (результат раціоналізації сигналізації за ISA-18.2).
 */
typedef struct {
    uint16_t id;
    char tag[MAX_ALARM_TAG_LEN];
    char action_text[MAX_ACTION_TEXT_LEN];
    char consequence[MAX_CONSEQUENCE_LEN];
    AlarmPriority_t priority;
    AlarmCategory_t category;
    uint32_t response_time_limit_ms;
    
    /* Параметри гістерезису та усунення брязкоту */
    float trip_threshold;
    float clear_threshold;
    bool is_high_alarm;                 /* true: тривога якщо value > trip, false: value < trip */
    uint32_t on_delay_ms;               /* Затримка спрацювання для фільтрації коротких піків */
    uint32_t off_delay_ms;              /* Затримка скидання для стабілізації */
    uint16_t chatter_limit;             /* Кількість переходів у вікні до детекції брязкоту */
    uint32_t chatter_window_ms;         /* Часове вікно перевірки брязкоту */

    /* Логіка пригнічення (Suppression by Design & Root-Cause) */
    uint32_t suppression_state_mask;    /* Бітова маска станів системи, де тривога вимкнена */
    int32_t parent_alarm_id;            /* ID батьківської тривоги (-1 якщо первинна) */
} AlarmConfig_t;

/**
 * @brief Динамічний стан тривоги під час виконання (Runtime State).
 */
typedef struct {
    AlarmState_t state;
    AlarmState_t prev_state;
    float current_value;
    bool raw_trip_condition;
    
    /* Часові мітки та таймери затримок */
    uint64_t trip_start_timestamp_ms;
    uint64_t clear_start_timestamp_ms;
    uint64_t state_change_timestamp_ms;
    uint64_t shelved_until_timestamp_ms;

    /* Детекція брязкоту (Chattering Detector) */
    uint16_t transitions_in_window;
    uint64_t first_transition_in_window_ms;
    bool is_chattering;

    /* Прапорці пригнічення */
    bool is_suppressed_by_state;
    bool is_suppressed_by_parent;
} AlarmRuntime_t;

#ifdef __cplusplus
}
#endif

#endif /* ALARM_TYPES_H */
