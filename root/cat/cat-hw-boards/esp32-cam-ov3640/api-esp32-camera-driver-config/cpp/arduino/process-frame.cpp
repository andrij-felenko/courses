#include "esp_camera.h"

void process_frame() {
    // Зчитування кадру
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Захоплення кадру не вдалося");
        return;
    }

    // Використання масиву fb->buf розміром fb->len
    Serial.printf("Кадр розгружено: %u байт\n", fb->len);

    // Звільнення дескриптора
    esp_camera_fb_return(fb);
}
