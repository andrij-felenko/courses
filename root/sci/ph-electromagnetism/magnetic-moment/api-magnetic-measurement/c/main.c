#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Коди помилок драйвера магнітометра */
typedef enum {
    MAGNETO_OK = 0,
    MAGNETO_ERR_I2C,
    MAGNETO_ERR_DEV_NOT_FOUND,
    MAGNETO_ERR_NOT_READY,
    MAGNETO_ERR_PARAM
} MagnetoStatus;

/* Виміряний вектор магнітного поля у мікротеслах [мкТл] */
typedef struct {
    float x;
    float y;
    float z;
} Vector3f;

/* Параметри калібрування твердого заліза */
typedef struct {
    float offset_x;
    float offset_y;
    float offset_z;
    float scale_x;
    float scale_y;
    float scale_z;
} MagnetoCalib;

/* Контекст пристрою */
typedef struct {
    uint8_t i2c_addr;
    float sensitivity_lsb_per_uT;
    MagnetoCalib calib;
    bool is_initialized;
} MagnetoDevice;

/* Низькорівневі прототипи I2C (реалізуються для конкретної платформи) */
extern int platform_i2c_read(uint8_t dev_addr, uint8_t reg_addr, uint8_t *data, uint16_t len);
extern int platform_i2c_write(uint8_t dev_addr, uint8_t reg_addr, const uint8_t *data, uint16_t len);

/* Ініціалізація датчика */
MagnetoStatus magneto_init(MagnetoDevice *dev, uint8_t i2c_addr) {
    if (!dev) return MAGNETO_ERR_PARAM;

    dev->i2c_addr = i2c_addr;
    dev->sensitivity_lsb_per_uT = 6842.0f; /* Для діапазону ±4 Гаус */
    dev->is_initialized = false;

    uint8_t who_am_i = 0;
    if (platform_i2c_read(dev->i2c_addr, 0x0F, &who_am_i, 1) != 0) {
        return MAGNETO_ERR_I2C;
    }

    if (who_am_i != 0x3D) {
        return MAGNETO_ERR_DEV_NOT_FOUND;
    }

    /* CTRL_REG1: 80 Hz, Ultra-high performance X/Y */
    uint8_t reg1 = 0x70;
    platform_i2c_write(dev->i2c_addr, 0x20, &reg1, 1);

    /* CTRL_REG2: ±4 Gauss FS */
    uint8_t reg2 = 0x00;
    platform_i2c_write(dev->i2c_addr, 0x21, &reg2, 1);

    /* CTRL_REG3: Continuous conversion mode */
    uint8_t reg3 = 0x00;
    platform_i2c_write(dev->i2c_addr, 0x22, &reg3, 1);

    /* Типові дефолтні значення калібрування */
    dev->calib.offset_x = 0.0f;
    dev->calib.offset_y = 0.0f;
    dev->calib.offset_z = 0.0f;
    dev->calib.scale_x  = 1.0f;
    dev->calib.scale_y  = 1.0f;
    dev->calib.scale_z  = 1.0f;

    dev->is_initialized = true;
    return MAGNETO_OK;
}

/* Зчитування відкаліброваного вектора поля B [мкТл] */
MagnetoStatus magneto_read_field(MagnetoDevice *dev, Vector3f *field_uT) {
    if (!dev || !dev->is_initialized || !field_uT) return MAGNETO_ERR_PARAM;

    uint8_t raw_buf[6];
    if (platform_i2c_read(dev->i2c_addr, 0x28 | 0x80, raw_buf, 6) != 0) {
        return MAGNETO_ERR_I2C;
    }

    int16_t raw_x = (int16_t)((raw_buf[1] << 8) | raw_buf[0]);
    int16_t raw_y = (int16_t)((raw_buf[3] << 8) | raw_buf[2]);
    int16_t raw_z = (int16_t)((raw_buf[5] << 8) | raw_buf[4]);

    /* Перетворення у мкТл та застосування калібрування */
    float uncal_x = (float)raw_x / dev->sensitivity_lsb_per_uT * 100.0f;
    float uncal_y = (float)raw_y / dev->sensitivity_lsb_per_uT * 100.0f;
    float uncal_z = (float)raw_z / dev->sensitivity_lsb_per_uT * 100.0f;

    field_uT->x = (uncal_x - dev->calib.offset_x) * dev->calib.scale_x;
    field_uT->y = (uncal_y - dev->calib.offset_y) * dev->calib.scale_y;
    field_uT->z = (uncal_z - dev->calib.offset_z) * dev->calib.scale_z;

    return MAGNETO_OK;
}

/* Розрахунок магнітного моменту джерела за виміряним полем на відстані R вздовж осі Z */
float magneto_estimate_dipole_moment_z(float field_bz_uT, float distance_m) {
    /* B_z = (mu_0 / 2pi) * (mu / r^3) -> mu = (2pi * r^3 * B_z) / mu_0 */
    float B_z_tesla = field_bz_uT * 1e-6f;
    float r3 = distance_m * distance_m * distance_m;
    float mu_0 = 1.256637e-6f;
    float pi = 3.14159265f;

    return (2.0f * pi * r3 * B_z_tesla) / mu_0;
}
