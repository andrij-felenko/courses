/* ports/host_mock/mock_hal_i2c.c — імітація шини I2C у пам'яті хоста.
 * Мікросхема тут — це масив регістрів і кілька правил про те, як вона
 * відповідає. Драйвер BME280 не бачить різниці: він говорить у ту саму
 * таблицю операцій, що й на живій платі.
 *
 * Калібрувальні коефіцієнти взято з реального примірника BME280, а сирі
 * коди підібрано так, щоб формула компенсації давала близько 25 °C. */
#include "include/sys_config.h"
#include "ports/host_mock/host_port.h"

#include <string.h>

#define MOCK_REG_COUNT   256u

typedef struct {
    uint8_t          addr;
    bool             present;
    uint8_t          regs[MOCK_REG_COUNT];
    uint8_t          reg_ptr;
    hal_i2c_status_t inject_status;
    unsigned         inject_left;
} mock_device_t;

static mock_device_t g_bme280;
static mock_device_t g_adxl345;
static unsigned      g_transactions;
static bool          g_initialised;

/* --- Заповнення регістрів імітованих мікросхем --- */

static void put_u16(mock_device_t *dev, uint8_t reg, uint16_t value)
{
    dev->regs[reg]      = (uint8_t)(value & 0xFFu);
    dev->regs[reg + 1u] = (uint8_t)(value >> 8);
}

static void bme280_load_calibration(mock_device_t *dev)
{
    dev->regs[0xD0u] = 0x60u;   /* ідентифікатор саме BME280 */
    dev->regs[0xF3u] = 0x00u;   /* перетворення не триває */

    put_u16(dev, 0x88u, 28000u);            /* dig_T1 */
    put_u16(dev, 0x8Au, (uint16_t)26500);   /* dig_T2 */
    put_u16(dev, 0x8Cu, (uint16_t)50);      /* dig_T3 */

    put_u16(dev, 0x8Eu, 36477u);                    /* dig_P1 */
    put_u16(dev, 0x90u, (uint16_t)(int16_t)-10685); /* dig_P2 */
    put_u16(dev, 0x92u, (uint16_t)3024);            /* dig_P3 */
    put_u16(dev, 0x94u, (uint16_t)2855);            /* dig_P4 */
    put_u16(dev, 0x96u, (uint16_t)140);             /* dig_P5 */
    put_u16(dev, 0x98u, (uint16_t)(int16_t)-7);     /* dig_P6 */
    put_u16(dev, 0x9Au, (uint16_t)15500);           /* dig_P7 */
    put_u16(dev, 0x9Cu, (uint16_t)(int16_t)-14600); /* dig_P8 */
    put_u16(dev, 0x9Eu, (uint16_t)6000);            /* dig_P9 */

    dev->regs[0xA1u] = 75u;                 /* dig_H1 */
    put_u16(dev, 0xE1u, (uint16_t)350);     /* dig_H2 */
    dev->regs[0xE3u] = 0u;                  /* dig_H3 */
    /* dig_H4 = 302, dig_H5 = 50 — дванадцятибітні зі спільним байтом 0xE5 */
    dev->regs[0xE4u] = (uint8_t)(302 >> 4);
    dev->regs[0xE5u] = (uint8_t)(((50 & 0x0F) << 4) | (302 & 0x0F));
    dev->regs[0xE6u] = (uint8_t)(50 >> 4);
    dev->regs[0xE7u] = 30u;                 /* dig_H6 */
}

void mock_bme280_set_raw(uint32_t adc_t, uint32_t adc_p, uint16_t adc_h)
{
    /* Регістри 0xF7…0xFE: тиск, температура, вологість — усі старшим
     * байтом уперед, тиск і температура по двадцять розрядів. */
    g_bme280.regs[0xF7u] = (uint8_t)((adc_p >> 12) & 0xFFu);
    g_bme280.regs[0xF8u] = (uint8_t)((adc_p >> 4) & 0xFFu);
    g_bme280.regs[0xF9u] = (uint8_t)((adc_p << 4) & 0xF0u);
    g_bme280.regs[0xFAu] = (uint8_t)((adc_t >> 12) & 0xFFu);
    g_bme280.regs[0xFBu] = (uint8_t)((adc_t >> 4) & 0xFFu);
    g_bme280.regs[0xFCu] = (uint8_t)((adc_t << 4) & 0xF0u);
    g_bme280.regs[0xFDu] = (uint8_t)(adc_h >> 8);
    g_bme280.regs[0xFEu] = (uint8_t)(adc_h & 0xFFu);
}

void mock_adxl345_set_axes(int16_t x, int16_t y, int16_t z)
{
    g_adxl345.regs[0x32u] = (uint8_t)((uint16_t)x & 0xFFu);
    g_adxl345.regs[0x33u] = (uint8_t)((uint16_t)x >> 8);
    g_adxl345.regs[0x34u] = (uint8_t)((uint16_t)y & 0xFFu);
    g_adxl345.regs[0x35u] = (uint8_t)((uint16_t)y >> 8);
    g_adxl345.regs[0x36u] = (uint8_t)((uint16_t)z & 0xFFu);
    g_adxl345.regs[0x37u] = (uint8_t)((uint16_t)z >> 8);
}

