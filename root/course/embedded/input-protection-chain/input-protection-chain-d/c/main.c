/* main.c — прогін наглядача крізь життя вхідної шини 24 В.
 *
 * Замість плати тут модель: профіль напруги на роз'ємі перетворюється на код
 * АЦП тим самим дільником 110к/10к, що стоїть у схемі, з шумом у кілька
 * молодших розрядів. Наглядач не знає, що джерело вибірок — модель.
 *
 * Збірка: cc -std=c11 -O2 -Wall -Wextra main.c power_monitor.c -o pwrsim
 */
#include <stddef.h>
#include <stdio.h>

#include "power_monitor.h"

#define SAMPLE_PERIOD_MS 1U
#define EFUSE_FLT_MS     830U   /* коли eFuse смикне PIN_FAULT_IRQ */
#define CLEAR_LOCKOUT_MS 1900U  /* коли оператор зніме засув */

/* Стан плати: єдиний вивід, яким наглядач керує напряму. */
typedef struct {
    bool     pin_pwr_enable;
    uint32_t toggles;
} board_t;

static void board_set_enable(void *ctx, bool on)
{
    board_t *b = (board_t *)ctx;
    b->pin_pwr_enable = on;
    b->toggles++;
}

typedef struct {
    uint32_t    until_ms;
    uint32_t    v_start_mv;
    uint32_t    v_end_mv;
    const char *what;
} segment_t;

/* Профіль напруги на вході: від холодного під'єднання до серії просідань. */
static const segment_t PROFILE[] = {
    {   20,     0,     0, "плата знеструмлена" },
    {  120,     0, 24000, "гаряче під'єднання: плавний пуск заряджає C_bulk" },
    {  400, 24000, 24000, "штатний режим 24 В" },
    {  460, 15000, 15000, "просідання шини до 15 В (пуск сусіднього приводу)" },
    {  800, 24000, 24000, "шина відновилася" },
    {  900, 48000, 48000, "пробій регулятора БЖ: 48 В на вході" },
    { 1430, 24000, 24000, "БЖ замінено, шина 24 В" },
    { 1460, 15000, 15000, "просідання №2" },
    { 1590, 24000, 24000, "норма" },
    { 1620, 15000, 15000, "просідання №3" },
    { 1750, 24000, 24000, "норма" },
    { 1780, 15000, 15000, "просідання №4 — ліміт повторів вичерпано" },
    { 2100, 24000, 24000, "норма, але тримається засув" },
};
#define PROFILE_LEN (sizeof PROFILE / sizeof PROFILE[0])

static uint32_t profile_voltage_mv(uint32_t t_ms, size_t *seg_index)
{
    uint32_t from_ms = 0U;
    for (size_t i = 0; i < PROFILE_LEN; i++) {
        if (t_ms < PROFILE[i].until_ms) {
            *seg_index = i;
            uint32_t span = PROFILE[i].until_ms - from_ms;
            uint32_t done = t_ms - from_ms;
            int32_t  delta = (int32_t)PROFILE[i].v_end_mv - (int32_t)PROFILE[i].v_start_mv;
            return (uint32_t)((int32_t)PROFILE[i].v_start_mv + delta * (int32_t)done / (int32_t)span);
        }
        from_ms = PROFILE[i].until_ms;
    }
    *seg_index = PROFILE_LEN - 1U;
    return PROFILE[PROFILE_LEN - 1U].v_end_mv;
}

/* Детермінований шум: прогін мусить повторюватися вибірка у вибірку. */
static uint32_t xorshift32(uint32_t *s)
{
    uint32_t x = *s;
    x ^= x << 13; x ^= x >> 17; x ^= x << 5;
    *s = x;
    return x;
}

