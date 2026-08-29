// bsp/bsp_bme280.c — уся внутрішня кухня давача: адреси регістрів, карта калібрування
// й формули компенсації Bosch. Назовні не видно жодного шістнадцяткового числа.
#include "bsp/bsp_bme280.h"

#include <stddef.h>
#include <string.h>

// --- Карта регістрів мікросхеми ------------------------------------------------
#define REG_CALIB_TP 0x88u  // dig_T1..dig_T3, dig_P1..dig_P9 — 24 байти поспіль
#define REG_CHIP_ID 0xD0u
#define REG_RESET 0xE0u
#define REG_CALIB_H 0xE1u  // dig_H2..dig_H6 — 7 байтів
#define REG_CALIB_H1 0xA1u
#define REG_CTRL_HUM 0xF2u
#define REG_STATUS 0xF3u
#define REG_CTRL_MEAS 0xF4u
#define REG_CONFIG 0xF5u
#define REG_DATA 0xF7u  // press msb..hum lsb — 8 байтів поспіль

#define CHIP_ID_BME280 0x60u

#define CTRL_HUM_OSRS_X1 0x01u
// osrs_t = x1 (001), osrs_p = x1 (001), mode = normal (11)
#define CTRL_MEAS_NORMAL_X1 ((1u << 5) | (1u << 2) | 0x03u)
// t_sb = 1000 мс, фільтр вимкнено, SPI-3wire вимкнено
#define CONFIG_STANDBY_1S 0xA0u

#define STATUS_MEASURING 0x08u
#define STATUS_IM_UPDATE 0x01u

// Скільки разів опитувати регістр стану, перш ніж вважати давач непритомним.
#define STATUS_POLL_ATTEMPTS 512u

// Значення, яким чип позначає «вибірки ще не було».
#define ADC_TP_UNSET 0x80000
#define ADC_H_UNSET 0x8000

struct bsp_bme280_dev {
    hal_i2c_bus_t* bus;
    uint8_t address;
    hal_i2c_status_t last_status;
    float t_fine;  // Спільна проміжна величина температури для тиску й вологості

    uint16_t dig_T1;
    int16_t dig_T2, dig_T3;
    uint16_t dig_P1;
    int16_t dig_P2, dig_P3, dig_P4, dig_P5, dig_P6, dig_P7, dig_P8, dig_P9;
    uint8_t dig_H1, dig_H3;
    int16_t dig_H2, dig_H4, dig_H5;
    int8_t dig_H6;
};

_Static_assert(sizeof(struct bsp_bme280_dev) <= sizeof(((bsp_bme280_storage_t*)0)->opaque.bytes),
               "bsp_bme280_storage_t замалий для дескриптора — збільште bytes[]");

// --- Дрібні розпаковувачі байтів ------------------------------------------------
static uint16_t le_u16(const uint8_t* p) { return (uint16_t)((uint16_t)p[1] << 8 | p[0]); }
static int16_t le_i16(const uint8_t* p) { return (int16_t)le_u16(p); }

