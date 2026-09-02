#include <stdio.h>
#include <string.h>

#include "platform.h"
#include "sensor.h"

/*
 * Хостова модель стенда: два місця на шині I2C, спільна лінія живлення.
 * Модель відтворює саме ті явища, через які ініціалізація й буває складною:
 *   - до кінця t_boot чип не підтверджує адресу (NACK);
 *   - команда SW_RESET на кілька мілісекунд глушить інтерфейсний блок;
 *   - RO-розряди (DRDY, FILT_RDY) і фабрична одиниця живуть у робочих регістрах;
 *   - у робочому режимі конфігураційні регістри заблоковані від запису;
 *   - завада спотворює один запис і збиває автомат інтерфейсу на SDA.
 */

#define REG_COUNT   0x20U
#define CHIP_COUNT  2U
#define SW_RESET_MS 8U

typedef struct {
    uint8_t  addr;
    bool     mounted;      /* чи справді змонтований на платі */
    bool     has_nrst;     /* чи розведено вивід скидання */
    uint32_t boot_ms;      /* власний t_boot кремнію */
    uint8_t  regs[REG_COUNT];
    uint32_t ready_at;     /* коли інтерфейс почне відповідати */
    uint32_t settled_at;   /* коли фільтр вийде на режим */
    int      glitch_writes; /* скільки записів попереду зіпсує завада */
    bool     desync;       /* автомат інтерфейсу збитий і от-от сяде на SDA */
} chip_t;

static chip_t   g_chips[CHIP_COUNT];
static uint32_t g_millis;
static uint32_t g_micros_acc;
static bool     g_rail_on;
static bool     g_sda_low;
static int      g_stuck_clocks;
static bool     g_pins_gpio;
static bool     g_scl_level = true;
static unsigned g_watchdog_kicks;

static chip_t *find_chip(uint8_t addr)
{
    for (unsigned i = 0; i < CHIP_COUNT; ++i) {
        if (g_chips[i].addr == addr) {
            return &g_chips[i];
        }
    }
    return NULL;
}

static void chip_boot(chip_t *chip, uint32_t delay)
{
    memset(chip->regs, 0, sizeof(chip->regs));
    chip->regs[REG_WHO_AM_I] = SENSOR_WHO_AM_I_VALUE;
    chip->regs[REG_RANGE] = 0x40U; /* зарезервований біт 6 завжди читається як 1 */
    chip->ready_at = g_millis + delay;
    chip->settled_at = UINT32_MAX;
    chip->desync = false;
}

void sim_reset_board(void)
{
    memset(g_chips, 0, sizeof(g_chips));
    g_millis = 0;
    g_micros_acc = 0;
    g_rail_on = false;
    g_sda_low = false;
    g_stuck_clocks = 0;
    g_pins_gpio = false;
    g_scl_level = true;
    g_watchdog_kicks = 0;

    /* Гіроскоп на місці, NRST розведений; на першу конфігурацію ловить заваду */
    g_chips[0].addr = 0x6A;
    g_chips[0].mounted = true;
    g_chips[0].has_nrst = true;
    g_chips[0].boot_ms = 30;
    g_chips[0].glitch_writes = 1;

    /* Місце давача вологості на цій ревізії плати не запаяне */
    g_chips[1].addr = 0x6B;
    g_chips[1].mounted = false;
    g_chips[1].boot_ms = 10;
}

static int bus_precheck(uint8_t addr, chip_t **out)
{
    if (g_sda_low) {
        return BUS_ERR_STUCK;
    }
    if (!g_rail_on) {
        return BUS_ERR_NACK;
    }
    chip_t *chip = find_chip(addr);
    if (chip == NULL || !chip->mounted) {
        return BUS_ERR_NACK; /* ніхто не тягне SDA на 9-му такті */
    }
    if (g_millis < chip->ready_at) {
        return BUS_ERR_NACK; /* усе ще всередині POR або SW-скидання */
    }
    *out = chip;
    return BUS_OK;
}

int i2c_read_reg(uint8_t dev_addr, uint8_t reg, uint8_t *out_value)
{
    chip_t *chip = NULL;
    int rc = bus_precheck(dev_addr, &chip);
    if (rc != BUS_OK) {
        return rc;
    }
    if (reg >= REG_COUNT) {
        return BUS_ERR_NACK;
    }

    uint8_t value = chip->regs[reg];
    if (reg == REG_STATUS) {
        value = BIT_STATUS_READY;
        if (g_millis >= chip->settled_at) {
            value |= BIT_STATUS_DRDY;
        }
    } else if (reg == REG_FILTER && g_millis >= chip->settled_at) {
        value |= BIT_FILTER_READY; /* апаратний RO-прапорець поверх конфігурації */
    }
    *out_value = value;

    if (chip->desync) {
        /* Збитий автомат добиває поточну транзакцію і сідає на лінію даних */
        chip->desync = false;
        g_sda_low = true;
        g_stuck_clocks = 3;
    }
    return BUS_OK;
}