/* Модель вимірювального тракту: напруга шини → код 12-бітного АЦП. */
static uint16_t sample_adc(const pwr_config_t *cfg, uint32_t bus_mv, uint32_t *noise_state)
{
    uint64_t num = (uint64_t)bus_mv * cfg->div_bottom_ohm * cfg->adc_full_scale;
    uint64_t den = ((uint64_t)cfg->div_top_ohm + cfg->div_bottom_ohm) * cfg->vref_mv;
    int64_t  code = (int64_t)(num / den);

    code += (int64_t)(xorshift32(noise_state) % 7U) - 3;  /* ±3 МЗР шуму */
    if (code < 0) code = 0;
    if (code > cfg->adc_full_scale) code = cfg->adc_full_scale;  /* насичення шкали */
    return (uint16_t)code;
}

int main(void)
{
    const pwr_config_t cfg = {
        .div_top_ohm     = 110000U,
        .div_bottom_ohm  = 10000U,
        .vref_mv         = 3300U,
        .adc_full_scale  = 4095U,
        .filter_shift    = 3U,
        .uvlo_trip_mv    = 16500U,
        .uvlo_clear_mv   = 18000U,
        .ovlo_clear_mv   = 30500U,
        .ovlo_trip_mv    = 32000U,
        .confirm_samples = 5U,
        .settle_samples  = 20U,
        .retry_delay_ms  = 100U,
        .retry_window_ms = 1500U,
        .retry_limit     = 5U,
    };

    board_t board = { .pin_pwr_enable = false, .toggles = 0U };
    pwr_monitor_t mon;

    pwr_err_t err = pwr_monitor_init(&mon, &cfg, board_set_enable, &board);
    if (err != PWR_OK) {
        fprintf(stderr, "наглядач не піднявся: код %d\n", (int)err);
        return 1;
    }

    printf("  t, мс |  U шини |  U виміряна | стан        | PIN_PWR_ENABLE\n");
    printf("--------+---------+-------------+-------------+---------------\n");

    uint32_t    noise_state = 0x1234ABCDU;
    pwr_state_t last_state = pwr_monitor_state(&mon);
    size_t      last_segment = (size_t)-1;
    bool        efuse_fired = false;
    bool        lockout_cleared = false;

    for (uint32_t t = 0U; t <= 2200U; t += SAMPLE_PERIOD_MS) {
        size_t   segment = 0U;
        uint32_t bus_mv = profile_voltage_mv(t, &segment);

        if (segment != last_segment) {
            printf("        · %s\n", PROFILE[segment].what);
            last_segment = segment;
        }

        if (!efuse_fired && t >= EFUSE_FLT_MS) {
            /* Переривання EXTI від виводу PIN_FAULT_IRQ. */
            pwr_monitor_efuse_isr(&mon);
            efuse_fired = true;
        }
        if (!lockout_cleared && t >= CLEAR_LOCKOUT_MS) {
            if (pwr_monitor_clear_lockout(&mon, t)) {
                printf("        · оператор зняв засув\n");
            }
            lockout_cleared = true;
        }

        uint16_t code = sample_adc(&cfg, bus_mv, &noise_state);
        if (pwr_monitor_on_sample(&mon, code, t) != PWR_OK) {
            fprintf(stderr, "вибірку відхилено на t=%u мс\n", t);
            return 1;
        }

        pwr_state_t now_state = pwr_monitor_state(&mon);
        if (now_state != last_state) {
            printf("%7u | %5u мВ | %8u мВ | %-11s | %d\n",
                   t, bus_mv, pwr_monitor_voltage_mv(&mon),
                   pwr_state_name(now_state), board.pin_pwr_enable ? 1 : 0);
            last_state = now_state;
        }
    }

    const pwr_stats_t *st = pwr_monitor_stats(&mon);
    printf("\nвибірок: %u   пусків: %u   перемикань ключа: %u\n",
           st->samples, st->starts, board.toggles);
    printf("аварії: UVLO %u, OVLO %u, eFuse %u, засувів %u\n",
           st->uvlo_events, st->ovlo_events, st->efuse_events, st->lockouts);
    printf("напруга шини: від %u мВ до %u мВ (стеля шкали дільника — 39.6 В)\n",
           st->v_min_mv, st->v_max_mv);
    return 0;
}
