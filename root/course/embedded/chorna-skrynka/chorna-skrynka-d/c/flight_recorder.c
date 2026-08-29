#include "flight_recorder.h"
#include "crc16.h"

/* Сховище живе поза .data і .bss, тож стартовий код (crt0 / Reset_Handler)
 * його не занулює й не переініціалізовує. Секцію .noinit мусить оголосити
 * скрипт компонувальника — без цього масив мовчки поїде в .bss і кожне
 * скидання стиратиме передісторію. */
__attribute__((section(".noinit"))) static BlackBoxStorage_t g_box;

/* --- критична секція --------------------------------------------------------
 * Зберігаємо PRIMASK і відновлюємо його, а не вмикаємо переривання наосліп:
 * реєстратор кличуть із переривання, де вони вже могли бути заборонені, і
 * сліпе cpsie i там відкрило б вкладене переривання посеред запису кадру.
 */
#if defined(__ARM_ARCH)
static inline uint32_t irq_lock(void)
{
    uint32_t primask;
    __asm volatile("mrs %0, primask" : "=r"(primask));
    __asm volatile("cpsid i" ::: "memory");
    return primask;
}

static inline void irq_unlock(uint32_t primask)
{
    if (primask == 0u) {
        __asm volatile("cpsie i" ::: "memory");
    }
}
#else
/* Хостова збірка (прогін декодера й перевірок на ПК): переривань немає,
 * але бар'єр компілятора лишаємо, щоб порядок звернень не перекроїли. */
static inline uint32_t irq_lock(void)
{
    __asm volatile("" ::: "memory");
    return 0u;
}

static inline void irq_unlock(uint32_t primask)
{
    (void)primask;
    __asm volatile("" ::: "memory");
}
#endif

/* --- заголовок -------------------------------------------------------------- */

static uint16_t header_checksum(void)
{
    return crc16_ccitt(&g_box, BLACKBOX_HEAD_CRC_BYTES, 0xFFFFu);
}

static void seal_header(void)
{
    g_box.header_crc = header_checksum();
}

static bool header_intact(void)
{
    return g_box.magic == BLACKBOX_MAGIC
        && g_box.schema == BLACKBOX_SCHEMA
        && g_box.capacity == BLACKBOX_CAPACITY
        && g_box.header_crc == header_checksum()
        && g_box.head < BLACKBOX_CAPACITY
        && g_box.post_trigger_left <= BLACKBOX_POST_TRIGGER;
}

/* --- запис кадру ------------------------------------------------------------ */

static uint16_t frame_checksum(const BlackBoxEvent_t *ev)
{
    return crc16_ccitt(ev, BLACKBOX_FRAME_CRC_BYTES, 0xFFFFu);
}

/* Викликається лише з-під irq_lock(). */
static void store_locked(SubsystemId_t subsys, EventId_t evt, uint16_t fsm_state,
                         const void *payload, size_t len)
{
    BlackBoxEvent_t *slot = &g_box.events[g_box.head];

    g_box.head = (g_box.head + 1u) % BLACKBOX_CAPACITY;
    g_box.sequence++; /* переповнення за 2^32 записів свідомо ігноруємо:
                       * при 20 подіях/с це 6.8 року неперервної роботи */

    slot->timestamp_ms = flight_recorder_uptime_ms();
    slot->subsystem_id = (uint8_t)subsys;
    slot->event_id = (uint8_t)evt;
    slot->fsm_state = fsm_state;

    memset(slot->payload, 0, sizeof slot->payload);
    if (payload != NULL && len != 0u) {
        const size_t copy = (len > sizeof slot->payload) ? sizeof slot->payload : len;
        memcpy(slot->payload, payload, copy);
    }

    slot->crc16 = frame_checksum(slot);
}

void flight_recorder_log(SubsystemId_t subsys, EventId_t evt, uint16_t fsm_state,
                         const void *payload, size_t len)
{
    const uint32_t saved = irq_lock();

    if (g_box.frozen == 0u) {
        store_locked(subsys, evt, fsm_state, payload, len);

        /* Пост-тригерне вікно: після аварії дописуємо ще кілька кадрів —
         * саме вони показують, ЯК система звалилася, — і замикаємо кільце. */
        if (g_box.post_trigger_left != 0u) {
            g_box.post_trigger_left--;
            if (g_box.post_trigger_left == 0u) {
                g_box.frozen = 1u;
            }
        }
    }

    irq_unlock(saved);
}

void flight_recorder_state(SubsystemId_t subsys, uint8_t previous, uint8_t next,
                           uint8_t hw_flags, uint8_t trigger, uint32_t dwell_ms)
{
    const BlackBoxTransition_t body = {
        .previous = previous,
        .trigger = trigger,
        .dwell_ms = dwell_ms,
    };
    const uint16_t fsm = (uint16_t)(((uint16_t)hw_flags << 8) | (uint16_t)next);

    flight_recorder_log(subsys, EVT_STATE_CHANGE, fsm, &body, sizeof body);
}

