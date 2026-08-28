#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stddef.h>   // offsetof, size_t

typedef enum {
    CAL_IDLE = 0,
    CAL_WARMUP,
    CAL_WAIT_LOW,
    CAL_AVG_LOW,
    CAL_WAIT_HIGH,
    CAL_AVG_HIGH,
    CAL_COMPUTE,
    CAL_SAVE,
    CAL_DONE,
    CAL_ABORT
} cal_state_t;

// Чому саме сюди впала помилка — щоб показати оператору й залогувати.
typedef enum {
    CAL_ERR_NONE = 0,
    CAL_ERR_NOISY,        // розкид відліків на опорі завеликий — давач/контакт шумить
    CAL_ERR_POINTS_CLOSE, // опори надто близько → нахил невизначений (ділення на ~0)
    CAL_ERR_RANGE,        // k або b поза здоровими межами — щось переплутали
    CAL_ERR_STORE         // запис у NVS не підтвердився
} cal_err_t;

typedef struct {
    cal_state_t state;
    cal_err_t   err;

    float    x_low, x_high;   // відомі еталонні величини (задані наперед)

    // накопичувач усереднення (спільний для обох опор)
    int64_t  acc;             // сума сирих кодів (64 біт — щоб не переповнити)
    uint32_t n;               // скільки відліків уже взято
    int32_t  raw_min, raw_max;// межі розкиду на поточній опорі (оцінка шуму)

    int32_t  raw_low, raw_high; // усереднені результати двох опор
    uint32_t t_enter;         // мітка часу входу в стан (для прогріву й таймаутів)

    cal_t    result;          // пораховані k і b (тип cal_t — з теми)
} cal_ctx_t;

static cal_ctx_t cal = { .state = CAL_IDLE };
