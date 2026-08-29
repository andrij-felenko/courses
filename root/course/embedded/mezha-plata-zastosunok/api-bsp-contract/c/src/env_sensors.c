#include "env_sensors.h"

#include "bsp/port.h"

/* ------------------------------------------------------------------ SHT3x */

#define SHT3X_ADDR        0x44u
#define SHT3X_MEAS_MS     15u   /* висока повторюваність, без розтягування такту */

/* CRC-8, поліном 0x31, початкове значення 0xFF — як у документації Sensirion. */
static uint8_t sht3x_crc(const uint8_t *data, size_t len)
{
    uint8_t crc = 0xFFu;

    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x80u) ? (uint8_t)((crc << 1) ^ 0x31u)
                                : (uint8_t)(crc << 1);
        }
    }
    return crc;
}

static bsp_status_t sht3x_measure(int16_t *out_t_centi, uint16_t *out_rh_centi)
{
    const uint8_t cmd[2] = { 0x24u, 0x00u }; /* одноразове вимірювання */
    uint8_t rx[6];

    BSP_TRY(bsp_port_i2c_write(SHT3X_ADDR, cmd, sizeof cmd));
    bsp_port_delay_us(SHT3X_MEAS_MS * 1000u);
    BSP_TRY(bsp_port_i2c_read(SHT3X_ADDR, rx, sizeof rx));

    /* Кожне слово має власну контрольну суму: биття на лінії ловиться тут. */
    if (sht3x_crc(&rx[0], 2u) != rx[2] || sht3x_crc(&rx[3], 2u) != rx[5]) {
        return BSP_STATUS_ERR_BUS_FAULT;
    }

    const uint32_t raw_t = ((uint32_t)rx[0] << 8) | rx[1];
    const uint32_t raw_h = ((uint32_t)rx[3] << 8) | rx[4];

    /* T = -45 + 175 * raw / 65535, одразу в сотих частках градуса. */
    *out_t_centi  = (int16_t)((int32_t)((17500u * raw_t) / 65535u) - 4500);
    /* RH = 100 * raw / 65535, у сотих частках відсотка. */
    *out_rh_centi = (uint16_t)((10000u * raw_h) / 65535u);
    return BSP_STATUS_OK;
}

/* ----------------------------------------------------------------- BMP280 */

#define BMP280_ADDR           0x76u
#define BMP280_REG_ID         0xD0u
#define BMP280_REG_CTRL_MEAS  0xF4u
#define BMP280_REG_CONFIG     0xF5u
#define BMP280_REG_STATUS     0xF3u
#define BMP280_REG_CALIB      0x88u
#define BMP280_REG_DATA       0xF7u
#define BMP280_CHIP_ID        0x58u
/* osrs_t = x1, osrs_p = x1, режим forced: одне вимірювання й сон. */
#define BMP280_CTRL_FORCED    0x25u

typedef struct {
    bool     valid;
    uint16_t t1;
    int16_t  t2, t3;
    uint16_t p1;
    int16_t  p2, p3, p4, p5, p6, p7, p8, p9;
} bmp280_calib_t;

static bmp280_calib_t s_calib;

void env_sensors_invalidate(void)
{
    s_calib.valid = false;
}

static bsp_status_t bmp280_read_regs(uint8_t reg, uint8_t *buf, size_t len)
{
    return bsp_port_i2c_write_read(BMP280_ADDR, &reg, 1u, buf, len);
}

static bsp_status_t bmp280_write_reg(uint8_t reg, uint8_t value)
{
    const uint8_t tx[2] = { reg, value };

    return bsp_port_i2c_write(BMP280_ADDR, tx, sizeof tx);
}

