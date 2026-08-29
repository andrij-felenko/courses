#include "crash_log.h"

#include "mcu.h"

#include <string.h>

#define CRASH_LOG_MAGIC 0x50524F44UL /* 'PROD' */

/* Секція .noinit НЕ обнуляється стартовим кодом: після теплого рестарту
 * (сторож, HardFault, програмний reset) вміст цих байтів лишається тим самим,
 * бо живлення ядра не зникало. Скрипт компонування мусить розмістити секцію
 * в SRAM і не включати її ні в .bss, ні в таблицю копіювання .data. */
__attribute__((section(".noinit"), used)) static crash_log_t g_log;

/* ---- CRC-16/CCITT-FALSE ------------------------------------------------
 * Журнал живе в пам'яті, яку могло зачепити просідання живлення. Без
 * контрольної суми ми б показали сервісному інженеру телеметрію з
 * випадкового сміття — це гірше, ніж чесне «журнал утрачено». */
static uint16_t crc16(const uint8_t *data, size_t len)
{
    uint16_t crc = 0xFFFFU;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x8000U) ? (uint16_t)((crc << 1) ^ 0x1021U)
                                  : (uint16_t)(crc << 1);
        }
    }
    return crc;
}

/* Сума рахується по всіх полях, крім самих crc/reserved у хвості. */
static size_t payload_len(void)
{
    return offsetof(crash_log_t, crc);
}

static uint16_t compute_crc(void)
{
    return crc16((const uint8_t *)&g_log, payload_len());
}

static void seal(void)
{
    g_log.crc = compute_crc();
    g_log.reserved = 0;
}

static bool verify(void)
{
    return g_log.magic == CRASH_LOG_MAGIC && g_log.crc == compute_crc();
}

static void wipe(void)
{
    memset(&g_log, 0, sizeof(g_log));
    g_log.magic = CRASH_LOG_MAGIC;
}

/* ---- Декодування причини скидання -------------------------------------
 * Порядок перевірки не довільний: прапорці накопичуються, і після
 * подачі живлення разом із PORRSTF апаратно виставляється й PINRSTF.
 * Тому спершу дивимося на «неприємні» причини — сторож і просідання, —
 * і лише потім на нормальні. */
static reset_cause_t decode_cause(uint32_t csr)
{
    if (csr & RCC_CSR_IWDGRSTF) {
        return RESET_CAUSE_IWDG;
    }
    if (csr & RCC_CSR_WWDGRSTF) {
        return RESET_CAUSE_WWDG;
    }
    if (csr & RCC_CSR_BORRSTF && !(csr & RCC_CSR_PORRSTF)) {
        return RESET_CAUSE_BROWN_OUT;
    }
    if (csr & RCC_CSR_SFTRSTF) {
        return RESET_CAUSE_SOFTWARE;
    }
    if (csr & RCC_CSR_LPWRRSTF) {
        return RESET_CAUSE_LOW_POWER;
    }
    if (csr & RCC_CSR_PORRSTF) {
        return RESET_CAUSE_POWER_ON;
    }
    if (csr & RCC_CSR_PINRSTF) {
        return RESET_CAUSE_PIN;
    }
    return RESET_CAUSE_UNKNOWN;
}

reset_cause_t crash_log_begin_boot(void)
{
    const uint32_t csr = RCC_CSR;
    /* Прапорці треба зняти тут-таки, інакше наступний старт побачить
     * суміш причин і звинуватить сторожа в чужому гріху. */
    RCC_CSR = csr | RCC_CSR_RMVF;

    const reset_cause_t cause = decode_cause(csr);
    const bool cold = (cause == RESET_CAUSE_POWER_ON) || (cause == RESET_CAUSE_UNKNOWN);

    if (cold || !verify()) {
        /* Журнал або новий, або зіпсований — починаємо з чистого. */
        wipe();
    }

    ++g_log.boot_count;
    g_log.reset_cause = (uint32_t)cause;
    g_log.raw_rcc_csr = csr;
    g_log.uptime_ms = 0;

    if (cause == RESET_CAUSE_IWDG || cause == RESET_CAUSE_WWDG ||
        cause == RESET_CAUSE_BROWN_OUT) {
        ++g_log.fault_count;
        /* Сторож і просідання не лишають ані PC, ані CFSR: ядро просто
         * зникло. Причину аварії ставимо лише тоді, коли її ще не записав
         * обробник збою перед рестартом. */
        if (g_log.panic_reason == (uint32_t)PANIC_NONE) {
            g_log.panic_reason = (cause == RESET_CAUSE_BROWN_OUT)
                                     ? (uint32_t)PANIC_BROWN_OUT
                                     : (uint32_t)PANIC_ASSERTION;
        }
    }

    seal();
    return cause;
}

void crash_log_record_panic(panic_reason_t reason, const fault_context_t *ctx)
{
    if (!verify()) {
        wipe();
    }
    g_log.panic_reason = (uint32_t)reason;
    if (ctx != NULL) {
        g_log.fault = *ctx;
    } else {
        memset(&g_log.fault, 0, sizeof(g_log.fault));
    }
    seal();
}