int i2c_write_reg(uint8_t dev_addr, uint8_t reg, uint8_t value)
{
    chip_t *chip = NULL;
    int rc = bus_precheck(dev_addr, &chip);
    if (rc != BUS_OK) {
        return rc;
    }
    if (reg >= REG_COUNT) {
        return BUS_ERR_NACK;
    }

    /* RO-регістри підтверджують байт, але не зберігають його */
    if (reg == REG_WHO_AM_I || reg == REG_STATUS) {
        return BUS_OK;
    }

    if (reg == REG_RESET_CTRL && (value & BIT_SW_RESET) != 0) {
        chip_boot(chip, SW_RESET_MS);
        return BUS_OK;
    }

    if (chip->glitch_writes > 0) {
        /* Завада EMI: байт прийнято з ACK, у пам'ять ліг зі спотвореним бітом */
        chip->glitch_writes--;
        chip->regs[reg] = (uint8_t)(value ^ 0x02U);
        chip->desync = true;
        return BUS_OK;
    }

    /* Конфігурація заблокована, поки чип не переведений у Standby */
    if (reg >= REG_INT_CFG && reg <= REG_INT_EN &&
        (chip->regs[REG_PWR] & PWR_MODE_CARE_MASK) != PWR_MODE_STANDBY) {
        return BUS_OK; /* ACK є, запису немає — це і ловить Read-Back */
    }

    if (reg == REG_RANGE) {
        chip->regs[reg] = (uint8_t)((value & 0x3FU) | 0x40U);
    } else if (reg == REG_FILTER) {
        chip->regs[reg] = (uint8_t)(value & 0x7FU);
    } else {
        chip->regs[reg] = value;
        if (reg == REG_PWR) {
            chip->settled_at = ((value & PWR_MODE_CARE_MASK) == PWR_MODE_NORMAL)
                                   ? g_millis + 20U
                                   : UINT32_MAX;
        }
    }
    return BUS_OK;
}

uint32_t platform_get_millis(void) { return g_millis; }

void delay_ms(uint32_t ms) { g_millis += ms; }

void delay_us(uint32_t us)
{
    g_micros_acc += us;
    g_millis += g_micros_acc / 1000U;
    g_micros_acc %= 1000U;
}

void hw_watchdog_kick(void) { g_watchdog_kicks++; }

void hw_power_rail_enable(bool on)
{
    g_rail_on = on;
    g_sda_low = false; /* зняте живлення заразом відпускає лінію */
    g_stuck_clocks = 0;
    if (!on) {
        return;
    }
    for (unsigned i = 0; i < CHIP_COUNT; ++i) {
        if (g_chips[i].mounted) {
            chip_boot(&g_chips[i], g_chips[i].boot_ms);
        }
    }
}

void hw_i2c_pins_to_gpio(void) { g_pins_gpio = true; }
void hw_i2c_pins_to_peripheral(void) { g_pins_gpio = false; }

void hw_scl_set(bool level)
{
    if (!g_pins_gpio) {
        return;
    }
    if (g_scl_level && !level && g_stuck_clocks > 0) {
        /* Спад SCL: ведений зсуває наступний біт застряглого байта */
        if (--g_stuck_clocks == 0) {
            g_sda_low = false;
        }
    }
    g_scl_level = level;
}

void hw_sda_set(bool level) { (void)level; }

bool hw_sda_read(void) { return !g_sda_low; }

bool hw_has_nrst(uint8_t dev_addr)
{
    const chip_t *chip = find_chip(dev_addr);
    return chip != NULL && chip->has_nrst;
}

void hw_nrst_pulse(uint8_t dev_addr)
{
    chip_t *chip = find_chip(dev_addr);
    if (chip == NULL || !chip->mounted) {
        return;
    }
    g_sda_low = false;
    g_stuck_clocks = 0;
    chip_boot(chip, chip->boot_ms);
}

void hw_fault_led(bool on) { printf("   [світлодіод несправності %s]\n", on ? "увімкнено" : "вимкнено"); }

void hw_actuators_disable(void) { printf("   [силові приводи знеструмлено]\n"); }
