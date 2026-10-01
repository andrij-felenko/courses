esp_err_t adjust_sensor_parameters(void) {
    sensor_t *s = esp_camera_sensor_get();
    if (!s) {
        return ESP_FAIL;
    }

    // Зміна роздільності кадру в реальному часі
    s->set_framesize(s, FRAMESIZE_VGA);
    // Налаштування яскравості (-2..2) та контрастності (-2..2)
    s->set_brightness(s, 1);
    s->set_contrast(s, 1);
    // Активація дзеркалювання та перевертання зображення
    s->set_hmirror(s, 1);
    s->set_vflip(s, 1);

    return ESP_OK;
}
