#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Структура калібрувальних коефіцієнтів з OTP пам'яті */
typedef struct {
    uint16_t dig_T1;
    int16_t  dig_T2;
    int16_t  dig_T3;
    uint16_t dig_P1;
    int16_t  dig_P2;
    int16_t  dig_P3;
    int16_t  dig_P4;
    int16_t  dig_P5;
    int16_t  dig_P6;
    int16_t  dig_P7;
    int16_t  dig_P8;
    int16_t  dig_P9;
} bmp280_calib_data_t;

/* Стан компенсаційного рушія */
typedef struct {
    bmp280_calib_data_t calib;
    int32_t t_fine; /* Тонка температура, необхідна для тиску */
} bmp280_engine_t;

/* Розбір 24 байтів сирого OTP буфера */
void bmp280_parse_calibration(bmp280_engine_t *engine, const uint8_t *buf) {
    engine->calib.dig_T1 = (uint16_t)(buf[0]  | (buf[1]  << 8));
    engine->calib.dig_T2 = (int16_t) (buf[2]  | (buf[3]  << 8));
    engine->calib.dig_T3 = (int16_t) (buf[4]  | (buf[5]  << 8));
    engine->calib.dig_P1 = (uint16_t)(buf[6]  | (buf[7]  << 8));
    engine->calib.dig_P2 = (int16_t) (buf[8]  | (buf[9]  << 8));
    engine->calib.dig_P3 = (int16_t) (buf[10] | (buf[11] << 8));
    engine->calib.dig_P4 = (int16_t) (buf[12] | (buf[13] << 8));
    engine->calib.dig_P5 = (int16_t) (buf[14] | (buf[15] << 8));
    engine->calib.dig_P6 = (int16_t) (buf[16] | (buf[17] << 8));
    engine->calib.dig_P7 = (int16_t) (buf[18] | (buf[19] << 8));
    engine->calib.dig_P8 = (int16_t) (buf[20] | (buf[21] << 8));
    engine->calib.dig_P9 = (int16_t) (buf[22] | (buf[23] << 8));
}

/* 
 * Розрахунок температури в сотих частках градуса Цельсія (наприклад, 2534 = 25.34 °C).
 * Одночасно оновлює engine->t_fine.
 */
int32_t bmp280_compensate_temperature(bmp280_engine_t *engine, int32_t adc_T) {
    int32_t var1, var2, T;

    /* var1 = (adc_T / 8 - dig_T1 * 2) * dig_T2 / 2048 */
    var1 = ((((adc_T >> 3) - ((int32_t)engine->calib.dig_T1 << 1))) * 
            ((int32_t)engine->calib.dig_T2)) >> 11;

    /* var2 = (adc_T / 16 - dig_T1) * (adc_T / 16 - dig_T1) * dig_T3 / 4194304 */
    var2 = (((((adc_T >> 4) - ((int32_t)engine->calib.dig_T1)) * 
              ((adc_T >> 4) - ((int32_t)engine->calib.dig_T1))) >> 12) * 
            ((int32_t)engine->calib.dig_T3)) >> 14;

    engine->t_fine = var1 + var2;
    T = (engine->t_fine * 5 + 128) >> 8;
    return T;
}

/* 
 * Розрахунок тиску в Паскалях у 64-бітній арифметиці (висока точність без втрати молодших бітів).
 * Повертає значення у форматі Q24.8 (1/256 Па), для отримання цілих Паскалів слід виконати >> 8.
 */
uint32_t bmp280_compensate_pressure_q24(bmp280_engine_t *engine, int32_t adc_P) {
    int64_t var1, var2, p;

    var1 = ((int64_t)engine->t_fine) - 128000;
    var2 = var1 * var1 * (int64_t)engine->calib.dig_P6;
    var2 = var2 + ((var1 * (int64_t)engine->calib.dig_P5) << 17);
    var2 = var2 + (((int64_t)engine->calib.dig_P4) << 35);
    var1 = ((var1 * var1 * (int64_t)engine->calib.dig_P3) >> 8) + 
           ((var1 * (int64_t)engine->calib.dig_P2) << 12);
    var1 = (((((int64_t)1) << 47) + var1)) * ((int64_t)engine->calib.dig_P1) >> 33;

    if (var1 == 0) {
        return 0; /* Захист від ділення на нуль */
    }

    p = 1048576 - adc_P;
    p = (((p << 31) - var2) * 3125) / var1;
    var1 = (((int64_t)engine->calib.dig_P9) * (p >> 13) * (p >> 13)) >> 25;
    var2 = (((int64_t)engine->calib.dig_P8) * p) >> 19;

    p = ((p + var1 + var2) >> 8) + (((int64_t)engine->calib.dig_P7) << 4);
    return (uint32_t)p;
}
