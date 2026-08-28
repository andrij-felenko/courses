// Цілочисельна апроксимація каліброваного Softmax у форматі Q15
uint16_t Fast_CalibratedConfidence_Q15(int16_t logit_max, int16_t logit_sum, int16_t temp_q8) {
    // Масштабування логітів на коефіцієнт температури T
    int32_t scaled_diff = ((int32_t)(logit_max - logit_sum) << 8) / temp_q8;
    if (scaled_diff > 2048) {
        scaled_diff = 2048; // Захист від виходу за межі LUT
    } else if (scaled_diff < 0) {
        scaled_diff = 0;
    }
    
    // Прямий вибір значення ймовірності з таблиці у Flash
    return ExpLut_Q15[scaled_diff];
}
