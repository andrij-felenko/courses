#include <stdint.h>
#include <stddef.h>

// ── Список підозрюваних. Порядок задає інженер: сусіди в списку — «близькі»
//    підозрювані, щоб розріз навпіл був осмислений. Максимум — розрядність маски.
typedef enum {
    SUS_EXTRA_FILTER = 0,   // зайвий крок обробки сигналу
    SUS_DMA_PATH,           // передача через DMA замість копіювання
    SUS_RADIO,              // радіопередавач
    SUS_EXT_SENSOR,         // зовнішній давач на шині
    SUS_WATCHDOG_FEED,      // годування сторожа з фонової задачі
    SUS_POWER_SAVE,         // перехід у режим зниженого споживання
    SUS_LOG_FLUSH,          // скидання журналу у Flash
    SUS_OTA_CHECK,          // фонова перевірка оновлень
    SUS_COUNT               // скільки всього підозрюваних (не вузол!)
} suspect_t;

// Маска ввімкнених вузлів: біт i виставлено ⟺ вузол i зараз працює.
// 32 біти → до 32 підозрюваних; треба більше — uint64_t або масив слів.
static uint32_t g_enabled_mask = 0;

// Гілка коду / вузол периферії питає СЕБЕ: мені зараз працювати?
static inline int suspect_enabled(suspect_t s) {
    return (g_enabled_mask >> (uint32_t)s) & 1u;
}

// Виставити маску напряму (усі вузли з бітом 1 — увімкнені).
static inline void suspects_set_mask(uint32_t mask) {
    g_enabled_mask = mask;
}
