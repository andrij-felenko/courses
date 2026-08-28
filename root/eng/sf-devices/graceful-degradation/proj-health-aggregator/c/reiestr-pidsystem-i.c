#include "esp_log.h"
static const char *TAG = "health";

typedef enum { SUB_OK = 0, SUB_DEGRADED = 1, SUB_FAILED = 2 } sub_status_t;
typedef enum { DEV_HEALTHY = 0, DEV_DEGRADED = 1, DEV_SAFE = 2 } dev_mode_t;

typedef struct {
    const char  *name;       // ім'я для логів і телеметрії
    bool         critical;   // критична (true) чи деградовна (false)
    sub_status_t status;     // поточний голос підсистеми
} subsystem_t;

#define MAX_SUBS 16
static subsystem_t s_subs[MAX_SUBS];
static int s_sub_count = 0;

// Реєстрація під час старту: повертає дескриптор-індекс
int health_register(const char *name, bool critical) {
    int id = s_sub_count++;
    s_subs[id] = (subsystem_t){ .name = name, .critical = critical, .status = SUB_OK };
    return id;
}

// Підсистема оновлює свій голос (з будь-якої задачі)
void health_set(int id, sub_status_t st) {
    if (s_subs[id].status != st) {
        ESP_LOGW(TAG, "%s: %d -> %d", s_subs[id].name, s_subs[id].status, st);
    }
    s_subs[id].status = st;
}

// Зведення: найгірший голос із урахуванням ваги вирішує режим
dev_mode_t health_aggregate(void) {
    dev_mode_t mode = DEV_HEALTHY;
    for (int i = 0; i < s_sub_count; i++) {
        subsystem_t *s = &s_subs[i];
        if (s->status == SUB_OK) continue;   // здорова підсистема режим не чіпає

        // Є проблема. Наскільки вона тяжка — вирішує НЕ її різновид, а вага:
        if (s->critical) return DEV_SAFE;    // будь-яка проблема критичної → безпечний стан, далі не дивимось
        if (mode < DEV_DEGRADED) mode = DEV_DEGRADED;  // проблема деградовної → щонайбільше деградований режим
    }
    return mode;
}