static uint16_t le_u16(const uint8_t *p)
{
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

static int16_t le_i16(const uint8_t *p)
{
    return (int16_t)le_u16(p);
}

static bsp_status_t bmp280_load_calib(void)
{
    uint8_t id = 0;
    uint8_t raw[24];

    BSP_TRY(bmp280_read_regs(BMP280_REG_ID, &id, 1u));
    if (id != BMP280_CHIP_ID) {
        /* Відповів хтось інший: або переплутана адреса, або інша ревізія плати. */
        return BSP_STATUS_ERR_UNSUPPORTED;
    }

    BSP_TRY(bmp280_read_regs(BMP280_REG_CALIB, raw, sizeof raw));
    s_calib.t1 = le_u16(&raw[0]);
    s_calib.t2 = le_i16(&raw[2]);
    s_calib.t3 = le_i16(&raw[4]);
    s_calib.p1 = le_u16(&raw[6]);
    s_calib.p2 = le_i16(&raw[8]);
    s_calib.p3 = le_i16(&raw[10]);
    s_calib.p4 = le_i16(&raw[12]);
    s_calib.p5 = le_i16(&raw[14]);
    s_calib.p6 = le_i16(&raw[16]);
    s_calib.p7 = le_i16(&raw[18]);
    s_calib.p8 = le_i16(&raw[20]);
    s_calib.p9 = le_i16(&raw[22]);

    /* Нулі в T1/P1 — ознака побитої сторінки: рахувати по ній не можна. */
    if (s_calib.t1 == 0u || s_calib.p1 == 0u) {
        return BSP_STATUS_ERR_BUS_FAULT;
    }

    /* Фільтр IIR вимкнено: у режимі forced він лише розмазав би одиничний відлік. */
    BSP_TRY(bmp280_write_reg(BMP280_REG_CONFIG, 0x00u));

    s_calib.valid = true;
    return BSP_STATUS_OK;
}

static bsp_status_t bmp280_wait_ready(void)
{
    /* На x1/x1 перетворення триває ~6.4 мс; чекаємо з запасом. */
    for (unsigned i = 0; i < 20u; ++i) {
        uint8_t status = 0;

        BSP_TRY(bmp280_read_regs(BMP280_REG_STATUS, &status, 1u));
        if ((status & 0x08u) == 0u) {
            return BSP_STATUS_OK;
        }
        bsp_port_delay_us(1000u);
    }
    return BSP_STATUS_ERR_TIMEOUT;
}

/* Компенсація за документацією Bosch, цілочисельний варіант. */
static int32_t bmp280_t_fine(int32_t adc_t)
{
    const int32_t v1 = (((adc_t >> 3) - ((int32_t)s_calib.t1 << 1)) * (int32_t)s_calib.t2) >> 11;
    const int32_t v2 = ((((adc_t >> 4) - (int32_t)s_calib.t1) *
                         ((adc_t >> 4) - (int32_t)s_calib.t1)) >> 12) * (int32_t)s_calib.t3 >> 14;

    return v1 + v2;
}

static uint32_t bmp280_pressure(int32_t adc_p, int32_t t_fine)
{
    int64_t v1 = (int64_t)t_fine - 128000;
    int64_t v2 = v1 * v1 * (int64_t)s_calib.p6;
    int64_t p;

    v2 += (v1 * (int64_t)s_calib.p5) << 17;
    v2 += ((int64_t)s_calib.p4) << 35;
    v1 = ((v1 * v1 * (int64_t)s_calib.p3) >> 8) + ((v1 * (int64_t)s_calib.p2) << 12);
    v1 = (((((int64_t)1) << 47) + v1) * (int64_t)s_calib.p1) >> 33;
    if (v1 == 0) {
        return 0u; /* ділення на нуль: биті коефіцієнти */
    }

    p = 1048576 - adc_p;
    p = (((p << 31) - v2) * 3125) / v1;
    v1 = ((int64_t)s_calib.p9 * (p >> 13) * (p >> 13)) >> 25;
    v2 = ((int64_t)s_calib.p8 * p) >> 19;
    p = ((p + v1 + v2) >> 8) + (((int64_t)s_calib.p7) << 4);

    /* Результат у форматі Q24.8 паскалів. */
    return (uint32_t)(p >> 8);
}

static bsp_status_t bmp280_measure(uint32_t *out_pa)
{
    uint8_t raw[6];
    int32_t adc_p;
    int32_t adc_t;
    uint32_t pa;

    if (!s_calib.valid) {
        BSP_TRY(bmp280_load_calib());
    }

    BSP_TRY(bmp280_write_reg(BMP280_REG_CTRL_MEAS, BMP280_CTRL_FORCED));
    BSP_TRY(bmp280_wait_ready());
    BSP_TRY(bmp280_read_regs(BMP280_REG_DATA, raw, sizeof raw));

    adc_p = (int32_t)(((uint32_t)raw[0] << 12) | ((uint32_t)raw[1] << 4) | ((uint32_t)raw[2] >> 4));
    adc_t = (int32_t)(((uint32_t)raw[3] << 12) | ((uint32_t)raw[4] << 4) | ((uint32_t)raw[5] >> 4));

    /* 0x80000 — значення регістрів після скидання: вимірювання не відбулося. */
    if (adc_p == 0x80000 || adc_t == 0x80000) {
        return BSP_STATUS_ERR_TIMEOUT;
    }

    pa = bmp280_pressure(adc_p, bmp280_t_fine(adc_t));
    /* Поза земними межами — отже читали сміття, а не тиск. */
    if (pa < 30000u || pa > 120000u) {
        s_calib.valid = false;
        return BSP_STATUS_ERR_BUS_FAULT;
    }

    *out_pa = pa;
    return BSP_STATUS_OK;
}

/* ------------------------------------------------------------------ Фасад */

bsp_status_t env_sensors_read(board_env_metrics_t *out_env)
{
    int16_t  t_centi = 0;
    uint16_t rh_centi = 0;
    uint32_t pressure_pa = 0;

    BSP_TRY(sht3x_measure(&t_centi, &rh_centi));
    BSP_TRY(bmp280_measure(&pressure_pa));

    /* Поза паспортним діапазоном давача (-40..+125 °C) — результат недійсний. */
    if (t_centi < -4000 || t_centi > 12500) {
        return BSP_STATUS_ERR_BUS_FAULT;
    }

    out_env->temperature_centi_c = t_centi;
    out_env->humidity_centi_pct  = rh_centi;
    out_env->pressure_pa         = pressure_pa;
    return BSP_STATUS_OK;
}
