#include "esp_camera.h"

// Динамічне налаштування регістрів та цикл зйомки в Arduino IDE
void capture_qxga_snapshot_arduino() {
    sensor_t *s = esp_camera_sensor_get();
    if (!s) {
        Serial.println("Сенсор камери не знайдено!");
        return;
    }

    // Налаштування внутрішнього ISP сенсора
    s->set_whitebal(s, 1);
    s->set_exposure_ctrl(s, 1);
    
    // Зміна роздільної здатності на UXGA
    s->set_framesize(s, FRAMESIZE_UXGA);
    delay(150); // Час на переналаштування внутрішніх регістрів OV3640

    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Помилка захоплення кадру!");
        return;
    }

    Serial.printf("Кадр UXGA успішно знято, обсяг: %u байт\n", fb->len);

    // Обов'язкове повернення кадрового буфера
    esp_camera_fb_return(fb);
}