static void mock_devices_init(void)
{
    if (g_initialised) {
        return;
    }
    g_initialised = true;

    memset(&g_bme280, 0, sizeof g_bme280);
    g_bme280.addr    = SYS_I2C_ADDR_BME280;
    g_bme280.present = true;
    bme280_load_calibration(&g_bme280);
    mock_bme280_set_raw(527144u, 415148u, 32000u);  /* ≈25 °C */

    memset(&g_adxl345, 0, sizeof g_adxl345);
    g_adxl345.addr        = SYS_I2C_ADDR_ADXL345;
    g_adxl345.present     = true;
    g_adxl345.regs[0x00u] = 0xE5u;   /* DEVID */
    mock_adxl345_set_axes(0, 0, 256);/* спокій: 1 g по осі Z */
}

static mock_device_t *find_device(uint8_t addr)
{
    mock_devices_init();
    if (addr == g_bme280.addr) {
        return &g_bme280;
    }
    if (addr == g_adxl345.addr) {
        return &g_adxl345;
    }
    return 0;
}

/* Спільна для всіх звертань перевірка: чи відповідає мікросхема взагалі
 * і чи не наказано їй зараз відмовити. */
static hal_i2c_status_t device_gate(mock_device_t **out_dev, uint8_t addr)
{
    mock_device_t *dev = find_device(addr);
    if (dev == 0 || !dev->present) {
        return HAL_I2C_ERR_NACK;
    }
    if (dev->inject_left > 0u) {
        dev->inject_left--;
        return dev->inject_status;
    }
    *out_dev = dev;
    g_transactions++;
    return HAL_I2C_OK;
}

/* Запис у регістр 0xF4 (ctrl_meas) у режимі forced означає «зміряй зараз».
 * Імітація відпрацьовує його миттєво: прапорець «міряю» навіть не встигає
 * піднятися, і драйвер бачить готовий результат. */
static void handle_register_write(mock_device_t *dev, uint8_t reg, uint8_t value)
{
    dev->regs[reg] = value;

    if (dev->addr == SYS_I2C_ADDR_BME280) {
        if (reg == 0xE0u && value == 0xB6u) {
            /* Скидання: конфігураційні регістри обнуляються, калібрування
             * і сирі дані лишаються — так само робить справжня мікросхема. */
            dev->regs[0xF2u] = 0u;
            dev->regs[0xF4u] = 0u;
            dev->regs[0xF5u] = 0u;
        }
        if (reg == 0xF4u && (value & 0x03u) == 0x01u) {
            dev->regs[0xF3u] = 0u;             /* вимір завершено */
            dev->regs[0xF4u] = (uint8_t)(value & 0xFCu); /* forced → sleep */
        }
    }
}

static hal_i2c_status_t mock_write(void *ctx, uint8_t dev_addr,
                                   const uint8_t *data, size_t len)
{
    (void)ctx;

    mock_device_t *dev = 0;
    const hal_i2c_status_t gate = device_gate(&dev, dev_addr);
    if (gate != HAL_I2C_OK) {
        return gate;
    }
    if (len == 0u) {
        return HAL_I2C_OK;   /* опитування присутності */
    }
    if (data == 0) {
        return HAL_I2C_ERR_ARG;
    }

    dev->reg_ptr = data[0];
    for (size_t i = 1u; i < len; i++) {
        handle_register_write(dev, (uint8_t)(dev->reg_ptr + (i - 1u)), data[i]);
    }
    return HAL_I2C_OK;
}

static hal_i2c_status_t mock_read(void *ctx, uint8_t dev_addr,
                                  uint8_t *data, size_t len)
{
    (void)ctx;

    mock_device_t *dev = 0;
    const hal_i2c_status_t gate = device_gate(&dev, dev_addr);
    if (gate != HAL_I2C_OK) {
        return gate;
    }
    if (data == 0 || len == 0u) {
        return HAL_I2C_ERR_ARG;
    }

    for (size_t i = 0u; i < len; i++) {
        /* Внутрішній лічильник адреси загортається на 256 — так само,
         * як у справжньої мікросхеми з однобайтовою адресою регістра. */
        data[i] = dev->regs[dev->reg_ptr];
        dev->reg_ptr = (uint8_t)(dev->reg_ptr + 1u);
    }
    return HAL_I2C_OK;
}

static hal_i2c_status_t mock_write_read(void *ctx, uint8_t dev_addr,
                                        const uint8_t *wdata, size_t wlen,
                                        uint8_t *rdata, size_t rlen)
{
    const hal_i2c_status_t st = mock_write(ctx, dev_addr, wdata, wlen);
    if (st != HAL_I2C_OK) {
        return st;
    }
    return mock_read(ctx, dev_addr, rdata, rlen);
}

static const hal_i2c_ops_t g_mock_ops = {
    .write      = mock_write,
    .read       = mock_read,
    .write_read = mock_write_read,
};

static const hal_i2c_bus_t g_mock_bus = {
    .ops = &g_mock_ops,
    .ctx = 0,
};

const hal_i2c_bus_t *mock_i2c_bus(void)
{
    mock_devices_init();
    return &g_mock_bus;
}

void mock_i2c_set_present(uint8_t dev_addr, bool present)
{
    mock_device_t *dev = find_device(dev_addr);
    if (dev != 0) {
        dev->present = present;
    }
}

void mock_i2c_inject_error(uint8_t dev_addr, hal_i2c_status_t status, unsigned count)
{
    mock_device_t *dev = find_device(dev_addr);
    if (dev != 0) {
        dev->inject_status = status;
        dev->inject_left   = count;
    }
}

unsigned mock_i2c_transaction_count(void)
{
    return g_transactions;
}
