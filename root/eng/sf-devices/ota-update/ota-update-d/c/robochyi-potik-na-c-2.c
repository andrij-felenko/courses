#include "esp_ota_ops.h"

void confirm_or_rollback(void) {
    // Викликати ПІСЛЯ старту, коли переконались, що все головне працює:
    if (self_test_passed()) {                          // мережа є, датчики ок, ...
        esp_ota_mark_app_valid_cancel_rollback();      // «я справний» → закріпити назавжди
    } else {
        esp_ota_mark_app_invalid_rollback_and_reboot();// «зі мною біда» → негайно відкотитись
    }
}
