#include "esp_ota_ops.h"

void confirm_or_rollback(void) {
    const esp_partition_t *run = esp_ota_get_running_partition();
    esp_ota_img_states_t st;
    esp_ota_get_state_partition(run, &st);

    // Образ стартує у стані PENDING_VERIFY — він «на випробуванні».
    if (st == ESP_OTA_IMG_PENDING_VERIFY) {
        if (self_test_ok()) {                          // мережа є, датчики живі?
            esp_ota_mark_app_valid_cancel_rollback();  // «я справний» → закріпити
        } else {
            esp_ota_mark_app_invalid_rollback_and_reboot(); // «зі мною біда» → відкат
        }
    }
}
