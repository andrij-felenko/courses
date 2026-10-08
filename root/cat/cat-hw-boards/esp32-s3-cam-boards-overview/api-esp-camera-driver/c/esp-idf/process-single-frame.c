#include "esp_camera.h"
#include "esp_log.h"

void process_single_frame(void) {
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        ESP_LOGE("CAM", "Не вдалося захопити кадр з камери");
        return;
    }

    ESP_LOGI("CAM", "Захоплено кадр: %u байтів, роздільність %ux%u", 
             (unsigned int)fb->len, fb->width, fb->height);

    // Виконання обробки кадру
    // ...

    // Обов'язкове повернення кадрового буфера в пул драйвера
    esp_camera_fb_return(fb);
    fb = NULL;
}
