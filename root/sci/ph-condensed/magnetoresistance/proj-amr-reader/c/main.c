/* C Implementation: Низькорівневий драйвер AMR-давача для вбудованих систем */
#include <stdio.h>
#include <math.h>
#include <stdint.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    float x;
    float y;
    float z;
} vector3f_t;

typedef struct {
    vector3f_t hard_iron_offset;
    float scale_matrix[3][3];
    float sensitivity_lsb_per_uT;
} amr_calibration_t;

/* Заглушки викликів I2C шини мікроконтролера */
static bool i2c_write_reg(uint8_t dev_addr, uint8_t reg, uint8_t value) {
    (void)dev_addr; (void)reg; (void)value;
    return true; /* У реальній системі: HAL_I2C_Mem_Write(...) */
}

static bool i2c_read_bytes(uint8_t dev_addr, uint8_t reg, uint8_t *buf, uint8_t len) {
    (void)dev_addr; (void)reg;
    for (uint8_t i = 0; i < len; i++) {
        buf[i] = (uint8_t)(100 + i * 10); /* Імітація даних АЦП */
    }
    return true;
}

/* Виконання циклу Set/Reset та зчитування сирого вектора */
bool amr_read_differential_raw(uint8_t dev_addr, vector3f_t *raw_out) {
    uint8_t buf[6];

    /* 1. Подаємо імпульс SET (регістр керування 0x09, біт 0x08) */
    if (!i2c_write_reg(dev_addr, 0x09, 0x08)) return false;
    if (!i2c_write_reg(dev_addr, 0x08, 0x01)) return false; /* Запуск вимірювання */
    if (!i2c_read_bytes(dev_addr, 0x00, buf, 6)) return false;

    int16_t set_x = (int16_t)((buf[0] << 8) | buf[1]);
    int16_t set_y = (int16_t)((buf[2] << 8) | buf[3]);
    int16_t set_z = (int16_t)((buf[4] << 8) | buf[5]);

    /* 2. Подаємо імпульс RESET (регістр керування 0x09, біт 0x10) */
    if (!i2c_write_reg(dev_addr, 0x09, 0x10)) return false;
    if (!i2c_write_reg(dev_addr, 0x08, 0x01)) return false; /* Запуск вимірювання */
    if (!i2c_read_bytes(dev_addr, 0x00, buf, 6)) return false;

    int16_t reset_x = (int16_t)((buf[0] << 8) | buf[1]);
    int16_t reset_y = (int16_t)((buf[2] << 8) | buf[3]);
    int16_t reset_z = (int16_t)((buf[4] << 8) | buf[5]);

    /* 3. Диференціальний вектор: V_diff = (V_SET - V_RESET) / 2 */
    raw_out->x = (float)(set_x - reset_x) / 2.0f;
    raw_out->y = (float)(set_y - reset_y) / 2.0f;
    raw_out->z = (float)(set_z - reset_z) / 2.0f;

    return true;
}

/* Обчислення вектору B у мкТл та компасного азимуту */
float amr_process_data(const vector3f_t *raw, const amr_calibration_t *cal, vector3f_t *b_out) {
    /* Віднімання hard-iron зсуву */
    float dx = (raw->x - cal->hard_iron_offset.x) / cal->sensitivity_lsb_per_uT;
    float dy = (raw->y - cal->hard_iron_offset.y) / cal->sensitivity_lsb_per_uT;
    float dz = (raw->z - cal->hard_iron_offset.z) / cal->sensitivity_lsb_per_uT;

    /* Множення на 3x3 матрицю soft-iron */
    b_out->x = cal->scale_matrix[0][0] * dx + cal->scale_matrix[0][1] * dy + cal->scale_matrix[0][2] * dz;
    b_out->y = cal->scale_matrix[1][0] * dx + cal->scale_matrix[1][1] * dy + cal->scale_matrix[1][2] * dz;
    b_out->z = cal->scale_matrix[2][0] * dx + cal->scale_matrix[2][1] * dy + cal->scale_matrix[2][2] * dz;

    /* Кут азимуту в градусах (0..360°) */
    float heading_rad = atan2f(b_out->y, b_out->x);
    float heading_deg = heading_rad * (180.0f / (float)M_PI);
    if (heading_deg < 0.0f) {
        heading_deg += 360.0f;
    }
    return heading_deg;
}