void crash_log_note_safe_state(void)
{
    if (!verify()) {
        wipe();
    }
    ++g_log.safe_state_entries;
    seal();
}

void crash_log_note_uptime(uint32_t ms)
{
    if (!verify()) {
        return;
    }
    g_log.uptime_ms = ms;
    seal();
}

const crash_log_t *crash_log_get(void)
{
    return &g_log;
}

bool crash_log_is_intact(void)
{
    return verify();
}

/* ---- Форматування рядка телеметрії ------------------------------------
 * printf у прошивці виробу тягне сотні байтів стека й купу коду; у гілці
 * аварії стек уже може бути зіпсований. Пишемо цифри руками. */
static size_t put_str(char *buf, size_t cap, size_t at, const char *s)
{
    while (*s != '\0' && at + 1 < cap) {
        buf[at++] = *s++;
    }
    return at;
}

static size_t put_u32(char *buf, size_t cap, size_t at, uint32_t v)
{
    char tmp[10];
    int n = 0;
    do {
        tmp[n++] = (char)('0' + (v % 10U));
        v /= 10U;
    } while (v != 0U && n < (int)sizeof(tmp));

    while (n-- > 0 && at + 1 < cap) {
        buf[at++] = tmp[n];
    }
    return at;
}

static size_t put_hex32(char *buf, size_t cap, size_t at, uint32_t v)
{
    static const char digits[] = "0123456789ABCDEF";
    at = put_str(buf, cap, at, "0x");
    for (int shift = 28; shift >= 0; shift -= 4) {
        if (at + 1 >= cap) {
            break;
        }
        buf[at++] = digits[(v >> shift) & 0xFU];
    }
    return at;
}

size_t crash_log_render(char *buf, size_t cap)
{
    if (buf == NULL || cap == 0U) {
        return 0U;
    }
    size_t at = 0U;

    at = put_str(buf, cap, at, "BOOT #");
    at = put_u32(buf, cap, at, g_log.boot_count);
    at = put_str(buf, cap, at, " cause=");
    at = put_str(buf, cap, at, reset_cause_name((reset_cause_t)g_log.reset_cause));
    at = put_str(buf, cap, at, " csr=");
    at = put_hex32(buf, cap, at, g_log.raw_rcc_csr);
    at = put_str(buf, cap, at, " faults=");
    at = put_u32(buf, cap, at, g_log.fault_count);
    at = put_str(buf, cap, at, " safe=");
    at = put_u32(buf, cap, at, g_log.safe_state_entries);

    if (g_log.panic_reason != (uint32_t)PANIC_NONE) {
        at = put_str(buf, cap, at, " panic=");
        at = put_str(buf, cap, at, panic_reason_name((panic_reason_t)g_log.panic_reason));
        at = put_str(buf, cap, at, " pc=");
        at = put_hex32(buf, cap, at, g_log.fault.pc);
        at = put_str(buf, cap, at, " lr=");
        at = put_hex32(buf, cap, at, g_log.fault.lr);
        at = put_str(buf, cap, at, " sp=");
        at = put_hex32(buf, cap, at, g_log.fault.sp);
        at = put_str(buf, cap, at, " cfsr=");
        at = put_hex32(buf, cap, at, g_log.fault.cfsr);
        at = put_str(buf, cap, at, " up=");
        at = put_u32(buf, cap, at, g_log.uptime_ms);
        at = put_str(buf, cap, at, "ms");
    }

    if (!verify()) {
        at = put_str(buf, cap, at, " [ЖУРНАЛ ПОШКОДЖЕНО]");
    }

    buf[at] = '\0';
    return at;
}

const char *reset_cause_name(reset_cause_t cause)
{
    switch (cause) {
    case RESET_CAUSE_POWER_ON:  return "POWER_ON";
    case RESET_CAUSE_PIN:       return "PIN";
    case RESET_CAUSE_BROWN_OUT: return "BROWN_OUT";
    case RESET_CAUSE_SOFTWARE:  return "SOFTWARE";
    case RESET_CAUSE_IWDG:      return "IWDG";
    case RESET_CAUSE_WWDG:      return "WWDG";
    case RESET_CAUSE_LOW_POWER: return "LOW_POWER";
    case RESET_CAUSE_UNKNOWN:
    default:                    return "UNKNOWN";
    }
}

const char *panic_reason_name(panic_reason_t reason)
{
    switch (reason) {
    case PANIC_HARDFAULT:      return "HARDFAULT";
    case PANIC_ASSERTION:      return "ASSERTION";
    case PANIC_SENSOR_TIMEOUT: return "SENSOR_TIMEOUT";
    case PANIC_BUS_STUCK:      return "BUS_STUCK";
    case PANIC_LOOP_TOO_FAST:  return "LOOP_TOO_FAST";
    case PANIC_BROWN_OUT:      return "BROWN_OUT";
    case PANIC_NONE:
    default:                   return "NONE";
    }
}
