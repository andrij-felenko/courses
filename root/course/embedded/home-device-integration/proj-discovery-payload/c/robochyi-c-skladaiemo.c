#include <stdio.h>
#include <string.h>
#include <stdbool.h>

// Спільний для всіх сутностей ідентифікатор пристрою — ТОЙ САМИЙ рядок,
// що піде в dev.ids кожної візитівки. Саме він зшиває картку.
#define DEV_ID   "th_livingroom"
#define DEV_NAME "Термостат вітальні"

// Корінь наших робочих топіків (стан/команда/доступність) для цього вузла.
#define BASE "home/livingroom/thermostat"

// Опис однієї сутності: усе, що відрізняє її від інших сутностей вузла.
typedef struct {
    const char *object_id;   // хвіст uniq_id і топіка config — унікальний у вузлі
    const char *component;   // платформа HA в топіку config; тут усі три — "sensor"
    const char *name;        // як підписати рядок у картці
    const char *state_topic; // топік, де тече значення саме цієї сутності
    const char *unit;        // одиниці ("°C", "%") або NULL, якщо без одиниць
} entity_t;

static const entity_t ENTITIES[] = {
    { "temp", "sensor", "Температура", BASE "/temp", "°C" },
    { "mode", "sensor", "Режим",      BASE "/mode", NULL },
    { "batt", "sensor", "Заряд",       BASE "/batt", "%"  },
};
