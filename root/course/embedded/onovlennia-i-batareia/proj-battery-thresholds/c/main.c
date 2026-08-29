#include <setjmp.h>
#include <stdio.h>
#include <string.h>

#include "battery_gate.h"
#include "ota_telemetry.h"

/* Модель плати замість справжнього заліза: комірка з ЕРС і внутрішнім
   опором, послідовний опір монтажу, тестове навантаження й backup-регістр,
   який переживає скид. Апаратний BOR моделюємо longjmp — керування
   повертається в точку старту прошивки, а NV лишається як був. */

#define WIRING_MOHM   250u /* контакти відсіку, дроти, шунт */
#define QUIESCENT_MA   20u /* споживання в спокої */
#define TEST_LOAD_MA  200u /* мусить збігатися з lim.test_load_ma */
#define BOR_MV       2700u /* апаратний поріг скиду ядра */

typedef struct {
    const char *name;
    bool        vbus;
    bool        temp_sensor_ok;
    int16_t     temp_c;
    uint8_t     soc;
    uint16_t    ocv_mv;
    uint16_t    cell_esr_mohm;
    bool        emergency;
} scenario_t;

typedef struct {
    const scenario_t *sc;
    bool              load_on;
    uint32_t          nv;        /* backup-регістр RTC */
    uint32_t          rng;
    unsigned          brownouts;
    jmp_buf           reset;
} board_t;

static board_t g_board;

static uint16_t rail_mv(const board_t *b, uint32_t load_ma)
{
    uint32_t r_total = (uint32_t)b->sc->cell_esr_mohm + WIRING_MOHM;
    uint32_t drop = (r_total * load_ma) / 1000u;
    return (drop >= b->sc->ocv_mv) ? 0u : (uint16_t)(b->sc->ocv_mv - drop);
}

/* Детермінований шум АЦП ±4 мВ — саме через нього ми усереднюємо відліки. */
static int adc_noise_mv(board_t *b)
{
    b->rng = b->rng * 1664525u + 1013904223u;
    return (int)((b->rng >> 16) % 9u) - 4;
}

static bool sim_vbus(void *ctx)
{
    return ((board_t *)ctx)->sc->vbus;
}

static bool sim_temperature(void *ctx, int16_t *out)
{
    board_t *b = (board_t *)ctx;
    if (!b->sc->temp_sensor_ok) {
        return false; /* NTC відвалився або I2C не відповів */
    }
    *out = b->sc->temp_c;
    return true;
}

static bool sim_soc(void *ctx, uint8_t *out)
{
    *out = ((board_t *)ctx)->sc->soc;
    return true;
}

static bool sim_voltage(void *ctx, uint16_t *out)
{
    board_t *b = (board_t *)ctx;
    uint32_t load = QUIESCENT_MA + (b->load_on ? TEST_LOAD_MA : 0u);
    int mv = (int)rail_mv(b, load) + adc_noise_mv(b);
    *out = (mv < 0) ? 0u : (uint16_t)mv;
    return true;
}

static void sim_test_load(void *ctx, bool on)
{
    board_t *b = (board_t *)ctx;
    b->load_on = on;
    if (on && rail_mv(b, QUIESCENT_MA + TEST_LOAD_MA) < BOR_MV) {
        /* Шина провалилась нижче порогу — ядро скидається. Flash при цьому
           цілий: жодного байта ми ще не стерли. */
        b->load_on = false;
        b->brownouts++;
        longjmp(b->reset, 1);
    }
}

static void sim_delay_ms(void *ctx, uint32_t ms)
{
    (void)ctx;
    (void)ms; /* на моделі час не тече */
}

static void sim_delay_us(void *ctx, uint32_t us)
{
    (void)ctx;
    (void)us;
}

static bool sim_nv_load(void *ctx, uint32_t *out)
{
    *out = ((board_t *)ctx)->nv;
    return true;
}

static bool sim_nv_store(void *ctx, uint32_t word)
{
    ((board_t *)ctx)->nv = word;
    return true;
}

