// Контролер просить «покажи себе» — блимаємо, поки триває опізнавання.
static esp_err_t app_identification_cb(identification::callback_type_t type,
                                       uint16_t endpoint_id,
                                       uint8_t effect_id,
                                       uint8_t effect_variant,
                                       void *priv_data)
{
    if (type == identification::callback_type_t::START) {
        led_blink_start();     // почати блимати світлодіодом
    } else if (type == identification::callback_type_t::STOP) {
        led_blink_stop();      // припинити
    }
    return ESP_OK;
}
