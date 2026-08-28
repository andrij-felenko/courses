/* Цілочисельна реалізація IIR-фільтра у форматі Q16.16 */
typedef struct {
    int32_t alpha_q16;         /* Коефіцієнт alpha * 65536 (наприклад, 0.15 * 65536 = 9830) */
    int32_t filtered_rssi_q16; /* Значення RSSI у дБм * 65536 */
    bool initialized;
} rssi_filter_fixed_t;

int32_t rssi_filter_update_fixed(rssi_filter_fixed_t *f, int32_t raw_rssi_dbm) {
    int32_t raw_q16 = raw_rssi_dbm << 16;
    
    if (!f->initialized) {
        f->filtered_rssi_q16 = raw_q16;
        f->initialized = true;
    } else {
        /* y[n] = alpha * x[n] + (1 - alpha) * y[n-1] у Q16 */
        int64_t term1 = (int64_t)f->alpha_q16 * raw_q16;
        int64_t term2 = (int64_t)(65536 - f->alpha_q16) * f->filtered_rssi_q16;
        f->filtered_rssi_q16 = (int32_t)((term1 + term2) >> 16);
    }
    
    return f->filtered_rssi_q16 >> 16; /* Повертаємо ціле значення у дБм */
}
