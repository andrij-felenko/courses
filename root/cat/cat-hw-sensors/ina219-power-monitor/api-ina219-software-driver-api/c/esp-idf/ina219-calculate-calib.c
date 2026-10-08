// Обчислення калібрування та перетворення вибірок мовою C
#include <stdint.h>
#include <math.h>

typedef struct {
    float r_shunt;
    float current_lsb;
    float power_lsb;
    uint16_t cal_value;
} ina219_calib_t;

ina219_calib_t ina219_calculate_calib(float r_shunt, float max_expected_i) {
    ina219_calib_t cal;
    cal.r_shunt = r_shunt;
    
    float min_lsb = max_expected_i / 32768.0f;
    // Округлення LSB до зручного кроку (наприклад, 100 мкА)
    cal.current_lsb = ceilf(min_lsb * 10000.0f) / 10000.0f;
    cal.power_lsb = 20.0f * cal.current_lsb;
    
    float cal_raw = 0.04096f / (cal.current_lsb * cal.r_shunt);
    cal.cal_value = (uint16_t)truncf(cal_raw);
    
    return cal;
}

float ina219_raw_to_bus_voltage(uint16_t raw_bus_reg) {
    // Зсув на 3 біти вправо та множення на LSB = 4 мВ
    uint16_t raw_val = raw_bus_reg >> 3;
    return raw_val * 0.004f;
}

float ina219_raw_to_current(int16_t raw_current_reg, float current_lsb) {
    return raw_current_reg * current_lsb;
}
