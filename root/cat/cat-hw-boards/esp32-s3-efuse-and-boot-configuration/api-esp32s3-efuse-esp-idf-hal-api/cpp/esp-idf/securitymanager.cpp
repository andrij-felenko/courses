#include <array>
#include "esp_log.h"
#include "esp_efuse.h"
#include "esp_efuse_table.h"

class SecurityManager {
private:
    static constexpr const char *TAG = "SecurityManager";

public:
    static bool isSecureBootEnabled() noexcept {
        size_t cnt = 0;
        if (esp_efuse_read_field_cnt(ESP_EFUSE_SECURE_BOOT_EN, &cnt) == ESP_OK) {
            return cnt > 0;
        }
        return false;
    }

    static esp_err_t provisionHmacKey(esp_efuse_block_t targetBlock, 
                                      const std::array<uint8_t, 32> &keyData) noexcept {
        return esp_efuse_write_key(targetBlock,
                                   ESP_EFUSE_KEY_PURPOSE_HMAC_DOWN_ALL,
                                   keyData.data(),
                                   keyData.size());
    }
};
