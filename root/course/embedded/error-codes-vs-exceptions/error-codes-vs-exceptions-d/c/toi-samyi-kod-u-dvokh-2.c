esp_err_t load_config(uint32_t *out_value) {
    nvs_handle_t h;
    esp_err_t err = nvs_open("cfg", NVS_READONLY, &h);
    if (err != ESP_OK) return err;        // ще нема чого прибирати

    err = nvs_get_u32(h, "value", out_value);
    // обидва шляхи сходяться на одному прибиранні:
    nvs_close(h);
    return err;                           // ESP_OK або помилка читання — як є
}
