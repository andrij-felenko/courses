/*
 * Прогін аудиту бюджетів на двох ревізіях автономного реєстратора.
 *
 * Ревізія A — плата зі столу: лінійний стабілізатор 12 В → 3.3 В, буферна
 * ємність 100 мкФ, 512 КБ Flash під образ 380 КБ, цикл передавання 60 с.
 * Ревізія B — та сама схема після перерахунку бюджетів: імпульсний
 * перетворювач, більший буфер, вдвічі більший Flash, довший цикл.
 *
 * Числа взяті з розрахунків статті, тож звіт показує рівно ті самі межі.
 */

#include "budget_monitor.h"

#include <stdio.h>
#include <string.h>

#define KIB 1024u

/* Профіль струму фаз циклу, мікроампери. */
static const uint32_t k_phase_current_ua[ENERGY_PHASE_COUNT] = {
    [ENERGY_PHASE_SLEEP]   = 15u,      /* 15 мкА глибокого сну */
    [ENERGY_PHASE_SENSE]   = 8500u,    /* 8.5 мА опитування по I2C */
    [ENERGY_PHASE_PROCESS] = 22000u,   /* 22 мА обробки та шифрування */
    [ENERGY_PHASE_TX]      = 140000u   /* 140 мА сплеску радіопередачі */
};

typedef struct {
    const char *title;
    uint32_t    regulator_loss_mw;   /* теплові втрати стабілізатора */
    uint32_t    bulk_uf;             /* буферна ємність шини */
    size_t      radio_stack_bytes;   /* стек задачі радіо */
    bool        heap_churn;          /* чи виділяється пам'ять безладно */
    uint32_t    flash_total_kib;
    uint32_t    sleep_ms;            /* сон між сеансами передавання */
    uint32_t    section_deadline_us; /* термін критичної секції */
} revision_t;

/* Області стеків: реєстратор вотермарки заливає їх шаблоном сам. */
static uint32_t g_stack_radio[512];  /* 2048 Б — стеля обох ревізій */
static uint32_t g_stack_sense[128];
static uint32_t g_stack_log[128];

static uint8_t  g_heap_area[16u * KIB];
static uint8_t  g_payload[4u * KIB];

/* Імітація зайнятої глибини стеку: задача затирає шаблон згори вниз. */
static void burn_stack(uint32_t *base, size_t size_bytes, size_t used_bytes)
{
    if (used_bytes > size_bytes) {
        used_bytes = size_bytes;
    }
    memset((uint8_t *)base + (size_bytes - used_bytes), 0xEE, used_bytes);
}

/* Корисне навантаження критичної секції: згортка Флетчера над буфером. */
static uint32_t fletcher32(const uint8_t *data, size_t length)
{
    uint32_t sum1 = 0xFFFFu;
    uint32_t sum2 = 0xFFFFu;

    for (size_t i = 0; i + 1u < length; i += 2u) {
        uint32_t word = (uint32_t)data[i] | ((uint32_t)data[i + 1u] << 8);
        sum1 = (sum1 + word) % 0xFFFFu;
        sum2 = (sum2 + sum1) % 0xFFFFu;
    }
    return (sum2 << 16) | sum1;
}

static void prepare_stacks(stack_registry_t *reg, const revision_t *rev)
{
    stack_registry_init(reg);
    stack_guard_register(reg, "радіо", g_stack_radio, rev->radio_stack_bytes, 256u);
    stack_guard_register(reg, "сенсори", g_stack_sense, sizeof g_stack_sense, 128u);
    stack_guard_register(reg, "журнал", g_stack_log, sizeof g_stack_log, 128u);

    /* Рукостискання TLS з'їдає 900 Б незалежно від ревізії плати. */
    burn_stack(g_stack_radio, rev->radio_stack_bytes, 900u);
    burn_stack(g_stack_sense, sizeof g_stack_sense, 220u);
    burn_stack(g_stack_log, sizeof g_stack_log, 180u);
}

