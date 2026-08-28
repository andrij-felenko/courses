#include <stdint.h>
#include <stdbool.h>

/* Розрахунок калібрувального коефіцієнта для INA226 */
uint16_t calculate_ina226_calibration(double r_shunt_ohms, double max_current_a, double *current_lsb_a) {
    /* Крок струму: Current_LSB = Max_Current / 2^15 */
    *current_lsb_a = max_current_a / 32768.0;
    /* CAL = trunc(0.00512 / (Current_LSB * R_shunt)) */
    double cal = 0.00512 / ((*current_lsb_a) * r_shunt_ohms);
    return (uint16_t)cal;
}

/* Перетворення сирих 16-розрядних регістрів у фізичні величини */
void parse_power_readings(uint16_t vbus_raw, int16_t current_raw, uint16_t power_raw,
                          double current_lsb_a, uint32_t *vbus_mv, int32_t *current_ma, uint32_t *power_mw) {
    /* VBUS LSB фіксований: 1.25 мВ */
    *vbus_mv = (uint32_t)((vbus_raw * 1250ULL) / 1000ULL);
    /* Струм у мА */
    *current_ma = (int32_t)(current_raw * current_lsb_a * 1000.0);
    /* Потужність: Power_LSB = 25 * Current_LSB (у Вт) -> переводимо в мВт */
    double power_lsb_w = 25.0 * current_lsb_a;
    *power_mw = (uint32_t)(power_raw * power_lsb_w * 1000.0);
}
