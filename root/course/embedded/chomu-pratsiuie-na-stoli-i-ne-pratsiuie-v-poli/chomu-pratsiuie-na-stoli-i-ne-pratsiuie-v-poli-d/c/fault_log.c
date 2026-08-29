/* fault_log.c — розкладка резервного домену й розшифровка причини старту.
 *
 * Розкладка двадцяти слів BKP0R..BKP19R:
 *   [0]      сигнатура (16 біт) | лічильник записів (8) | голова кільця (8)
 *   [1]      старти (16) | Brownout-скидання (16)
 *   [2]      скидання сторожем (16) | порятунки шини (16)
 *   [3]      слід HardFault: 0xFA у старшому байті | молодші 24 біти PC
 *   [4..19]  шістнадцять подій, по одному слову на подію
 *
 * Подія пакується в 32 біти так:
 *   31..29 причина · 28..21 температура+64 · 20..13 напруга/16 · 12..0 секунди
 * Кожне поле обрізане свідомо: точність тут не потрібна, потрібна історія
 * останніх шістнадцяти аварій у пам'яті, якої всього двадцять слів.
 */

#include "fault_log.h"
#include "platform.h"

#define BKP_HEADER 0u
#define BKP_COUNTERS_A 1u
#define BKP_COUNTERS_B 2u
#define BKP_HARDFAULT 3u
#define BKP_EVENTS 4u

#define LOG_MAGIC 0xF1E1u
#define HARDFAULT_MARK 0xFAu

/* --- сигнатури CMSIS для прапорів RCC_CSR (їх знає лише порт) ------------ */
#define CSR_LPWRRST (1u << 31)
#define CSR_WWDGRST (1u << 30)
#define CSR_IWDGRST (1u << 29)
#define CSR_SFTRST (1u << 28)
#define CSR_PORRST (1u << 27)
#define CSR_PINRST (1u << 26)
#define CSR_BORRST (1u << 25)

static uint32_t read_word(uint8_t index)
{
    uint32_t value = 0u;
    (void)plat_bkp_read(index, &value);
    return value;
}

static uint16_t header_count(uint32_t header)
{
    return (uint16_t)((header >> 8) & 0xFFu);
}

static uint8_t header_head(uint32_t header)
{
    return (uint8_t)(header & 0xFFu);
}

static void header_store(uint8_t count, uint8_t head)
{
    (void)plat_bkp_write(BKP_HEADER, ((uint32_t)LOG_MAGIC << 16) | ((uint32_t)count << 8) | head);
}

static void wipe_domain(void)
{
    for (uint8_t i = 0u; i < PLAT_BKP_WORDS; i++) {
        (void)plat_bkp_write(i, 0u);
    }
    header_store(0u, 0u);
}

static void counters_load(fault_counters_t *out)
{
    const uint32_t a = read_word(BKP_COUNTERS_A);
    const uint32_t b = read_word(BKP_COUNTERS_B);
    out->boots = (uint16_t)(a >> 16);
    out->brownouts = (uint16_t)(a & 0xFFFFu);
    out->watchdogs = (uint16_t)(b >> 16);
    out->bus_recoveries = (uint16_t)(b & 0xFFFFu);
}

static void counters_store(const fault_counters_t *c)
{
    (void)plat_bkp_write(BKP_COUNTERS_A, ((uint32_t)c->boots << 16) | c->brownouts);
    (void)plat_bkp_write(BKP_COUNTERS_B, ((uint32_t)c->watchdogs << 16) | c->bus_recoveries);
}

/* Лічильники впираються в стелю замість переповнення: «65535 Brownout»
 * — це вирок конструкції, і обнулити його до нуля означало б збрехати. */
static uint16_t bump(uint16_t value)
{
    return (value == 0xFFFFu) ? value : (uint16_t)(value + 1u);
}

/* --- пакування події ----------------------------------------------------- */