static void prepare_heap(mem_pool_t *pool, const revision_t *rev)
{
    mem_pool_init(pool, g_heap_area, sizeof g_heap_area);

    if (!rev->heap_churn) {
        /* Буфери виділені один раз на старті — розривів не буде взагалі. */
        for (int i = 0; i < 3; ++i) {
            (void)mem_pool_alloc(pool, 1500u);
        }
        return;
    }

    /*
     * Ревізія A виділяє й звільняє пакети вроздріб протягом тижнів роботи.
     * Вільного лишається чимало, але суцільним він уже не буває.
     */
    void *blocks[48];
    size_t taken = 0u;

    while (taken < sizeof blocks / sizeof blocks[0]) {
        void *p = mem_pool_alloc(pool, 496u);
        if (p == NULL) {
            break;
        }
        blocks[taken++] = p;
    }
    for (size_t i = 0; i < taken; i += 2u) {
        mem_pool_free(pool, blocks[i]);
    }
}

static void prepare_energy(energy_ledger_t *ledger, const revision_t *rev)
{
    energy_ledger_init(ledger, k_phase_current_ua);

    /* П'ять повних циклів: сон, опитування, обробка, передача. */
    for (int cycle = 0; cycle < 5; ++cycle) {
        energy_ledger_account(ledger, ENERGY_PHASE_SLEEP,
                              (uint64_t)rev->sleep_ms * 1000u);
        energy_ledger_account(ledger, ENERGY_PHASE_SENSE, 300000u);
        energy_ledger_account(ledger, ENERGY_PHASE_PROCESS, 100000u);
        energy_ledger_account(ledger, ENERGY_PHASE_TX, 400000u);
    }
}

static void prepare_rail(rail_monitor_t *rail, const revision_t *rev)
{
    const rail_limits_t limits = {
        .nominal_mv = 3300u,
        .warn_mv    = 3000u,
        .bor_mv     = 2900u
    };
    rail_monitor_init(rail, &limits);

    /* Сплеск передавача: 350 мА протягом 120 мкс, ESR буфера 50 мОм. */
    uint32_t droop_mv = rail_estimate_droop_mv(350u, 50u, rev->bulk_uf, 120u);
    uint16_t under_load =
        (droop_mv < limits.nominal_mv)
            ? (uint16_t)(limits.nominal_mv - droop_mv)
            : 0u;

    printf("  розрахункове просідання на сплеску: %lu мВ → %u мВ на шині "
           "(BOR %u мВ)\n",
           (unsigned long)droop_mv, (unsigned)under_load,
           (unsigned)limits.bor_mv);

    rail_monitor_sample(rail, limits.nominal_mv);
    rail_monitor_sample(rail, under_load);
    rail_monitor_sample(rail, 3150u);
}

static void prepare_thermal(thermal_monitor_t *tm, const revision_t *rev)
{
    const thermal_limits_t limits = {
        .tj_max_dc      = 1250, /* 125.0 °C */
        .warn_margin_dc = 150,  /* тривога від 110.0 °C */
        .hysteresis_dc  = 50,
        .rth_ja_mcw     = 200000u /* SOT-23: 200 °C/Вт */
    };
    thermal_monitor_init(tm, &limits);

    /* Усередині герметичного корпусу під сонцем — 75 °C. */
    const int16_t ambient_dc = 750;

    uint32_t max_mw = thermal_max_power_mw(&limits, ambient_dc);
    uint32_t max_ma = thermal_ldo_max_current_ma(&limits, ambient_dc, 8700u);
    printf("  тепловий стелаж корпусу: %lu мВт, тобто %lu мА при перепаді "
           "8.7 В; вузол розсіює %lu мВт\n",
           (unsigned long)max_mw, (unsigned long)max_ma,
           (unsigned long)rev->regulator_loss_mw);

    thermal_monitor_sample(tm, ambient_dc, rev->regulator_loss_mw);
}

