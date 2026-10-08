// Допоміжна функція зчитування АЦП та обчислення Rs і ppm
static void mq7_process_measurement(mq7_t *dev, uint16_t raw_adc) {
    dev->raw_adc_value = raw_adc;
    
    // Перетворення значень АЦП у напругу (мВ)
    float v_out_mv = ((float)raw_adc / dev->config.adc_max_value) * dev->config.v_ref_mv;
    if (v_out_mv <= 1.0f) {
        v_out_mv = 1.0f; // Запобігання діленню на нуль
    }
    
    // Розрахунок опору сенсора Rs з вимірювального дільника
    dev->rs_kohm = dev->config.rl_kohm * (dev->config.v_ref_mv - v_out_mv) / v_out_mv;
    
    // Співвідношення Rs / R0
    float ratio = dev->rs_kohm / dev->config.r0_kohm;
    
    // Степенева формула розрахунку ppm для MQ-7: ppm = 98.53 * (Rs/R0)^(-1.52)
    dev->co_ppm = 98.53f * powf(ratio, -1.52f);
    dev->data_ready = true;
}

void mq7_tick(mq7_t *dev, uint32_t current_time_ms, uint16_t current_adc_raw) {
    if (dev == NULL || dev->state == MQ7_STATE_UNINIT) return;

    dev->last_tick_ms = current_time_ms;
    uint32_t elapsed = current_time_ms - dev->last_state_change_ms;

    switch (dev->state) {
        case MQ7_STATE_HIGH_HEAT:
            if (elapsed >= dev->config.high_heat_time_ms) {
                // Перехід до фази низького нагріву (1.4 В -> ~28% ШІМ = 71 / 255)
                ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, 71);
                ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
                
                dev->state = MQ7_STATE_LOW_HEAT;
                dev->last_state_change_ms = current_time_ms;
            }
            break;

        case MQ7_STATE_LOW_HEAT:
            // Зчитуємо АЦП наприкінці вимірювальної фази (за 200 мс до кінця)
            if (elapsed >= (dev->config.low_heat_time_ms - 200) && !dev->data_ready) {
                mq7_process_measurement(dev, current_adc_raw);
            }
            
            if (elapsed >= dev->config.low_heat_time_ms) {
                // Завершення вимірювального циклу, повернення до очищення (5.0 В -> 100% ШІМ)
                ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, 255);
                ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
                
                dev->state = MQ7_STATE_HIGH_HEAT;
                dev->last_state_change_ms = current_time_ms;
                dev->data_ready = false; // Скидаємо прапорець для наступного циклу
            }
            break;

        default:
            break;
    }
}

bool mq7_read_ppm(mq7_t *dev, float *out_ppm) {
    if (dev != NULL && dev->data_ready && out_ppm != NULL) {
        *out_ppm = dev->co_ppm;
        return true;
    }
    return false;
}
