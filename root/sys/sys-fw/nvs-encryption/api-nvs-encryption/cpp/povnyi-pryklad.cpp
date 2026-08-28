#include "nvs_flash.h"
#include "nvs.h"
#include "esp_log.h"
#include <string_view>
#include <system_error>
#include <algorithm>
#include <cstring>

namespace sys {

class EncryptedNvsStorage {
public:
    static esp_err_t init(std::string_view partition_label) noexcept {
        const esp_partition_t* key_part = esp_partition_find_first(
            ESP_PARTITION_TYPE_DATA,
            ESP_PARTITION_SUBTYPE_DATA_NVS_KEYS,
            nullptr
        );
        if (!key_part) {
            ESP_LOGE("NVS_CPP", "Розділ nvs_keys не знайдено!");
            return ESP_ERR_NOT_FOUND;
        }

        nvs_sec_cfg_t cfg{};
        esp_err_t err = nvs_flash_read_security_cfg(key_part, &cfg);
        if (err == ESP_ERR_NVS_KEYS_NOT_INITIALIZED) {
            ESP_LOGW("NVS_CPP", "Перший запуск: генерація ключів через TRNG...");
            err = nvs_flash_generate_keys(key_part, &cfg);
        }
        if (err != ESP_OK) {
            return err;
        }

        err = nvs_flash_secure_init_partition(partition_label.data(), &cfg);

        // Гарантоване затирання конфіденційних даних у пам'яті
        std::fill(reinterpret_cast<uint8_t*>(&cfg),
                  reinterpret_cast<uint8_t*>(&cfg) + sizeof(cfg), 0);
        return err;
    }
};

} // namespace sys
