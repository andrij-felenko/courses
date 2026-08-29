/* Шини до периферії: спершу примусово вивільняємо I2C, далі звіряємо
 * ідентифікатори мікросхем. Тестер ніколи не довіряє тому, що шина вільна. */

#include "fct.h"
#include "hal.h"

#define I2C_TIMEOUT_US   5000u
#define SPI_TIMEOUT_US   8000u
#define I2C_HALF_BIT_US  5u      /* ~100 кГц у режимі bit-banging */

typedef struct {
    const char *name;
    uint8_t addr7;
    uint8_t id_reg;
    uint8_t id_expected;
} i2c_device_t;

static const i2c_device_t k_devices[] = {
    {"ICM-42688 IMU", 0x68, 0x75, 0x47},  /* WHO_AM_I */
    {"BMP390 baro",   0x77, 0x00, 0x60}   /* CHIP_ID  */
};

/* Дев'ять тактів SCL вивільняють веденого, що завис посеред видачі байта
 * й тримає SDA притиснутою до землі. Робиться ДО ініціалізації периферії:
 * апаратний контролер у стані Bus Busy не дасть навіть почати транзакцію. */
static bool i2c_bus_recover(void)
{
    hal_i2c_pins_to_gpio();
    hal_i2c_sda_write(true);
    hal_i2c_scl_write(true);
    hal_delay_us(I2C_HALF_BIT_US);

    bool released = hal_i2c_sda_read();
    for (int pulse = 0; pulse < 9 && !released; pulse++) {
        hal_i2c_scl_write(false);
        hal_delay_us(I2C_HALF_BIT_US);
        hal_i2c_scl_write(true);
        hal_delay_us(I2C_HALF_BIT_US);
        released = hal_i2c_sda_read();
    }

    /* Стоп-умова: SDA 0→1 при високому SCL — ведений повертається в idle. */
    hal_i2c_scl_write(false);
    hal_i2c_sda_write(false);
    hal_delay_us(I2C_HALF_BIT_US);
    hal_i2c_scl_write(true);
    hal_delay_us(I2C_HALF_BIT_US);
    hal_i2c_sda_write(true);
    hal_delay_us(I2C_HALF_BIT_US);

    released = hal_i2c_sda_read();
    hal_i2c_pins_to_peripheral();
    hal_i2c_reinit();
    return released;
}

void test_i2c_devices(fct_verdict_t *v)
{
    if (!i2c_bus_recover()) {
        /* Дев'ять тактів не допомогли — SDA замкнена на землю доріжкою
         * або мертвим чипом, а не завислою транзакцією. */
        fct_fail(v, FCT_BUS_LOCKED, "SDA лишилася низькою після 9 тактів SCL");
        return;
    }

    const size_t count = sizeof(k_devices) / sizeof(k_devices[0]);
    for (size_t i = 0; i < count; i++) {
        const i2c_device_t *dev = &k_devices[i];
        uint8_t id = 0;

        if (!hal_i2c_read_reg(dev->addr7, dev->id_reg, &id, I2C_TIMEOUT_US)) {
            fct_fail_at(v, FCT_TIMEOUT, "Ведений не квитує адресу (NACK)",
                        dev->addr7, "addr");
            return;
        }
        if (id != dev->id_expected) {
            fct_fail_at(v, FCT_INVALID_ID, "Чужий або нечитний ідентифікатор",
                        id, "id");
            return;
        }
        hal_watchdog_kick();
    }

    fct_pass(v, "Усі ведені відгукнулися своїм ID", (int32_t)count, "devices");
}

void test_spi_flash(fct_verdict_t *v)
{
    const uint8_t tx[4] = {0x9F, 0x00, 0x00, 0x00};  /* JEDEC Read ID */
    uint8_t rx[4] = {0};

    hal_spi_cs(true);
    bool ok = hal_spi_xfer(tx, rx, sizeof(tx), SPI_TIMEOUT_US);
    hal_spi_cs(false);

    if (!ok) {
        fct_fail(v, FCT_TIMEOUT, "SPI: обмін не завершився");
        return;
    }

    const uint8_t mfg = rx[1];
    const uint8_t type = rx[2];
    const uint8_t capacity = rx[3];

    /* 0x00 і 0xFF на всіх байтах — це не ідентифікатор, а обірваний MISO:
     * лінія притиснута до землі або підтягнута до живлення. */
    if ((mfg == 0x00 && type == 0x00 && capacity == 0x00) ||
        (mfg == 0xFF && type == 0xFF && capacity == 0xFF)) {
        fct_fail(v, FCT_BUS_LOCKED, "MISO застряг у 0/1: пайка або CS");
        return;
    }
    /* Очікуємо Winbond W25Q128: EF 40 18. */
    if (mfg != 0xEF || type != 0x40 || capacity != 0x18) {
        fct_fail_at(v, FCT_INVALID_ID, "Незнайомий JEDEC ID або інший об'єм",
                    ((int32_t)mfg << 16) | ((int32_t)type << 8) | capacity, "jedec");
        return;
    }

    /* 0x18 → 2^24 байт = 16 МіБ. */
    fct_pass(v, "W25Q128 відповів своїм JEDEC ID", 1 << (capacity - 20), "MiB");
}