// --- Завантаження калібрувальних коефіцієнтів ------------------------------------
static bool load_calibration(struct bsp_bme280_dev* dev)
{
    uint8_t tp[24];
    dev->last_status = hal_i2c_read_reg(dev->bus, dev->address, REG_CALIB_TP, tp, sizeof(tp));
    if (dev->last_status != HAL_I2C_OK) return false;

    dev->dig_T1 = le_u16(&tp[0]);
    dev->dig_T2 = le_i16(&tp[2]);
    dev->dig_T3 = le_i16(&tp[4]);
    dev->dig_P1 = le_u16(&tp[6]);
    dev->dig_P2 = le_i16(&tp[8]);
    dev->dig_P3 = le_i16(&tp[10]);
    dev->dig_P4 = le_i16(&tp[12]);
    dev->dig_P5 = le_i16(&tp[14]);
    dev->dig_P6 = le_i16(&tp[16]);
    dev->dig_P7 = le_i16(&tp[18]);
    dev->dig_P8 = le_i16(&tp[20]);
    dev->dig_P9 = le_i16(&tp[22]);

    uint8_t h1 = 0u;
    dev->last_status = hal_i2c_read_reg(dev->bus, dev->address, REG_CALIB_H1, &h1, 1u);
    if (dev->last_status != HAL_I2C_OK) return false;
    dev->dig_H1 = h1;

    uint8_t h[7];
    dev->last_status = hal_i2c_read_reg(dev->bus, dev->address, REG_CALIB_H, h, sizeof(h));
    if (dev->last_status != HAL_I2C_OK) return false;

    dev->dig_H2 = le_i16(&h[0]);
    dev->dig_H3 = h[2];
    // dig_H4 і dig_H5 упаковані в спільний півбайт регістра 0xE5 — саме тому
    // калібрування вологості не читається одним акуратним масивом.
    dev->dig_H4 = (int16_t)(((int16_t)(int8_t)h[3] << 4) | (int16_t)(h[4] & 0x0Fu));
    dev->dig_H5 = (int16_t)(((int16_t)(int8_t)h[5] << 4) | (int16_t)(h[4] >> 4));
    dev->dig_H6 = (int8_t)h[6];

    // dig_P1 == 0 означає порожню або побиту сторінку калібрування:
    // з такими коефіцієнтами формула тиску ділить на нуль.
    return dev->dig_T1 != 0u && dev->dig_P1 != 0u;
}

// --- Переведення чипа в робочий режим ---------------------------------------------
static bool configure_chip(struct bsp_bme280_dev* dev)
{
    // ctrl_hum набирає чинності лише після запису ctrl_meas — порядок обовʼязковий.
    dev->last_status = hal_i2c_write_u8(dev->bus, dev->address, REG_CTRL_HUM, CTRL_HUM_OSRS_X1);
    if (dev->last_status != HAL_I2C_OK) return false;

    dev->last_status = hal_i2c_write_u8(dev->bus, dev->address, REG_CONFIG, CONFIG_STANDBY_1S);
    if (dev->last_status != HAL_I2C_OK) return false;

    dev->last_status = hal_i2c_write_u8(dev->bus, dev->address, REG_CTRL_MEAS, CTRL_MEAS_NORMAL_X1);
    if (dev->last_status != HAL_I2C_OK) return false;

    // Чекаємо, доки чип перенесе калібрування з NVM і завершить першу вибірку.
    for (unsigned attempt = 0u; attempt < STATUS_POLL_ATTEMPTS; ++attempt) {
        uint8_t status = 0u;
        dev->last_status = hal_i2c_read_reg(dev->bus, dev->address, REG_STATUS, &status, 1u);
        if (dev->last_status != HAL_I2C_OK) return false;
        if ((status & (STATUS_MEASURING | STATUS_IM_UPDATE)) == 0u) {
            return true;
        }
    }
    dev->last_status = HAL_I2C_ERR_TIMEOUT;
    return false;
}

bsp_bme280_t* bsp_bme280_init(bsp_bme280_storage_t* storage, hal_i2c_bus_t* bus, uint8_t i2c_addr)
{
    if (!storage || !bus || !bus->ops) return NULL;

    struct bsp_bme280_dev* dev = (struct bsp_bme280_dev*)(void*)storage->opaque.bytes;
    memset(dev, 0, sizeof(*dev));
    dev->bus = bus;
    dev->address = i2c_addr;
    dev->last_status = HAL_I2C_OK;

    if (!bsp_bme280_reconfigure(dev)) return NULL;
    return dev;
}

bool bsp_bme280_reconfigure(bsp_bme280_t* dev)
{
    if (!dev) return false;

    uint8_t chip_id = 0u;
    dev->last_status = hal_i2c_read_reg(dev->bus, dev->address, REG_CHIP_ID, &chip_id, 1u);
    if (dev->last_status != HAL_I2C_OK) return false;
    if (chip_id != CHIP_ID_BME280) {
        // На адресі відповів хтось інший (BMP280 віддає 0x58). Мовчки рахувати
        // його дані за наші не можна: карта калібрування в них різна.
        dev->last_status = HAL_I2C_ERR_BUS;
        return false;
    }

    if (!load_calibration(dev)) return false;
    return configure_chip(dev);
}

