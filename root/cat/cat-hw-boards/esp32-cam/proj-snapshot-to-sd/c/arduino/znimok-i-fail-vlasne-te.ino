static bool save_photo(const char *path) {
    // 1. Просимо драйвер камери віддати готовий кадр.
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Не вдалося зняти кадр");
        return false;
    }

    // 2. Відкриваємо файл на картці для запису.
    File file = SD_MMC.open(path, FILE_WRITE);
    if (!file) {
        Serial.printf("Не відкрити файл %s\n", path);
        esp_camera_fb_return(fb);   // буфер усе одно ПОВЕРНУТИ
        return false;
    }

    // 3. Ллємо стиснені байти JPEG у файл одним махом.
    file.write(fb->buf, fb->len);   // fb->buf — адреса, fb->len — довжина
    file.close();

    Serial.printf("Збережено %s  (%u байт)\n", path, (unsigned)fb->len);

    // 4. ОБОВ'ЯЗКОВО повертаємо буфер драйверу.
    esp_camera_fb_return(fb);
    return true;
}
