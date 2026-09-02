#include "platform.h"
#include "sensor.h"

#define RECOVERY_CLOCKS      9U
#define RECOVERY_HALF_US     5U   /* пів-період ручного тактування, ~100 кГц */
#define POWER_DISCHARGE_MS   50U  /* час на розряд декаплінгу, інакше POR не спрацює */
#define POWER_REBOOT_MS      40U  /* t_ramp + t_boot після повернення живлення */
#define NRST_RECOVER_MS      10U

/*
 * Ведений, збитий завадою посеред байта, тримає SDA у нулі й блокує всю шину.
 * Порядок ударів наростає: ручне тактування -> апаратний NRST -> перезапуск
 * живлення. Кожен наступний крок робиться лише тоді, коли попередній не поміг.
 */
void i2c_bus_recover(uint8_t dev_addr)
{
    hw_i2c_pins_to_gpio();
    hw_sda_set(true); /* відпускаємо SDA: тепер її тримає лише ведений */

    for (unsigned i = 0; i < RECOVERY_CLOCKS && !hw_sda_read(); ++i) {
        hw_scl_set(false);
        delay_us(RECOVERY_HALF_US);
        hw_scl_set(true);
        delay_us(RECOVERY_HALF_US);
    }

    bool line_free = hw_sda_read();
    if (line_free) {
        /* Явна умова STOP: SDA 0 -> 1 при високому SCL */
        hw_sda_set(false);
        delay_us(RECOVERY_HALF_US);
        hw_scl_set(true);
        delay_us(RECOVERY_HALF_US);
        hw_sda_set(true);
        delay_us(RECOVERY_HALF_US);
    }

    hw_i2c_pins_to_peripheral();
    if (line_free) {
        return;
    }

    if (hw_has_nrst(dev_addr)) {
        hw_nrst_pulse(dev_addr);
        delay_ms(NRST_RECOVER_MS);
        return;
    }

    hw_power_rail_enable(false);
    delay_ms(POWER_DISCHARGE_MS);
    hw_power_rail_enable(true);
    delay_ms(POWER_REBOOT_MS);
}