// --- Компенсація за формулами Bosch у рухомій комі ---------------------------------
static float compensate_temperature(struct bsp_bme280_dev* dev, int32_t adc_T)
{
    const float t = (float)adc_T;
    const float var1 = (t / 16384.0f - (float)dev->dig_T1 / 1024.0f) * (float)dev->dig_T2;
    const float d = t / 131072.0f - (float)dev->dig_T1 / 8192.0f;
    const float var2 = d * d * (float)dev->dig_T3;
    dev->t_fine = var1 + var2;
    return dev->t_fine / 5120.0f;
}

static float compensate_pressure(const struct bsp_bme280_dev* dev, int32_t adc_P)
{
    float var1 = dev->t_fine / 2.0f - 64000.0f;
    float var2 = var1 * var1 * (float)dev->dig_P6 / 32768.0f;
    var2 = var2 + var1 * (float)dev->dig_P5 * 2.0f;
    var2 = var2 / 4.0f + (float)dev->dig_P4 * 65536.0f;
    var1 = ((float)dev->dig_P3 * var1 * var1 / 524288.0f + (float)dev->dig_P2 * var1) / 524288.0f;
    var1 = (1.0f + var1 / 32768.0f) * (float)dev->dig_P1;
    if (var1 == 0.0f) {
        return 0.0f;  // Ділення на нуль при негодящому калібруванні
    }
    float p = 1048576.0f - (float)adc_P;
    p = (p - var2 / 4096.0f) * 6250.0f / var1;
    var1 = (float)dev->dig_P9 * p * p / 2147483648.0f;
    var2 = p * (float)dev->dig_P8 / 32768.0f;
    p = p + (var1 + var2 + (float)dev->dig_P7) / 16.0f;
    return p / 100.0f;  // Па → гПа
}

static float compensate_humidity(const struct bsp_bme280_dev* dev, int32_t adc_H)
{
    float h = dev->t_fine - 76800.0f;
    h = ((float)adc_H - ((float)dev->dig_H4 * 64.0f + (float)dev->dig_H5 / 16384.0f * h)) *
        ((float)dev->dig_H2 / 65536.0f *
         (1.0f + (float)dev->dig_H6 / 67108864.0f * h *
                     (1.0f + (float)dev->dig_H3 / 67108864.0f * h)));
    h = h * (1.0f - (float)dev->dig_H1 * h / 524288.0f);

    if (h > 100.0f) return 100.0f;
    if (h < 0.0f) return 0.0f;
    return h;
}

bool bsp_bme280_read(bsp_bme280_t* dev, bsp_bme280_data_t* out_data)
{
    if (!dev || !out_data) return false;

    uint8_t raw[8];
    dev->last_status = hal_i2c_read_reg(dev->bus, dev->address, REG_DATA, raw, sizeof(raw));
    if (dev->last_status != HAL_I2C_OK) {
        // Шар BSP не рахує математику за сміттєвими байтами буфера.
        return false;
    }

    const int32_t adc_P = (int32_t)(((uint32_t)raw[0] << 12) | ((uint32_t)raw[1] << 4) |
                                    ((uint32_t)raw[2] >> 4));
    const int32_t adc_T = (int32_t)(((uint32_t)raw[3] << 12) | ((uint32_t)raw[4] << 4) |
                                    ((uint32_t)raw[5] >> 4));
    const int32_t adc_H = (int32_t)(((uint32_t)raw[6] << 8) | (uint32_t)raw[7]);

    if (adc_T == ADC_TP_UNSET) {
        // Чип у режимі сну або ще не зробив жодної вибірки.
        return false;
    }

    out_data->temperature_c = compensate_temperature(dev, adc_T);
    out_data->pressure_hpa = (adc_P == ADC_TP_UNSET) ? 0.0f : compensate_pressure(dev, adc_P);
    out_data->humidity_percent = (adc_H == ADC_H_UNSET) ? 0.0f : compensate_humidity(dev, adc_H);
    return true;
}

hal_i2c_status_t bsp_bme280_last_status(const bsp_bme280_t* dev)
{
    return dev ? dev->last_status : HAL_I2C_ERR_ARG;
}
