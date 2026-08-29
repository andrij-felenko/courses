/* main.c — автономний датчик: раз на хвилину прокинутися на кілька мілісекунд,
 * зміряти температуру й повернутися у Stop2 зі струмом одиниць мікроампер.
 *
 * Уся цінність тут не в вимірі, а в тому, що між вимірами плата справді спить:
 * цикл виходить із сну, робить роботу й проходить повний автомат присипляння.
 */
#include <stdbool.h>
#include <stdint.h>

#include "debugctl.h"
#include "i2c.h"
#include "lowpower.h"
#include "pins.h"
#include "regs.h"

#define SENSOR_ADDR7   0x48u   /* LM75-сумісний термометр на комутованій шині */
#define SENSOR_REG_TMP 0x00u
#define SLEEP_SECONDS  60u

#define FAULT_I2C          (1u << 0)
#define FAULT_BUS_STUCK    (1u << 1)
#define FAULT_RAIL_POWERED (1u << 2)
#define FAULT_FLOATING     (1u << 3)
#define FAULT_PROBE        (1u << 4)

/* Показання зберігаємо в резервному регістрі RTC: він живе через Stop2
 * і не коштує ані мікроампера. Передавання по радіо — тема іншого кроку. */
static void store_sample(int16_t half_degrees, uint32_t faults)
{
    RTC_BKP0R = (uint32_t)(uint16_t)half_degrees;
    RTC_BKP1R = faults;
}

/* LM75: два байти, знакове значення в старших дев'яти бітах, крок 0.5 °C. */
static int16_t decode_lm75(const uint8_t raw[2])
{
    const int16_t word = (int16_t)(((uint16_t)raw[0] << 8) | raw[1]);
    return (int16_t)(word >> 7);
}

static uint32_t measure(int16_t *half_degrees)
{
    uint8_t raw[2] = { 0, 0 };
    uint32_t faults = 0;

    board_rail_on();

    i2c_err_t err = i2c1_init();
    if (err == I2C_ERR_STUCK) {
        /* Раб тримає SDA внизу. Поки так, дві підтяжки по 10 кОм палять
         * понад 600 мкА цілу хвилину паузи — це гірше за втрачений вимір. */
        faults |= FAULT_BUS_STUCK;
    } else if (err != I2C_OK) {
        faults |= FAULT_I2C;
    } else {
        err = i2c1_read_reg(SENSOR_ADDR7, SENSOR_REG_TMP, raw, 2u);
        if (err == I2C_OK) {
            *half_degrees = decode_lm75(raw);
        } else {
            faults |= FAULT_I2C;
            if (i2c1_bus_stuck() && i2c1_bus_recover() != I2C_OK) {
                faults |= FAULT_BUS_STUCK;
            }
        }
    }

    i2c1_deinit();
    return faults;
}

/* Індикація вмикається лише під зондом: у полі кожен спалах — це десятки
 * мікроампер·годин, яких датчик собі дозволити не може. */
static void report(uint32_t faults)
{
    if (faults == 0u || !debug_probe_attached()) {
        return;
    }
    for (unsigned i = 0; i < 3u; ++i) {
        board_led(true);
        board_delay_ms(60);
        board_led(false);
        board_delay_ms(60);
    }
}

int main(void)
{
    board_clocks_init();
    board_pins_init();

    const bool have_clock = (lowpower_rtc_init() == SLEEP_OK);
    if (!have_clock) {
        /* Без LSE немає чим відміряти хвилину. Кнопка лишається єдиним
         * джерелом пробудження — спимо до неї, а не крутимо порожній цикл. */
        for (;;) {
            int16_t half_degrees = 0;
            const uint32_t faults = measure(&half_degrees);
            store_sample(half_degrees, faults);
            (void)lowpower_enter_stop2(0u);
        }
    }

    for (;;) {
        int16_t half_degrees = 0;
        uint32_t faults = measure(&half_degrees);

        const sleep_err_t err = lowpower_enter_stop2(SLEEP_SECONDS);
        switch (err) {
        case SLEEP_ERR_RAIL_POWERED:
            faults |= FAULT_RAIL_POWERED;
            break;
        case SLEEP_ERR_FLOATING_PINS:
            faults |= FAULT_FLOATING;
            break;
        case SLEEP_ERR_PROBE_ATTACHED:
            faults |= FAULT_PROBE;
            break;
        default:
            break;
        }

        store_sample(half_degrees, faults);

        if (lowpower_last_wake_source() == WAKE_BUTTON) {
            /* Натиснута кнопка — єдиний випадок, коли спалах виправданий. */
            board_led(true);
            board_delay_ms(30);
            board_led(false);
        }
        report(faults);
    }
}
