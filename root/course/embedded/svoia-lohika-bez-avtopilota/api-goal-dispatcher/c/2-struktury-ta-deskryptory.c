typedef enum {
    GOAL_TYPE_NONE          = 0,
    GOAL_TYPE_WAYPOINT      = 1, /* Рух у задану точку із заданою швидкістю */
    GOAL_TYPE_HOLD_HEADING  = 2, /* Стабілізація та утримання курсу впродовж часу */
    GOAL_TYPE_STATION_KEEP  = 3, /* Утримання позиції на місці з автопідрулюванням */
    GOAL_TYPE_INSPECT_SCAN  = 4, /* Сканування сектору датчиком або камерою */
    GOAL_TYPE_PAYLOAD_DROP  = 5  /* Активація механізму скидання вантажу */
} GoalType;

typedef enum {
    GOAL_STATUS_PENDING     = 0, /* Ціль очікує своєї черги у кільцевому буфері */
    GOAL_STATUS_ACTIVE      = 1, /* Ціль виконується в поточному стані */
    GOAL_STATUS_SUCCEEDED   = 2, /* Критерій досягнення успішно виконано */
    GOAL_STATUS_TIMEOUT     = 3, /* Перевищено граничний час виконання */
    GOAL_STATUS_ABORTED     = 4  /* Ціль примусово скасовано аварійним скиданням */
} GoalStatus;

typedef struct {
    uint8_t  type;               /* GoalType */
    uint8_t  status;             /* GoalStatus */
    uint16_t goal_id;            /* Унікальний ідентифікатор завдання */
    uint32_t timeout_ms;         /* Максимально допустимий час на виконання */
    uint32_t start_time_ms;      /* Момент старту кроку в мілісекундах */
    union {
        struct {
            int32_t target_x_mm;
            int32_t target_y_mm;
            float   cruise_speed_mps;
            float   acceptance_radius_mm;
        } waypoint;
        struct {
            uint32_t duration_ms;
            float    target_yaw_rad;
        } hold;
        struct {
            uint8_t  pattern_id;
            uint16_t sample_count;
        } scan;
    } args;
    /* Деструктор специфічного очищення при аварії */
    void (*on_abort_cleanup)(void *context);
} Goal;
