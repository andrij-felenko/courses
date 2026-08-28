#include <stdint.h>

// --- контракт модуля (адреси й поля — у довіднику регістрів) ---
#define ADDR          0x76        // SDO=GND; 0x77 якщо SDO=VDDIO
#define REG_CTRL_HUM  0xF2
#define REG_CTRL_MEAS 0xF4
#define REG_CONFIG    0xF5
#define REG_TEMP      0xFA        // 0xFA..0xFC, 20-бітний код

// значення полів (зсуви — за розкладкою регістрів)
#define OSRS_H_x1     0x01
#define OSRS_T_x2     (0x02 << 5)
#define OSRS_P_x16    (0x05 << 2)
#define MODE_NORMAL   0x03
#define FILTER_x4     (0x02 << 2)
#define STBY_250MS    (0x03 << 5)

// заводські коефіцієнти цього екземпляра (зчитані з calib при старті)
typedef struct { uint16_t T1; int16_t T2, T3; } calib_t;

extern void i2c_write(uint8_t addr, uint8_t reg, uint8_t val);
extern void i2c_read (uint8_t addr, uint8_t reg, uint8_t *buf, uint8_t n);

// увімкнення: ПОРЯДОК важливий — ctrl_hum ПЕРЕД ctrl_meas
void env_setup(void) {
    i2c_write(ADDR, REG_CONFIG,    FILTER_x4 | STBY_250MS);            // IIR-фільтр + пауза між циклами
    i2c_write(ADDR, REG_CTRL_HUM,  OSRS_H_x1);                         // передискретизація вологості
    i2c_write(ADDR, REG_CTRL_MEAS, OSRS_T_x2 | OSRS_P_x16 | MODE_NORMAL); // T×2, тиск×16, неперервно
}

// сирий 20-бітний код → °C через індивідуальні коефіцієнти (формула з даташита)
float read_temp_c(const calib_t *c) {
    uint8_t b[3];
    i2c_read(ADDR, REG_TEMP, b, 3);
    int32_t raw = ((int32_t)b[0] << 12) | ((int32_t)b[1] << 4) | (b[2] >> 4);

    float v1 = ((float)raw / 16384.0f - (float)c->T1 / 1024.0f) * (float)c->T2;
    float v2 =  (float)raw / 131072.0f - (float)c->T1 / 8192.0f;
    v2 = v2 * v2 * (float)c->T3;
    return (v1 + v2) / 5120.0f;                                        // °C
}
