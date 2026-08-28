#include <stdint.h>
#include <math.h>

float calc_heading_error_bam(float target_rad, float meas_rad) {
    uint16_t target_bam = (uint16_t)(target_rad * (32768.0f / (float)M_PI));
    uint16_t meas_bam   = (uint16_t)(meas_rad   * (32768.0f / (float)M_PI));

    // Апаратне переповнення беззнакового регістра реалізує операцію за модулем 2¹⁶:
    int16_t diff_bam = (int16_t)(target_bam - meas_bam);

    // Перетворення назад у плаваючу кому:
    return (float)diff_bam * ((float)M_PI / 32768.0f);
}
