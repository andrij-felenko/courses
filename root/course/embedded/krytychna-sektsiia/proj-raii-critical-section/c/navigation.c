#include "navigation.h"
#include "critical_section.h"

static navigation_data_t g_fix;
static bool              g_has_fix;

/*
 * volatile саме тут, а не на всій трійці: g_fix і g_has_fix читаються лише
 * всередині секцій, а бар'єр на вході й виході й так змушує компілятор
 * перечитати їх із пам'яті. Лічильник же віддається назовні БЕЗ секції —
 * без volatile компілятор мав би право закешувати його в регістрі й крутити
 * фоновий цикл на значенні, яке обробник переривання давно змінив.
 */
static volatile uint32_t g_updates;

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
        g_updates++;   /* читання-зміна-запис: атомарний лише під маскою */
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
    /*
     * Секція тут зайва: вирівняне 32-бітне читання на Cortex-M і так
     * неподільне, а від застарілого значення в регістрі рятує volatile.
     */
    return g_updates;
}

/* Обробник переривання GNSS: приблизно 100 Гц. */
void GNSS_IRQHandler(void)
{
    navigation_data_t fix;

    /* Кадр міг прийти битий — тоді старий фікс лишається чинним. */
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
