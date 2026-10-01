#include "esp_camera.h"
#include "esp_log.h"

static const char *TAG = "cam_capture";

void capture_and_process_frame(void) {
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        ESP_LOGE(TAG, "Не вдалося захопити кадр з камери");
        return;
    }

    ESP_LOGI(TAG, "Отримано кадр: %u байт, розмір %ux%u", 
             (unsigned int)fb->len, fb->width, fb->height);

    // Логіка обробки або передачі даних...

    esp_camera_fb_return(fb);
}
