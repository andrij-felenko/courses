#include "board_sim.h"

#include "board.h"

#define VIN_NOMINAL_MV   12000u
#define VIN_COLLAPSED_MV  7800u
#define PGOOD_MIN_VIN_MV  9000u  /* нижче Buck зривається, PGOOD падає */

#define CORE_RAMP_MS      2u     /* м'який старт I ступеня */
#define IO_RAMP_MS        3u     /* LDO DVDD */
#define PERIPH_RAMP_MS    3u     /* t_r ключа з керованим dV/dt */

typedef struct {
    bool enable;
    uint32_t since_en_ms;
    uint32_t ramp_ms;
    bool dead;
} sim_rail_t;

static struct {
    sim_scenario_t sc;
    uint32_t now_ms;
    sim_rail_t core;
    sim_rail_t io;
    sim_rail_t periph;
    bool reset_asserted;
    bool bus_active;
    uint32_t leak_ms;
} g;

static void rail_set(sim_rail_t *r, bool on)
{
    if (r->enable != on) {
        r->enable = on;
        r->since_en_ms = 0;
    }
}

static void rail_advance(sim_rail_t *r, uint32_t ms)
{
    if (r->enable && r->since_en_ms < UINT32_MAX - ms) {
        r->since_en_ms += ms;
    }
}

static bool rail_up(const sim_rail_t *r)
{
    return r->enable && !r->dead && r->since_en_ms >= r->ramp_ms;
}

void sim_load(const sim_scenario_t *scenario)
{
    const sim_rail_t core = { false, 0, CORE_RAMP_MS, scenario->core_rail_dead };
    const sim_rail_t io = { false, 0, IO_RAMP_MS, scenario->io_rail_dead };
    const sim_rail_t periph = { false, 0, PERIPH_RAMP_MS, false };

    g.sc = *scenario;
    g.now_ms = 0;
    g.core = core;
    g.io = io;
    g.periph = periph;
    g.reset_asserted = true;
    g.bus_active = false;
    g.leak_ms = 0;
}

void sim_advance(uint32_t ms)
{
    /* Витік рахуємо за фактом стану на початку кроку: піни активні,
     * а VCC периферії вже (або ще) немає. */
    if (g.bus_active && !rail_up(&g.periph)) {
        g.leak_ms += ms;
    }

    g.now_ms += ms;
    rail_advance(&g.core, ms);
    rail_advance(&g.io, ms);
    rail_advance(&g.periph, ms);
}

uint32_t sim_now_ms(void)
{
    return g.now_ms;
}

uint32_t sim_leak_ms(void)
{
    return g.leak_ms;
}

/* --- реалізація контракту board.h --- */

void board_core_rail_en(bool on)
{
    rail_set(&g.core, on);
}

void board_io_rail_en(bool on)
{
    rail_set(&g.io, on);
}

void board_periph_switch_en(bool on)
{
    rail_set(&g.periph, on);
}

void board_reset_assert(bool asserted)
{
    g.reset_asserted = asserted;
}

void board_bus_pins_isolate(void)
{
    g.bus_active = false;
}

void board_bus_pins_activate(void)
{
    g.bus_active = true;
}

uint16_t board_vin_mv(void)
{
    uint32_t v = VIN_NOMINAL_MV;

    if (g.sc.vin_collapse_at_ms != 0u && g.now_ms >= g.sc.vin_collapse_at_ms) {
        v = VIN_COLLAPSED_MV;
    }
    /* Кидок зарядного струму ємності навантаження просаджує вхід рівно на
     * час наростання ключа. */
    if (g.periph.enable && g.periph.since_en_ms < g.periph.ramp_ms) {
        v = (v > g.sc.periph_inrush_mv) ? (v - g.sc.periph_inrush_mv) : 0u;
    }
    return (uint16_t)v;
}

bool board_core_pgood(void)
{
    return rail_up(&g.core) && board_vin_mv() >= PGOOD_MIN_VIN_MV;
}

bool board_io_pgood(void)
{
    /* DVDD живиться з першого ступеня: без нього PGOOD не з'явиться. */
    return board_core_pgood() && rail_up(&g.io);
}

bool board_fault_irq(void)
{
    if (g.sc.overcurrent_at_ms == 0u || g.now_ms < g.sc.overcurrent_at_ms) {
        return false;
    }
    return g.periph.enable; /* ключ уже знятий — аварії більше немає */
}
