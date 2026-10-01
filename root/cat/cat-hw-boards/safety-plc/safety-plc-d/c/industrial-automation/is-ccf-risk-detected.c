// Структура діагностичної перевірки відмов спільної причини (CCF)
typedef struct {
    uint8_t  channel_a_power_ok; // Стан живлення каналу А
    uint8_t  channel_b_power_ok; // Стан живлення каналу Б
    uint16_t temp_sensor_diff;   // Розбіжність температури між каналами (°C)
    uint8_t  ccf_score;          // Поточна сумарна оцінка CCF за шкалою IEC 61508
} __attribute__((packed)) ccf_diagnostic_t;

bool is_ccf_risk_detected(const ccf_diagnostic_t *diag) {
    // Якщо розбіжність живлячих ліній або температури критична — блокуємо систему
    if (!diag->channel_a_power_ok || !diag->channel_b_power_ok || diag->temp_sensor_diff > 5) {
        return true; // Виявлено ризик відмови спільної причини
    }
    return false;
}
