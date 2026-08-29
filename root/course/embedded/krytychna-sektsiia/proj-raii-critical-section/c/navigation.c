#include "navigation.h"
#include "critical_section.h"

/* Драйвери плати: у прошивці справжні, у тестах підмінені фейками. */
extern bool gnss_read_fix(navigation_data_t *out);
extern void radio_send(const navigation_data_t *fix);

static navigation_data_t g_fix;
static bool              g_has_fix;
static uint32_t          g_updates;

void navigation_init(void)
{
    CRITICAL_BLOCK() {
        g_has_fix = false;
        g_updates = 0U;
    }
}

void navigation_update(const navigation_data_t *fix)
{
    if (fix == NULL) {
        return;
    }
    /*
     * Чотири поля й 64-бітна мітка — це кілька окремих STR. Переривання
     * посеред них віддало б читачеві пакет, зшитий із двох різних фіксів.
     */
    CRITICAL_BLOCK() {
        g_fix     = *fix;
        g_has_fix = true;
        g_updates++;
    }
}

bool navigation_get_snapshot(navigation_data_t *out)
{
    if (out == NULL) {
        return false;
    }

    CRITICAL_BLOCK() {
        if (!g_has_fix) {
            /* Достроковий вихід просто з-під блокування: cleanup поверне
               PRIMASK і на цьому шляху. Саме тут ручний exit і забувають. */
            return false;
        }
        *out = g_fix;
    }
    return true;
}

uint32_t navigation_updates(void)
{
    /* Вирівняне 32-бітне читання на Cortex-M атомарне — секція тут зайва. */
    return g_updates;
}

/* Обробник переривання GNSS: приблизно 100 Гц. */
void GNSS_IRQHandler(void)
{
    navigation_data_t fix;

    /* Кадр міг прийти биті — тоді старий фікс лишається чинним. */
    if (gnss_read_fix(&fix)) {
        navigation_update(&fix);
    }
}

void telemetry_step(void)
{
    navigation_data_t snapshot;

    if (navigation_get_snapshot(&snapshot)) {
        /* Передача — ПОЗА критичною секцією: усередині ми лише копіюємо. */
        radio_send(&snapshot);
    }
}
