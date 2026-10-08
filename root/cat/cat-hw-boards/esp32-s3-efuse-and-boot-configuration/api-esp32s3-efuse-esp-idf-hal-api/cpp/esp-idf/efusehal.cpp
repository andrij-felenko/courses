#include <array>
#include "esp_log.h"
#include "esp_efuse.h"
#include "esp_efuse_table.h"

class EfuseHal {
private:
    static constexpr const char *TAG = "EfuseHal";

public:
    static esp_err_t getFactoryMac(std::array<uint8_t, 6> &mac) noexcept {
        esp_err_t err = esp_efuse_read_field_blob(ESP_EFUSE_MAC_FACTORY, mac.data(), mac.size() * 8);
        if (err != ESP_OK) {
            ESP_LOGE(TAG, "Помилка зчитування MAC: %s", esp_err_to_name(err));
        }
        return err;
    }

    static esp_err_t setUserIdTransactional(uint32_t userId) noexcept {
        esp_err_t err = esp_efuse_batch_write_begin();
        if (err != ESP_OK) return err;

        err = esp_efuse_write_field_blob(ESP_EFUSE_USER_DATA, &userId, 32);
        if (err != ESP_OK) {
            esp_efuse_batch_write_cancel();
            return err;
        }

        return esp_efuse_batch_write_commit();
    }
};