static uint32_t event_pack(reset_cause_t cause, int16_t temperature_c, uint16_t voltage_mv,
                           uint32_t uptime_s)
{
    int32_t t = (int32_t)temperature_c + 64;
    if (t < 0) {
        t = 0;
    } else if (t > 255) {
        t = 255;
    }

    uint32_t mv = voltage_mv / 16u;
    if (mv > 255u) {
        mv = 255u;
    }
    if (uptime_s > 8191u) {
        uptime_s = 8191u;
    }

    return (((uint32_t)cause & 7u) << 29) | ((uint32_t)t << 21) | (mv << 13) | uptime_s;
}

static void event_unpack(uint32_t word, fault_event_t *out)
{
    out->cause = (reset_cause_t)((word >> 29) & 7u);
    out->temperature_c = (int16_t)(((word >> 21) & 0xFFu) - 64u);
    out->voltage_mv = (uint16_t)(((word >> 13) & 0xFFu) * 16u);
    out->uptime_s = (uint16_t)(word & 0x1FFFu);
}

/* --- причина старту ------------------------------------------------------ */

static reset_cause_t decode_flags(uint32_t csr)
{
    /* Порядок перевірок — це порядок важливості, а не порядок бітів.
     * Залізо часто піднімає кілька прапорів одразу: після Brownout стоїть
     * і PINRST, бо просадка тягне лінію NRST. Питання «що нас убило»
     * має рівно одну відповідь, і це найгірший з піднятих прапорів. */
    if ((csr & CSR_BORRST) != 0u) {
        return RESET_CAUSE_BROWNOUT;
    }
    if ((csr & (CSR_IWDGRST | CSR_WWDGRST)) != 0u) {
        return RESET_CAUSE_WATCHDOG;
    }
    if ((csr & CSR_LPWRRST) != 0u) {
        return RESET_CAUSE_LOW_POWER;
    }
    if ((csr & CSR_SFTRST) != 0u) {
        return RESET_CAUSE_SOFTWARE;
    }
    if ((csr & CSR_PINRST) != 0u) {
        return RESET_CAUSE_PIN;
    }
    if ((csr & CSR_PORRST) != 0u) {
        return RESET_CAUSE_POWER_ON;
    }
    return RESET_CAUSE_UNKNOWN;
}

void fault_log_open(boot_report_t *report)
{
    if (report == 0) {
        return;
    }

    const uint32_t header = read_word(BKP_HEADER);
    report->history_lost = ((header >> 16) != LOG_MAGIC);
    if (report->history_lost) {
        /* Перший старт, знята батарейка резервного домену або зіпсовані
         * слова. Розмічаємо наново — і кажемо про це вголос. */
        wipe_domain();
    }

    report->cause = decode_flags(plat_reset_flags_raw());
    report->fault_pc = 0u;

    /* Слід HardFault важить більше за прапор заліза: після виклику
     * NVIC_SystemReset із обробника винятку RCC_CSR покаже лише SFTRST,
     * тобто «нас перезапустила програма» — правду знає тільки цей запис. */
    const uint32_t mark = read_word(BKP_HARDFAULT);
    if ((mark >> 24) == HARDFAULT_MARK) {
        report->cause = RESET_CAUSE_HARD_FAULT;
        report->fault_pc = mark & 0x00FFFFFFu;
        (void)plat_bkp_write(BKP_HARDFAULT, 0u); /* слід прочитано, знімаємо */
    }

    counters_load(&report->counters);
    report->counters.boots = bump(report->counters.boots);
    if (report->cause == RESET_CAUSE_BROWNOUT) {
        report->counters.brownouts = bump(report->counters.brownouts);
    } else if (report->cause == RESET_CAUSE_WATCHDOG) {
        report->counters.watchdogs = bump(report->counters.watchdogs);
    }
    counters_store(&report->counters);
}

