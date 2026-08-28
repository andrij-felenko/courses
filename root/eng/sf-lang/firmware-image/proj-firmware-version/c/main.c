#include "esp_ota_ops.h"
#include "esp_log.h"
#include "app_version.h"      // згенерований збіркою

static const char *TAG = "boot";

void log_firmware_version(void) {
    const esp_app_desc_t *app = esp_ota_get_app_description();
    ESP_LOGI(TAG, "git:   %s", APP_GIT_VERSION);
    ESP_LOGI(TAG, "ver:   %s", app->version);
    ESP_LOGI(TAG, "built: %s %s", app->date, app->time);
    ESP_LOGI(TAG, "idf:   %s", app->idf_ver);
}
