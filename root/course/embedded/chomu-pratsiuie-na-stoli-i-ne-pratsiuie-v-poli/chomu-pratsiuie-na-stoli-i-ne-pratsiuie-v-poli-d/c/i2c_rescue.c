/* i2c_rescue.c — дев'ять тактів, умова STOP і облік невдач. */

#include "fault_log.h"
#include "i2c_rescue.h"
#include "platform.h"

#define BIT_HALF_PERIOD_US 5u /* ≈100 кГц під час ручного тактування */
#define RECOVER_CLOCKS 9u     /* вісім бітів байта плюс такт квитанції */

void i2c_bus_init(i2c_bus_t *bus, uint8_t address)
{
    if (bus == 0) {
        return;
    }
    bus->address = address;
    bus->fail_streak = 0u;
    bus->recover_streak = 0u;
    bus->recover_total = 0u;
    plat_i2c_init();
}

static bool bus_recover(i2c_bus_t *bus)
{
    plat_i2c_pins_take();

    /* Відпускаємо обидві лінії й дивимося, чи підняла їх підтяжка. */
    plat_i2c_sda_write(true);
    plat_i2c_scl_write(true);
    plat_delay_us(BIT_HALF_PERIOD_US * 2u);

    bool released = plat_i2c_sda_read();

    for (uint8_t i = 0u; i < RECOVER_CLOCKS && !released; i++) {
        /* Кожен такт витягує з раба один зайвий біт. Рано чи пізно він
         * доходить до кінця байта, бачить заперечення й відпускає SDA. */
        plat_i2c_scl_write(false);
        plat_delay_us(BIT_HALF_PERIOD_US);
        plat_i2c_scl_write(true);
        plat_delay_us(BIT_HALF_PERIOD_US);

        if (!plat_i2c_scl_read()) {
            /* SCL не піднявся навіть відпущений: це вже не завислий раб,
             * а замикання лінії або обірвана підтяжка. Тактувати далі марно. */
            break;
        }
        released = plat_i2c_sda_read();
    }

    if (released) {
        /* Умова STOP: SDA з нуля в одиницю при високому SCL. Без неї раб
         * лишиться вважати, що транзакція триває, і зависне знову на
         * першому ж нашому START. */
        plat_i2c_sda_write(false);
        plat_delay_us(BIT_HALF_PERIOD_US);
        plat_i2c_scl_write(true);
        plat_delay_us(BIT_HALF_PERIOD_US);
        plat_i2c_sda_write(true);
        plat_delay_us(BIT_HALF_PERIOD_US * 2u);
    }

    plat_i2c_pins_release(); /* ніжки назад під периферію, блок скинуто */
    bus->recover_total++;
    fault_log_bump_recovery();

    return released;
}

bus_health_t i2c_bus_check(i2c_bus_t *bus)
{
    if (bus == 0) {
        return BUS_HEALTH_DEAD;
    }

    const plat_i2c_status_t st = plat_i2c_probe(bus->address);
    if (st == PLAT_I2C_OK) {
        bus->fail_streak = 0u;
        bus->recover_streak = 0u;
        return BUS_HEALTH_OK;
    }

    bus->fail_streak++;

    if (st == PLAT_I2C_NACK) {
        /* Лінії живі, просто ніхто не озвався. Тактувати тут нічого:
         * або давач ще піднімається після власного скидання, або його
         * вже немає — обидва випадки лікуються не порятунком шини. */
        return BUS_HEALTH_SILENT;
    }

    /* PLAT_I2C_BUSY чи PLAT_I2C_TIMEOUT — лінію тримають унизу. */
    if (!bus_recover(bus)) {
        bus->recover_streak++;
        return BUS_HEALTH_DEAD;
    }

    if (plat_i2c_probe(bus->address) == PLAT_I2C_OK) {
        bus->fail_streak = 0u;
        bus->recover_streak = 0u;
        return BUS_HEALTH_RECOVERED;
    }

    /* SDA відпустили, але раб усе одно мовчить: розчепірили лінію, не
     * полагодивши причину. Лічильник поспіль підкаже головному циклу,
     * коли перестати пробувати те саме. */
    bus->recover_streak++;
    return BUS_HEALTH_STUCK;
}

bool i2c_bus_read(i2c_bus_t *bus, uint8_t reg, uint8_t *buf, uint8_t len)
{
    if (bus == 0) {
        return false;
    }

    if (plat_i2c_read_reg(bus->address, reg, buf, len) == PLAT_I2C_OK) {
        bus->fail_streak = 0u;
        return true;
    }

    bus->fail_streak++;
    return false;
}
