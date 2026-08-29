#include "sim_device.h"
#include "dev_driver.h"
#include "platform.h"

#include <stdio.h>
#include <string.h>

#define SIM_REG_COUNT      (0x20U)
#define SIM_RESET_CORE_MS  (5U) /* доки ядро в скиданні, чип не відповідає взагалі */
#define SIM_STUCK_BITS     (6U) /* ведений обірвався на шостому біті байта */
#define SIM_ODR_MAX        (0x50U) /* більші коди ODR/DLPF кремній не приймає */

typedef struct {
    uint32_t now;
    sim_faults_t faults;
    bool cut_done;
    bool restore_done;

    bool powered;
    uint32_t por_ready_ms;  /* до цієї миті V_DD ще наростає */
    bool reset_pending;
    uint32_t core_up_ms;    /* до цієї миті цифрове ядро в скиданні */

    bool sda_stuck;
    unsigned stuck_bits;    /* скільки тактів SCL винен ведений, щоб відпустити лінію */
    unsigned recoveries;
    unsigned scl_edges;

    uint8_t regs[SIM_REG_COUNT];
} sim_state_t;

static sim_state_t g_sim;

static void load_defaults(void)
{
    memset(g_sim.regs, 0, sizeof g_sim.regs);
    g_sim.regs[REG_CHIP_ID] = EXPECTED_CHIP_ID;
    g_sim.regs[REG_RESET_CTRL] = BIT_DEVICE_READY;
}

sim_faults_t sim_faults_default(void)
{
    sim_faults_t f;
    f.power_off_at_ms = SIM_NEVER;
    f.power_on_at_ms = SIM_NEVER;
    f.por_ramp_ms = 2U; /* здорова плата: V_DD наростає за пару мілісекунд */
    return f;
}

void sim_device_reset(const sim_faults_t *faults)
{
    memset(&g_sim, 0, sizeof g_sim);
    g_sim.faults = *faults;
    g_sim.powered = true;
    g_sim.por_ready_ms = faults->por_ramp_ms;
    load_defaults();
}

static void power_down(void)
{
    g_sim.powered = false;
    /* Живлення зникло посеред байта: ведений так і лишив SDA притиснутою. */
    g_sim.sda_stuck = true;
    g_sim.stuck_bits = SIM_STUCK_BITS;
}

static void power_up(void)
{
    g_sim.powered = true;
    g_sim.por_ready_ms = g_sim.now + g_sim.faults.por_ramp_ms;
    g_sim.reset_pending = false;
    load_defaults();
}

void sim_tick(void)
{
    g_sim.now++;

    if (!g_sim.cut_done && g_sim.now >= g_sim.faults.power_off_at_ms) {
        g_sim.cut_done = true;
        power_down();
    }
    if (g_sim.cut_done && !g_sim.restore_done && g_sim.now >= g_sim.faults.power_on_at_ms) {
        g_sim.restore_done = true;
        power_up();
    }
    /* Внутрішній цикл перезавантаження добіг кінця: біт SW_RESET самоочистився. */
    if (g_sim.powered && g_sim.reset_pending && g_sim.now >= g_sim.core_up_ms) {
        g_sim.reset_pending = false;
        load_defaults();
    }
}

uint32_t sim_now(void)      { return g_sim.now; }
unsigned sim_recoveries(void) { return g_sim.recoveries; }
bool sim_sda_stuck(void)    { return g_sim.sda_stuck; }

/* --- реалізація контракту platform.h --- */

uint32_t platform_get_millis(void)
{
    return g_sim.now;
}

/* Спільна для читання й запису перевірка: чи взагалі можлива транзакція. */
static bus_status_t bus_precheck(uint8_t dev_addr)
{
    if (g_sim.sda_stuck) {
        return BUS_ERR_TIMEOUT; /* SDA в нулі — START не сформується */
    }
    if (!g_sim.powered) {
        power_down(); /* спроба звернутися до знеструмленого веденого валить шину */
        return BUS_ERR_NACK;
    }
    if (dev_addr != DEV_I2C_ADDR) {
        return BUS_ERR_NACK;
    }
    if (g_sim.now < g_sim.por_ready_ms) {
        return BUS_ERR_NACK; /* V_DD ще наростає */
    }
    if (g_sim.reset_pending && g_sim.now < g_sim.core_up_ms) {
        return BUS_ERR_NACK; /* генератор зупинено на час перезавантаження */
    }
    return BUS_OK;
}

bus_status_t platform_i2c_write(uint8_t dev_addr, uint8_t reg, uint8_t val)
{
    bus_status_t st = bus_precheck(dev_addr);
    if (st != BUS_OK) {
        return st;
    }
    if (reg >= SIM_REG_COUNT || reg == REG_CHIP_ID) {
        return BUS_ERR_NACK; /* неіснуючий або суто читальний регістр */
    }

    if (reg == REG_RESET_CTRL && (val & BIT_SW_RESET) != 0U) {
        g_sim.reset_pending = true;
        g_sim.core_up_ms = g_sim.now + SIM_RESET_CORE_MS;
        g_sim.regs[REG_RESET_CTRL] = BIT_SW_RESET; /* біт тримається до кінця циклу */
        return BUS_OK;
    }

    if (reg == REG_ODR_FILTER && (val & 0x7FU) > SIM_ODR_MAX) {
        /* Заборонена комбінація ODR/DLPF: кремній її мовчки ігнорує.
           Транзакція успішна, а регістр лишається нульовим — рівно той випадок,
           заради якого й існує Read-Back. */
        g_sim.regs[REG_ODR_FILTER] = 0x00U;
        return BUS_OK;
    }

    g_sim.regs[reg] = val;
    return BUS_OK;
}

bus_status_t platform_i2c_read(uint8_t dev_addr, uint8_t reg, uint8_t *val)
{
    bus_status_t st = bus_precheck(dev_addr);
    if (st != BUS_OK) {
        return st;
    }
    if (reg >= SIM_REG_COUNT) {
        return BUS_ERR_NACK;
    }

    *val = g_sim.regs[reg];
    if (reg == REG_ODR_FILTER) {
        /* Біт 7 цього регістра — статус DRDY, він читається одиницею незалежно
           від записаної конфігурації. Побайтове порівняння тут завжди програє. */
        *val |= BIT_DATA_READY;
    }
    return BUS_OK;
}

void platform_bus_recover(void)
{
    /* На залізі SCL переводять у GPIO open-drain і женуть до дев'яти тактів,
       поки ведений не дотактує зависле слово й не відпустить SDA. */
    for (unsigned i = 0U; i < 9U; ++i) {
        g_sim.scl_edges++;
        if (g_sim.stuck_bits > 0U) {
            g_sim.stuck_bits--;
        }
    }
    if (g_sim.stuck_bits == 0U) {
        g_sim.sda_stuck = false;
    }
    g_sim.recoveries++;
}

void platform_notify_fault(const char *reason)
{
    /* На виробі тут знеструмлюють приводи й піднімають аварійний прапорець. */
    printf("       [FAULT-SAFE] %s\n", reason);
}
