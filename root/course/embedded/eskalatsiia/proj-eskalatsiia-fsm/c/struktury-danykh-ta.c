#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_OPTIONS_COUNT     4
#define BREADCRUMB_CAPACITY   64
#define ROI_MAX_BYTES         256

/* Коди апаратних тригерів ескалації */
typedef enum {
    ESCALATION_TRIGGER_NONE = 0,
    ESCALATION_TRIGGER_SCENE_AMBIGUITY,    /* Висока ентропія softmax / близькі класи */
    ESCALATION_TRIGGER_PATH_EXHAUSTED,     /* Усі гілки costmap заблоковані */
    ESCALATION_TRIGGER_BORDERLINE_CRITICAL,/* Критичний об'єкт у діапазоні впевненості [0.4..0.7] */
    ESCALATION_TRIGGER_ODD_EXCURSION       /* Порушення умов середовища (сонце, вітер, EKF) */
} EscalationTrigger;

/* Стан автомата ескалації */
typedef enum {
    FSM_STATE_AUTONOMOUS = 0,
    FSM_STATE_ESCALATION_REQUESTED,
    FSM_STATE_AWAITING_OPERATOR,
    FSM_STATE_APPLYING_OVERRIDE,
    FSM_STATE_FAILSAFE_HOLD,
    FSM_STATE_FAILSAFE_BACKTRACK,
    FSM_STATE_FAILSAFE_SAFE_ABORT
} EscalationState;

/* Дискретна дія, прорахована бортом */
typedef struct {
    uint8_t option_id;              /* 1: Ліворуч, 2: Праворуч, 3: Скасувати, 4: Стоп */
    char description[32];           /* Текстовий підпис для UI оператора */
    float estimated_cost_detour_m;  /* Додаткова дистанція у метрах */
    float risk_score;               /* Оцінка залишкового ризику 0.0 .. 1.0 */
} EscalationOption;

/* Пакет запиту до оператора */
typedef struct {
    uint16_t query_id;              /* Монотонний лічильник запитів */
    uint32_t timestamp_ms;          /* Бортовий час створення */
    uint16_t deadline_ms;           /* Динамічний таймаут на відповідь */
    EscalationTrigger trigger_code; /* Чому виник запит */
    float position_xyz[3];          /* Поточні координати */
    float velocity_xyz[3];          /* Поточний вектор швидкості */
    uint8_t options_count;          /* Кількість варіантів дій */
    EscalationOption options[MAX_OPTIONS_COUNT];
    uint16_t roi_size_bytes;        /* Розмір стисненого фрагмента кадру */
    uint8_t roi_jpeg_buffer[ROI_MAX_BYTES];
} EscalationQueryPacket;

/* Точка історії для реверсу траєкторії */
typedef struct {
    float x, y, z;
    float yaw;
    uint32_t timestamp_ms;
    int8_t rssi_dbm;                /* Рівень радіосигналу в цій точці */
} BreadcrumbPoint;

/* Кільцевий буфер історії руху */
typedef struct {
    BreadcrumbPoint buffer[BREADCRUMB_CAPACITY];
    uint16_t head;
    uint16_t count;
} BreadcrumbTrail;