static void prepare_sections(section_timer_t *sections, const revision_t *rev)
{
    section_timer_init(&sections[0], "підпис пакета", rev->section_deadline_us);
    section_timer_init(&sections[1], "запис у журнал", 20000u);

    for (size_t i = 0; i < sizeof g_payload; ++i) {
        g_payload[i] = (uint8_t)(i * 31u + 7u);
    }

    volatile uint32_t sink = 0u;
    for (int run = 0; run < 8; ++run) {
        section_timer_begin(&sections[0]);
        sink ^= fletcher32(g_payload, sizeof g_payload);
        section_timer_end(&sections[0]);

        section_timer_begin(&sections[1]);
        sink ^= fletcher32(g_payload, 256u);
        section_timer_end(&sections[1]);
    }
    (void)sink;
}

static budget_action_t audit_revision(const revision_t *rev)
{
    stack_registry_t  stacks;
    mem_pool_t        heap;
    rail_monitor_t    rail;
    thermal_monitor_t thermal;
    energy_ledger_t   energy;
    section_timer_t   sections[2];

    printf("=== %s ===\n", rev->title);

    prepare_stacks(&stacks, rev);
    prepare_heap(&heap, rev);
    prepare_energy(&energy, rev);
    prepare_rail(&rail, rev);
    prepare_thermal(&thermal, rev);
    prepare_sections(sections, rev);

    const budget_monitor_t monitor = {
        .stacks        = &stacks,
        .heap          = &heap,
        .rail          = &rail,
        .thermal       = &thermal,
        .energy        = &energy,
        .sections      = sections,
        .section_count = sizeof sections / sizeof sections[0],
        .flash = {
            .total_bytes      = rev->flash_total_kib * KIB,
            .sector_bytes     = 2u * KIB,
            .bootloader_bytes = 32u * KIB,
            .nvs_bytes        = 32u * KIB,
            .image_bytes      = 380u * KIB
        },
        .limits = {
            .heap = {
                .min_free_bytes    = 8u * KIB,
                .min_largest_bytes = 2u * KIB /* найтовстіший мережевий буфер */
            },
            .battery_mah    = 2000u, /* літієвий елемент 2000 мА·год */
            .required_hours = 8760u  /* рік автономності за технічним завданням */
        }
    };

    budget_report_t report;
    budget_monitor_run(&monitor, &report);

    char text[1024];
    budget_report_format(&report, text, sizeof text);
    fputs(text, stdout);
    putchar('\n');

    return budget_monitor_action(report.flags);
}

int main(void)
{
    const revision_t revisions[] = {
        {
            .title               = "Ревізія A: LDO, 512 КБ Flash, цикл 60 с",
            .regulator_loss_mw   = 870u,  /* (12 - 3.3) В * 100 мА */
            .bulk_uf             = 100u,
            .radio_stack_bytes   = 1024u,
            .heap_churn          = true,
            .flash_total_kib     = 512u,
            .sleep_ms            = 59200u,
            .section_deadline_us = 5u
        },
        {
            .title               = "Ревізія B: Buck 92 %, 1 МБ Flash, цикл 10 хв",
            .regulator_loss_mw   = 29u,   /* втрати імпульсного перетворювача */
            .bulk_uf             = 470u,
            .radio_stack_bytes   = 2048u,
            .heap_churn          = false,
            .flash_total_kib     = 1024u,
            .sleep_ms            = 599200u,
            .section_deadline_us = 5000u
        }
    };

    budget_action_t final_action = BUDGET_ACTION_RUN;
    for (size_t i = 0; i < sizeof revisions / sizeof revisions[0]; ++i) {
        final_action = audit_revision(&revisions[i]);
    }

    /* Плата, яка після аудиту не виходить у штатний режим, у серію не йде. */
    return (final_action == BUDGET_ACTION_RUN) ? 0 : 1;
}
