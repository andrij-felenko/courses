// Оголошено в node::create. Кличеться на КОЖЕН запис у будь-який атрибут.
static esp_err_t app_attribute_update_cb(callback_type_t type,
                                         uint16_t endpoint_id,
                                         uint32_t cluster_id,
                                         uint32_t attribute_id,
                                         esp_matter_attr_val_t *val,
                                         void *priv_data)
{
    // Реагуємо тільки на PRE_UPDATE — «ось що збираються записати».
    // POST_UPDATE (значення вже лягло) тут нам не потрібен: ми хочемо
    // ПОГОДИТИ дію з залізом ще до того, як число стане офіційним.
    if (type != PRE_UPDATE) {
        return ESP_OK;
    }
    // Чужі endpoint нас не обходять (у нас він один, але звичка корисна).
    if (endpoint_id != s_endpoint_id) {
        return ESP_OK;
    }

    // Розбираємо, в який кластер і атрибут прийшов запис.
    if (cluster_id == Thermostat::Id) {

        if (attribute_id == Thermostat::Attributes::OccupiedHeatingSetpoint::Id) {
            // Нова ЦІЛЬОВА температура — приходить у сотих. Назад у градуси.
            float target_c = val->val.i16 / 100.0f;
            ESP_LOGI(TAG, "новий setpoint: %.2f °C", target_c);
            apply_setpoint(target_c);     // -> регулятор реле з гістерезисом
        }
        else if (attribute_id == Thermostat::Attributes::SystemMode::Id) {
            uint8_t mode = val->val.u8;   // 0=Off, 3=Cool, 4=Heat
            ESP_LOGI(TAG, "новий режим: %u", mode);
            apply_mode(mode);             // Off -> реле напевно вимкнути
        }
    }

    // ESP_OK = «дію заліза виконано, запис у модель дозволяю».
    // Повернеш помилку — SDK ВІДМОВИТЬ у записі, атрибут лишиться старим.
    return ESP_OK;
}