void fault_log_append(reset_cause_t cause, int16_t temperature_c, uint16_t voltage_mv,
                      uint32_t uptime_ms)
{
    const uint32_t header = read_word(BKP_HEADER);
    if ((header >> 16) != LOG_MAGIC) {
        wipe_domain(); /* домен зіпсувався в роботі — краще порожній, ніж брехливий */
    }

    uint8_t head = header_head(header);
    uint16_t count = header_count(header);
    if (head >= FAULT_LOG_SLOTS) {
        head = 0u;
    }

    (void)plat_bkp_write((uint8_t)(BKP_EVENTS + head),
                         event_pack(cause, temperature_c, voltage_mv, uptime_ms / 1000u));

    head = (uint8_t)((head + 1u) % FAULT_LOG_SLOTS);
    if (count < FAULT_LOG_SLOTS) {
        count++;
    }
    header_store((uint8_t)count, head);
}

uint8_t fault_log_read(fault_event_t *out, uint8_t max)
{
    if (out == 0 || max == 0u) {
        return 0u;
    }

    const uint32_t header = read_word(BKP_HEADER);
    if ((header >> 16) != LOG_MAGIC) {
        return 0u;
    }

    uint16_t count = header_count(header);
    if (count > FAULT_LOG_SLOTS) {
        count = FAULT_LOG_SLOTS;
    }
    if (max > count) {
        max = (uint8_t)count;
    }

    uint8_t head = header_head(header) % FAULT_LOG_SLOTS;
    for (uint8_t i = 0u; i < max; i++) {
        /* Ідемо назад від голови: найсвіжіша подія лежить перед нею. */
        head = (uint8_t)((head + FAULT_LOG_SLOTS - 1u) % FAULT_LOG_SLOTS);
        event_unpack(read_word((uint8_t)(BKP_EVENTS + head)), &out[i]);
    }
    return max;
}

void fault_log_bump_recovery(void)
{
    fault_counters_t c;
    counters_load(&c);
    c.bus_recoveries = bump(c.bus_recoveries);
    counters_store(&c);
}

const char *fault_log_cause_name(reset_cause_t cause)
{
    switch (cause) {
    case RESET_CAUSE_POWER_ON:
        return "power-on";
    case RESET_CAUSE_PIN:
        return "nrst";
    case RESET_CAUSE_BROWNOUT:
        return "brownout";
    case RESET_CAUSE_WATCHDOG:
        return "watchdog";
    case RESET_CAUSE_HARD_FAULT:
        return "hardfault";
    case RESET_CAUSE_SOFTWARE:
        return "software";
    case RESET_CAUSE_LOW_POWER:
        return "low-power";
    default:
        return "unknown";
    }
}

bool fault_log_needs_safe_start(const boot_report_t *report)
{
    if (report == 0) {
        return true;
    }
    if (report->cause == RESET_CAUSE_BROWNOUT || report->cause == RESET_CAUSE_HARD_FAULT) {
        return true;
    }
    /* Один сторожовий перезапуск за все життя приладу — випадковість.
     * Три і більше — зависання повторюване, і піднімати радіо на повній
     * частоті означає знову приїхати сюди ж. */
    return report->counters.watchdogs >= 3u;
}

/* --- перехоплення винятку ------------------------------------------------ */

/* Викликається з обробника нижче з покажчиком на кадр, який залізо поклало
 * на стек: r0 r1 r2 r3 r12 lr pc psr. Нас цікавить pc — адреса інструкції,
 * на якій усе розвалилося. Прототип поруч, бо єдиний виклик — з асемблера. */
void fault_record_and_reset(const uint32_t *frame);

void fault_record_and_reset(const uint32_t *frame)
{
    (void)plat_bkp_write(BKP_HARDFAULT, ((uint32_t)HARDFAULT_MARK << 24) | (frame[6] & 0x00FFFFFFu));
    plat_system_reset();
}

/* Обробник голий: жодного прологу, бо пролог зіпсував би регістри до того,
 * як ми дізнаємось, на якому стеку лежить кадр винятку. Біт 2 у LR каже,
 * звідки прийшли — з головного стека чи з процесного. */
__attribute__((naked)) void HardFault_Handler(void)
{
    __asm volatile("tst lr, #4                 \n"
                   "ite eq                     \n"
                   "mrseq r0, msp              \n"
                   "mrsne r0, psp              \n"
                   "b fault_record_and_reset   \n");
}
