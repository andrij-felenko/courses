esp_err_t load_config(uint32_t *out_value) {
    nvs_handle_t h;
    esp_err_t err = nvs_open("cfg", NVS_READONLY, &h);
    if (err != ESP_OK) {
        return err;                       // не відкрилось — повертаємо як є
    }

    err = nvs_get_u32(h, "value", out_value);
    if (err != ESP_OK) {
        nvs_close(h);                     // ВАЖЛИВО: закрити навіть на помилці
        return err;
    }

    nvs_close(h);
    return ESP_OK;
}
