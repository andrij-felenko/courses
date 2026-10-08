#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint16_t adc_min;
    uint16_t adc_max;
    uint16_t max_resolution;
} pot_config_t;

bool read_potentiometer_angle(uint16_t raw_adc, const pot_config_t *cfg, uint16_t *out_angle) {
    if (raw_adc < cfg->adc_min || raw_adc > cfg->adc_max) {
        // Сигнал вийшов за валідний діапазон мертвих зон
        return false;
    }
    
    uint32_t span = cfg->adc_max - cfg->adc_min;
    uint32_t offset_val = raw_adc - cfg->adc_min;
    *out_angle = (uint16_t)((offset_val * cfg->max_resolution) / span);
    return true;
}

bool calculate_pwm_angle(uint32_t t_high, uint32_t t_period, uint32_t max_res, uint16_t *out_angle) {
    if (t_period == 0) return false;
    
    // Перевірка допустимого діапазону заповнення (від 1% до 99%)
    uint32_t duty_ppm = (t_high * 1000000UL) / t_period;
    if (duty_ppm < 10000 || duty_ppm > 990000) {
        return false; // Помилка заповнення або відсутність сигналу
    }
    
    *out_angle = (uint16_t)((duty_ppm * max_res) / 1000000UL);
    return true;
}
