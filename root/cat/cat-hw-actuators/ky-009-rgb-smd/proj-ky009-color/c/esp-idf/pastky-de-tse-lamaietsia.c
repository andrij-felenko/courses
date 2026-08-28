// Ті самі коефіцієнти — тільки перед самим записом у канал.
static const uint16_t TRIM[3] = { 200, 255, 255 };   // R притлумлено, G і B на повну

static void set_color(uint8_t r, uint8_t g, uint8_t b) {
    const uint8_t raw[3] = { r, g, b };
    for (int i = 0; i < 3; i++) {
        uint8_t v = gamma8[(uint16_t)raw[i] * TRIM[i] / 255];
        ledc_set_duty(LEDC_LOW_SPEED_MODE, CH[i], v);
        ledc_update_duty(LEDC_LOW_SPEED_MODE, CH[i]);
    }
}
