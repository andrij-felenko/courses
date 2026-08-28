// Лічильник перезавантажень: кожен крок перевіряємо.
esp_err_t bump_boot_count(uint32_t *out) {
    if (out == NULL) return ESP_ERR_INVALID_ARG;

    nvs_handle_t h;
    esp_err_t err = nvs_open("storage", NVS_READWRITE, &h);
    if (err != ESP_OK) return err;

    uint32_t count = 0;
    err = nvs_get_u32(h, "boot_cnt", &count);
    // ESP_ERR_NVS_NOT_FOUND — легітимний перший старт, count лишається 0;
    // будь-яка ІНША помилка означає биті дані — не довіряємо їм.
    if (err != ESP_OK && err != ESP_ERR_NVS_NOT_FOUND) {
        nvs_close(h);
        return err;
    }

    count++;
    err = nvs_set_u32(h, "boot_cnt", count);
    if (err == ESP_OK) err = nvs_commit(h);
    nvs_close(h);

    if (err != ESP_OK) return err;
    *out = count;
    return ESP_OK;
}
