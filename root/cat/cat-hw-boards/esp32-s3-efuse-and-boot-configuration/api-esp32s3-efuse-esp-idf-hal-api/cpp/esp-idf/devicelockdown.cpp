#include "esp_log.h"
#include "esp_efuse.h"
#include "esp_efuse_table.h"

class DeviceLockdown {
private:
    static constexpr const char *TAG = "DeviceLockdown";

public:
    static esp_err_t disableJtagAndLockUserBlock() noexcept {
        esp_err_t err = esp_efuse_batch_write_begin();
        if (err != ESP_OK) return err;

        err = esp_efuse_write_field_bit(ESP_EFUSE_DIS_PAD_JTAG);
        if (err != ESP_OK) {
            esp_efuse_batch_write_cancel();
            return err;
        }

        err = esp_efuse_set_write_dis_mask(1 << EFUSE_BLK3);
        if (err != ESP_OK) {
            esp_efuse_batch_write_cancel();
            return err;
        }

        return esp_efuse_batch_write_commit();
    }
};
