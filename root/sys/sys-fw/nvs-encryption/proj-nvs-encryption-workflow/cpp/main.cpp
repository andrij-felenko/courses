#include <iostream>
#include <string_view>
#include <vector>
#include <memory>
#include <span>
#include <algorithm>
#include <cstring>
#include "esp_log.h"
#include "nvs_flash.h"
#include "nvs.h"

namespace production {

class ScopedNvsHandle {
public:
    explicit ScopedNvsHandle(nvs_handle_t handle) noexcept : handle_(handle) {}
    ~ScopedNvsHandle() noexcept {
        if (handle_ != 0) {
            nvs_close(handle_);
        }
    }

    ScopedNvsHandle(const ScopedNvsHandle&) = delete;
    ScopedNvsHandle& operator=(const ScopedNvsHandle&) = delete;

    ScopedNvsHandle(ScopedNvsHandle&& other) noexcept : handle_(other.handle_) {
        other.handle_ = 0;
    }

    [[nodiscard]] nvs_handle_t get() const noexcept { return handle_; }
    [[nodiscard]] bool valid() const noexcept { return handle_ != 0; }

private:
    nvs_handle_t handle_{0};
};

class SecureProductionStorage {
public:
    static esp_err_t initialize_and_verify(std::string_view partition_name) noexcept {
        const esp_partition_t* key_part = esp_partition_find_first(
            ESP_PARTITION_TYPE_DATA,
            ESP_PARTITION_SUBTYPE_DATA_NVS_KEYS,
            nullptr
        );
        if (!key_part) {
            ESP_LOGE("NVS_PROJ", "Розділ nvs_keys не знайдено!");
            return ESP_ERR_NOT_FOUND;
        }

        nvs_sec_cfg_t cfg{};
        esp_err_t err = nvs_flash_read_security_cfg(key_part, &cfg);
        if (err == ESP_ERR_NVS_KEYS_NOT_INITIALIZED) {
            ESP_LOGW("NVS_PROJ", "Генерація ключів NVS на чіпі...");
            err = nvs_flash_generate_keys(key_part, &cfg);
        }
        if (err != ESP_OK) {
            return err;
        }

        err = nvs_flash_secure_init_partition(partition_name.data(), &cfg);

        // Безпечне затирання локальної структури ключів
        std::fill(reinterpret_cast<uint8_t*>(&cfg),
                  reinterpret_cast<uint8_t*>(&cfg) + sizeof(cfg), 0);
        return err;
    }

    static esp_err_t read_secret_blob(std::string_view part_name,
                                      std::string_view nspace,
                                      std::string_view key,
                                      std::vector<uint8_t>& output_buffer) {
        nvs_handle_t raw_h{0};
        esp_err_t err = nvs_open_from_partition(part_name.data(), nspace.data(), NVS_READONLY, &raw_h);
        if (err != ESP_OK) {
            return err;
        }
        ScopedNvsHandle handle(raw_h);

        size_t required_len = 0;
        err = nvs_get_blob(handle.get(), key.data(), nullptr, &required_len);
        if (err != ESP_OK || required_len == 0) {
            return err;
        }

        output_buffer.resize(required_len);
        return nvs_get_blob(handle.get(), key.data(), output_buffer.data(), &required_len);
    }
};

} // namespace production