static void print_report(const ota_gate_report_t *r)
{
    printf("  %s\n", ota_verdict_name(r->verdict));
    if (r->has_temp) {
        printf("    температура: %d °C\n", (int)r->temp_c);
    }
    if (r->has_soc) {
        printf("    заряд: %u %%\n", (unsigned)r->soc_percent);
    }
    if (r->has_idle) {
        printf("    напруга спокою: %u мВ\n", (unsigned)r->v_idle_mv);
    }
    if (r->has_pulse) {
        printf("    під навантаженням: %u мВ, опір %u мОм, прогноз %u мВ (бар'єр %u мВ)\n",
               (unsigned)r->v_load_mv, (unsigned)r->esr_mohm,
               (unsigned)r->v_forecast_mv,
               (unsigned)ota_gate_safe_floor_mv(&OTA_LIMITS_DEFAULT));
    }
    if (r->throttled) {
        printf("    пом'якшення: CPU %u МГц, SPI %u МГц, TX %+d dBm\n",
               (unsigned)r->throttle.cpu_mhz, (unsigned)r->throttle.spi_mhz,
               (int)r->throttle.tx_dbm);
    }
    if (r->power_faults > 0) {
        printf("    зривів живлення в латчі: %u\n", (unsigned)r->power_faults);
    }
}

static void print_telemetry(const ota_gate_report_t *r)
{
    ota_deny_summary_t summary;
    if (!ota_telemetry_summarize(r, &OTA_LIMITS_DEFAULT, &summary)) {
        return;
    }

    uint8_t packet[64];
    int n = ota_telemetry_encode(r, &OTA_LIMITS_DEFAULT, packet, sizeof packet);
    if (n < 0) {
        printf("    телеметрія не вмістилась у буфер\n");
        return;
    }

    printf("    телеметрія: %s, retry-after %lu с%s\n",
           ota_telemetry_code_name(summary.code),
           (unsigned long)summary.retry_after_s,
           summary.service_required ? ", потрібен виїзд техніка" : "");
    printf("    пакет:");
    for (int i = 0; i < n; ++i) {
        printf(" %02X", packet[i]);
    }
    putchar('\n');
}

static const scenario_t SCENARIOS[] = {
    { "мережевий адаптер увімкнено",              true,  true,  24, 62, 4050,  120, false },
    { "свіжа комірка, кімнатна температура",      false, true,  22, 88, 3950,   90, false },
    { "комірка на морозі",                        false, true,  -2, 71, 3800,  400, false },
    { "паливомір показує 28 %",                   false, true,  20, 28, 3600,  150, false },
    { "зношена комірка, планове оновлення",       false, true,  12, 47, 3180,  950, false },
    { "та сама комірка, критичний патч безпеки",  false, true,  12, 47, 3180,  950, true  },
    { "комірка провалює вже тестовий імпульс",    false, true,   8, 46, 2960, 1500, false },
    { "термодавач не відповідає",                 false, false,  0, 80, 3900,  120, false }
};

int main(void)
{
    ota_hal_t hal = {
        .vbus_present       = sim_vbus,
        .read_temperature_c = sim_temperature,
        .read_soc_percent   = sim_soc,
        .read_voltage_mv    = sim_voltage,
        .set_test_load      = sim_test_load,
        .delay_ms           = sim_delay_ms,
        .delay_us           = sim_delay_us,
        .nv_load            = sim_nv_load,
        .nv_store           = sim_nv_store,
        .ctx                = &g_board
    };

    for (volatile size_t i = 0; i < sizeof SCENARIOS / sizeof SCENARIOS[0]; ++i) {
        memset(&g_board, 0, sizeof g_board);
        g_board.sc  = &SCENARIOS[i];
        g_board.rng = 0x1234u + (uint32_t)i;

        printf("=== %s ===\n", SCENARIOS[i].name);

        volatile unsigned attempt = 0;
        for (;;) {
            if (setjmp(g_board.reset) != 0) {
                /* Сюди повертає «скид»: у RAM усе втрачено, латч у NV живий. */
                printf("  [спроба %u] BOR під час тестового імпульсу — "
                       "перезавантаження у стару прошивку\n", attempt);
                if (attempt >= 8u) {
                    printf("  забагато скидів, зупиняємо прогін сценарію\n");
                    break;
                }
                continue;
            }

            attempt++;
            ota_gate_report_t report;
            ota_gate_evaluate(&hal, &OTA_LIMITS_DEFAULT, SCENARIOS[i].emergency, &report);
            print_report(&report);
            if (!ota_gate_allowed(&report)) {
                print_telemetry(&report);
            }
            break;
        }

        if (g_board.brownouts > 0) {
            printf("  зривів живлення на цій платі: %u\n", g_board.brownouts);
        }
        putchar('\n');
    }

    return 0;
}
