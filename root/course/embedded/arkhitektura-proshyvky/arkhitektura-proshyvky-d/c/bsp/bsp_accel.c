/* bsp/bsp_accel.c — приватна реалізація драйвера ADXL345.
 * Тут, і лише тут, живуть номери регістрів мікросхеми, ціна молодшого
 * розряду й повна будова дескриптора. Заголовок про них не знає, тож
 * заміна ADXL345 на LIS3DH — правка одного цього файла. */
#include "bsp/bsp_accel.h"

#include "hal/hal_time.h"

#include <math.h>
#include <string.h>

/* --- Карта регістрів ADXL345 (datasheet, розділ Register Map) --- */
#define ADXL345_REG_DEVID        0x00u
#define ADXL345_REG_BW_RATE      0x2Cu
#define ADXL345_REG_POWER_CTL    0x2Du
#define ADXL345_REG_DATA_FORMAT  0x31u
#define ADXL345_REG_DATAX0       0x32u
#define ADXL345_REG_FIFO_CTL     0x38u

#define ADXL345_DEVID_VALUE      0xE5u
#define ADXL345_RATE_100HZ       0x0Au
#define ADXL345_POWER_MEASURE    0x08u
#define ADXL345_POWER_STANDBY    0x00u
#define ADXL345_FORMAT_FULL_RES  0x08u
#define ADXL345_FIFO_BYPASS      0x00u

/* У режимі повної роздільності ціна розряду однакова для всіх діапазонів. */
#define ADXL345_LSB_PER_G        256.0f

#define BSP_ACCEL_MAGIC          0x41434C31u /* "ACL1" */

/* Повне визначення структури — приватне для цього файла. */
struct bsp_accel {
    uint32_t             magic;
    const hal_i2c_bus_t *bus;
    uint8_t              addr;
    bsp_accel_range_t    range;
    hal_i2c_status_t     last_error;
    uint32_t             last_read_ms;
    uint32_t             error_count;
};

_Static_assert(sizeof(struct bsp_accel) <= sizeof(bsp_accel_storage_t),
               "bsp_accel_storage_t замалий: збільште bytes[] у заголовку");

static bool handle_is_live(const struct bsp_accel *dev)
{
    return dev != 0 && dev->magic == BSP_ACCEL_MAGIC;
}

static bool write_checked(struct bsp_accel *dev, uint8_t reg, uint8_t value)
{
    const hal_i2c_status_t st = hal_i2c_write_reg(dev->bus, dev->addr, reg, value);
    if (st != HAL_I2C_OK) {
        dev->last_error = st;
        dev->error_count++;
        return false;
    }
    return true;
}

bsp_accel_t *bsp_accel_create(bsp_accel_storage_t *storage,
                              const hal_i2c_bus_t *bus,
                              uint8_t i2c_addr,
                              bsp_accel_range_t range)
{
    if (storage == 0 || !hal_i2c_bus_is_valid(bus)) {
        return 0;
    }

    struct bsp_accel *dev = (struct bsp_accel *)storage;
    memset(dev, 0, sizeof *dev);
    dev->bus        = bus;
    dev->addr       = i2c_addr;
    dev->range      = range;
    dev->last_error = HAL_I2C_OK;

    /* Мікросхема має відрекомендуватися. Якщо на цій адресі сидить хтось
     * інший (а на 0x53 залюбки сидить чужий давач), краще дізнатися це
     * тут, ніж на польових даних, які тихо брешуть. */
    uint8_t devid = 0u;
    const hal_i2c_status_t st =
        hal_i2c_read_reg(bus, i2c_addr, ADXL345_REG_DEVID, &devid);
    if (st != HAL_I2C_OK) {
        dev->last_error = st;
        return 0;
    }
    if (devid != ADXL345_DEVID_VALUE) {
        dev->last_error = HAL_I2C_ERR_BUS;
        return 0;
    }

    const uint8_t format =
        (uint8_t)(ADXL345_FORMAT_FULL_RES | ((uint8_t)range & 0x03u));

    dev->magic = BSP_ACCEL_MAGIC;
    if (!write_checked(dev, ADXL345_REG_POWER_CTL, ADXL345_POWER_STANDBY) ||
        !write_checked(dev, ADXL345_REG_DATA_FORMAT, format) ||
        !write_checked(dev, ADXL345_REG_BW_RATE, ADXL345_RATE_100HZ) ||
        !write_checked(dev, ADXL345_REG_FIFO_CTL, ADXL345_FIFO_BYPASS) ||
        !write_checked(dev, ADXL345_REG_POWER_CTL, ADXL345_POWER_MEASURE)) {
        dev->magic = 0u;
        return 0;
    }

    /* Перший вимір з'являється не раніше ніж через період перетворення. */
    hal_time_delay_ms(20u);
    return dev;
}

bool bsp_accel_read(bsp_accel_t *dev, bsp_accel_sample_t *out_sample)
{
    if (!handle_is_live(dev) || out_sample == 0) {
        return false;
    }

    uint8_t raw[6] = { 0u };
    const hal_i2c_status_t st =
        hal_i2c_read_regs(dev->bus, dev->addr, ADXL345_REG_DATAX0, raw, sizeof raw);
    if (st != HAL_I2C_OK) {
        dev->last_error = st;
        dev->error_count++;
        return false;
    }

    /* ADXL345 віддає осі молодшим байтом уперед, у доповняльному коді. */
    const int16_t x = (int16_t)((uint16_t)raw[0] | ((uint16_t)raw[1] << 8));
    const int16_t y = (int16_t)((uint16_t)raw[2] | ((uint16_t)raw[3] << 8));
    const int16_t z = (int16_t)((uint16_t)raw[4] | ((uint16_t)raw[5] << 8));

    out_sample->x_g = (float)x / ADXL345_LSB_PER_G;
    out_sample->y_g = (float)y / ADXL345_LSB_PER_G;
    out_sample->z_g = (float)z / ADXL345_LSB_PER_G;

    dev->last_read_ms = hal_time_now_ms();
    dev->last_error   = HAL_I2C_OK;
    return true;
}

float bsp_accel_vibration_g(const bsp_accel_sample_t *sample)
{
    if (sample == 0) {
        return 0.0f;
    }
    /* Модуль вектора мінус одиниця тяжіння: нерухомий давач у будь-якій
     * орієнтації дає нуль, а хитання підшипника — справжню амплітуду. */
    const float magnitude = sqrtf(sample->x_g * sample->x_g +
                                  sample->y_g * sample->y_g +
                                  sample->z_g * sample->z_g);
    return fabsf(magnitude - 1.0f);
}

hal_i2c_status_t bsp_accel_last_error(const bsp_accel_t *dev)
{
    return handle_is_live(dev) ? dev->last_error : HAL_I2C_ERR_ARG;
}

void bsp_accel_destroy(bsp_accel_t *dev)
{
    if (!handle_is_live(dev)) {
        return;
    }
    (void)hal_i2c_write_reg(dev->bus, dev->addr,
                            ADXL345_REG_POWER_CTL, ADXL345_POWER_STANDBY);
    /* Затираємо мітку: подальші виклики з цим покажчиком тихо відмовлять
     * замість того, щоб працювати з мертвим дескриптором. */
    dev->magic = 0u;
    dev->bus   = 0;
}
