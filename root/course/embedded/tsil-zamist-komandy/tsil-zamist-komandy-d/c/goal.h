#ifndef GOAL_H
#define GOAL_H

/* Типи диспетчера автономних цілей: сама ціль, стан апарата й шкала пріоритетів.
   Пам'ять статична — жодного malloc у польоті, розмір черги відомий компілятору. */

#include <math.h>
#include <stdbool.h>
#include <stdint.h>

#define GOAL_QUEUE_CAPACITY 8

/* Шкала пріоритетів (та сама, що в таблиці статті). */
#define GOAL_PRIO_EMERGENCY 255u /* аварійне повернення, ухилення від зіткнення */
#define GOAL_PRIO_OPERATOR  150u /* оперативне переривання оператором */
#define GOAL_PRIO_SUBTASK   100u /* динамічні підзадачі, дорозвідка */
#define GOAL_PRIO_MISSION    50u /* основна польотна місія */
#define GOAL_PRIO_SERVICE    10u /* фонові сервісні завдання */

/* Ліки від гойдалки пріоритетів (Goal Thrashing): нова ціль мусить перевищити
   активну щонайменше на цю дельту... */
#define GOAL_PREEMPT_HYSTERESIS 10u
/* ...і щойно активовану ціль не витісняємо перші три секунди. Виняток один —
   аварійний пріоритет 255, його не стримує ні гістерезис, ні таймер. */
#define GOAL_HOLD_DOWN_SEC 3.0f

/* Скільки разів локальний контролер має право попросити обхід, перш ніж
   диспетчер визнає ціль недосяжною. */
#define GOAL_MAX_REPLANS 3

/* У скільки разів дисперсія EKF має перевищити допуск, щоб політ по координатах
   вважався безглуздим і апарат просто тримав точку. */
#define GOAL_EKF_PANIC_FACTOR 4.0f

typedef enum {
    GOAL_WAYPOINT = 0,
    GOAL_SURVEY_AREA,
    GOAL_HOLD_POSITION,
    GOAL_EMERGENCY_RTH
} goal_type_t;

/* Стани життєвого циклу цілі. GOAL_SLOT_FREE — слот у черзі порожній. */
typedef enum {
    GOAL_SLOT_FREE = 0,
    GOAL_PENDING,
    GOAL_VALIDATING,
    GOAL_ACTIVE,
    GOAL_PREEMPTED,
    GOAL_COMPLETED,
    GOAL_ABORTED,
    GOAL_REJECTED
} goal_state_t;

/* Вердикт передстартової перевірки або причина зняття цілі з виконання. */
typedef enum {
    GOAL_CHECK_OK = 0,
    GOAL_CHECK_BAD_REQUEST,      /* ціль сформовано неправильно */
    GOAL_CHECK_EKF_DIVERGED,     /* дисперсія навігаційної оцінки поза допуском */
    GOAL_CHECK_OUTSIDE_GEOFENCE, /* точка за межами дозволеної зони */
    GOAL_CHECK_NO_ENERGY,        /* не вистачить на «дійти й повернутися» */
    GOAL_CHECK_HEADWIND,         /* вітер сильніший за апарат: треку не витримати */
    GOAL_CHECK_TIMEOUT,          /* ціль не встигла у відведений час */
    GOAL_CHECK_PATH_BLOCKED,     /* прохід заблоковано, обходу не знайдено */
    GOAL_CHECK_SENSOR_FAILURE,   /* критична: відмова давачів */
    GOAL_CHECK_MOTOR_FAILURE     /* критична: відмова силової установки */
} goal_check_t;

/* Критична помилка веде ціль в ABORTED, некритична — у REJECTED. */
static inline bool goal_check_is_critical(goal_check_t v)
{
    return v == GOAL_CHECK_SENSOR_FAILURE || v == GOAL_CHECK_MOTOR_FAILURE;
}

/* Світова система координат NED: x — на північ, y — на схід, z — УНИЗ.
   Тому висота над точкою старту це -(z - home.z). */
typedef struct {
    float x;
    float y;
    float z;
} vec3_t;

static inline vec3_t vec3_sub(vec3_t a, vec3_t b)
{
    vec3_t r = { a.x - b.x, a.y - b.y, a.z - b.z };
    return r;
}

static inline float vec3_dot(vec3_t a, vec3_t b)
{
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

static inline float vec3_norm(vec3_t v)
{
    return sqrtf(vec3_dot(v, v));
}

typedef struct {
    uint32_t id;             /* 0 — недійсна ціль; справжні id починаються з 1 */
    goal_type_t type;
    uint8_t priority;
    vec3_t target;           /* цільова точка, метри, NED */
    float acceptance_radius; /* R_tol: радіус зарахування, метри */
    float timeout_sec;       /* 0 — без обмеження часу */
    float cruise_airspeed;   /* повітряна швидкість на маршруті, м/с */
} goal_t;

/* Зріз стану апарата, який диспетчер отримує від оцінювача (EKF) і монітора
   живлення. Диспетчер його лише читає. */
typedef struct {
    vec3_t pos;              /* поточна позиція, метри, NED */
    float battery_voltage;   /* В */
    float battery_energy_wh; /* залишок енергії, Вт·год */
    float cruise_power_w;    /* середнє споживання в крейсері, Вт */
    vec3_t wind;             /* швидкість повітряної маси, м/с, NED */
    float ekf_pos_variance;  /* дисперсія оцінки позиції, м² */
    bool sensors_ok;
    bool motors_ok;
} system_state_t;

#endif /* GOAL_H */
