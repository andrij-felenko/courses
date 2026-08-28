static bool camera_start(void) {
    // Спалах сидить на GPIO4. Заганяємо його в нуль ЩЕ ДО init камери й картки,
    // щоб світлодіод не спалахнув навіть на мить.
    pinMode(4, OUTPUT);
    digitalWrite(4, LOW);

    camera_config_t config = make_camera_config();
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Камера не піднялася, помилка 0x%x\n", err);
        return false;   // далі йти немає сенсу
    }
    return true;
}