void flight_recorder_health(SubsystemId_t subsys, EventId_t evt, uint16_t fsm_state,
                            uint16_t vbat_mv, uint16_t load_ma, uint16_t code)
{
    const BlackBoxHealth_t body = {
        .vbat_mv = vbat_mv,
        .load_ma = load_ma,
        .code = code,
    };
    flight_recorder_log(subsys, evt, fsm_state, &body, sizeof body);
}

void flight_recorder_link(SubsystemId_t subsys, uint16_t lost_packets,
                          int16_t rssi_dbm, int16_t snr_cb)
{
    const BlackBoxLink_t body = {
        .lost_packets = lost_packets,
        .rssi_dbm = rssi_dbm,
        .snr_cb = snr_cb,
    };
    flight_recorder_log(subsys, EVT_LINK_STATS, 0u, &body, sizeof body);
}

void flight_recorder_panic(uint8_t reason, uint32_t pc, uint16_t fault_status)
{
    const uint32_t saved = irq_lock();

    /* Якщо кільце вже заморожене, це або друга аварія поспіль, або звіт про
     * попередню ще не забрали. Перетирати старший доказ новішим не можна. */
    if (g_box.frozen == 0u) {
        const BlackBoxFault_t body = { .pc = pc, .status = fault_status };

        store_locked(SUBSYS_CORE, EVT_CRASH_PANIC, (uint16_t)reason, &body, sizeof body);
        g_box.crash_count++;

#if BLACKBOX_POST_TRIGGER > 0
        g_box.post_trigger_left = (uint8_t)BLACKBOX_POST_TRIGGER;
#else
        g_box.frozen = 1u;
#endif
        seal_header(); /* crash_count входить у накриту сумою частину */
    }

    irq_unlock(saved);
}

void flight_recorder_freeze(void)
{
    const uint32_t saved = irq_lock();
    g_box.frozen = 1u;
    g_box.post_trigger_left = 0u;
    irq_unlock(saved);
}

void flight_recorder_release(void)
{
    const uint32_t saved = irq_lock();
    g_box.frozen = 0u;
    g_box.post_trigger_left = 0u;
    irq_unlock(saved);
}

/* --- старт ------------------------------------------------------------------ */

static void cold_start(void)
{
    memset(&g_box, 0, sizeof g_box);
    g_box.magic = BLACKBOX_MAGIC;
    g_box.schema = BLACKBOX_SCHEMA;
    g_box.capacity = BLACKBOX_CAPACITY;
    g_box.boot_count = 1u;
    seal_header();
}

void flight_recorder_init(uint8_t reset_cause)
{
    if (header_intact()) {
        /* Теплий старт: живлення SRAM не зникало, передісторія на місці. */
        g_box.boot_count++;
        seal_header();
    } else {
        cold_start();
    }

    /* Заморожене кільце НЕ розморожуємо: там лежить аварійний знімок, і його
     * має спершу забрати прошивка (звіт у радіоканал або скидання у FRAM),
     * а вже потім покликати flight_recorder_release(). */
    if (g_box.frozen == 0u) {
        const BlackBoxHealth_t body = {
            .vbat_mv = 0u,
            .load_ma = 0u,
            .code = (uint16_t)reset_cause, /* вміст RCC_CSR / RSTSRC */
        };
        flight_recorder_log(SUBSYS_CORE, EVT_BOOT, (uint16_t)g_box.boot_count,
                            &body, sizeof body);
    }
}

/* --- читання ---------------------------------------------------------------- */

bool flight_recorder_history_valid(void)
{
    return header_intact() && g_box.sequence != 0u;
}

bool flight_recorder_crash_pending(void)
{
    return header_intact() && g_box.frozen != 0u && g_box.crash_count != 0u;
}

size_t flight_recorder_replay(BlackBoxVisitor_t visit, void *ctx)
{
    if (visit == NULL || !flight_recorder_history_valid()) {
        return 0u;
    }

    const bool wrapped = (g_box.sequence >= BLACKBOX_CAPACITY);
    const size_t total = wrapped ? (size_t)BLACKBOX_CAPACITY : (size_t)g_box.sequence;
    const size_t start = wrapped ? (size_t)g_box.head : 0u;

    for (size_t i = 0u; i < total; ++i) {
        const BlackBoxEvent_t *ev = &g_box.events[(start + i) % BLACKBOX_CAPACITY];
        visit(ev, ev->crc16 == frame_checksum(ev), ctx);
    }
    return total;
}

const BlackBoxStorage_t *flight_recorder_storage(void)
{
    return &g_box;
}
