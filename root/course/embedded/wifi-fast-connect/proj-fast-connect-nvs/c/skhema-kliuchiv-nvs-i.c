#include "nvs.h"
#include "nvs_flash.h"
#include "esp_log.h"

static const char *TAG = "fastconn";
#define NVS_NS  "fastconn"
#define NVS_KEY "blob"

// Записати весь стан одним блобом. Повертає ESP_OK при успіху.
static esp_err_t fastconn_save(const fastconn_t *st)
{
    nvs_handle_t h;
    esp_err_t err = nvs_open(NVS_NS, NVS_READWRITE, &h);
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "nvs_open failed: %s", esp_err_to_name(err));
        return err;
    }

    err = nvs_set_blob(h, NVS_KEY, st, sizeof(*st));
    if (err == ESP_OK) {
        err = nvs_commit(h);   // без commit запис лишиться лише в RAM-кеші
    }
    nvs_close(h);

    if (err != ESP_OK) {
        ESP_LOGW(TAG, "save failed: %s", esp_err_to_name(err));
    }
    return err;
}
