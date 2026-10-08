typedef struct {
    uint16_t v_black;
    uint16_t v_white;
    uint16_t threshold;
    uint16_t hysteresis;
} tcrt5000_calib_t;

// Автоматичний розрахунок порогових параметрів
tcrt5000_err_t tcrt5000_calculate_calibration(tcrt5000_calib_t *calib, uint16_t raw_black, uint16_t raw_white, float k_factor) {
    if (!calib || k_factor < 0.0f || k_factor > 1.0f) {
        return TCRT5000_ERR_INVALID_ARG;
    }
    
    calib->v_black = raw_black;
    calib->v_white = raw_white;
    
    int32_t span = (int32_t)raw_white - (int32_t)raw_black;
    if (span < 50) { // Недостатній контраст між поверхнями
        return TCRT5000_ERR_INVALID_ARG;
    }
    
    calib->threshold = raw_black + (uint16_t)(k_factor * span);
    calib->hysteresis = (uint16_t)(0.05f * (span < 0 ? -span : span)); // 5% гістерезис
    return TCRT5000_OK;
}

// Визначення логічного стану з урахуванням гістерезису
bool tcrt5000_evaluate_state(uint16_t current_val, const tcrt5000_calib_t *calib, bool current_state) {
    uint16_t upper_bound = calib->threshold + calib->hysteresis;
    uint16_t lower_bound = (calib->threshold > calib->hysteresis) ? (calib->threshold - calib->hysteresis) : 0;
    
    if (current_state) {
        if (current_val < lower_bound) return false;
        return true;
    } else {
        if (current_val > upper_bound) return true;
        return false;
    }
}
