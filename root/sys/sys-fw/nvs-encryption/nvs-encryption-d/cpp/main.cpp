#include <iostream>
#include <string_view>
#include <memory>
#include <vector>
#include <algorithm>
#include <cstring>
#include "esp_log.h"
#include "nvs_flash.h"
#include "nvs.h"

namespace storage {

class NvsHandleWrapper {
public:
    explicit NvsHandleWrapper(nvs_handle_t handle) noexcept : handle_(handle) {}
    ~NvsHandleWrapper() noexcept {
        if (handle_ != 0) {
            nvs_close(handle_);
        }
    }

    NvsHandleWrapper(const NvsHandleWrapper&) = delete;
    NvsHandleWrapper& operator=(const NvsHandleWrapper&) = delete;

    NvsHandleWrapper(NvsHandleWrapper&& other) noexcept : handle_(other.handle_) {
        other.handle_ = 0;
    }

    [[nodiscard]] nvs_handle_t get() const noexcept { return handle_; }
    [[nodiscard]] bool is_valid() const noexcept { return handle_ != 0; }

private:
    nvs_handle_t handle_{0};
};

class SecureNvsStore {
public:
    static esp_err_t initialize() noexcept {
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
            ESP_LOGW("NVS_CPP", "Створення нових ключів NVS...");
            err = nvs_flash_generate_keys(key_part, &cfg);
        }
        if (err != ESP_OK) {
            return err;
        }

        err = nvs_flash_secure_init(&cfg);

        // Гарантоване затирання локальної структури ключів у пам'яті
        std::fill(reinterpret_cast<uint8_t*>(&cfg),
                  reinterpret_cast<uint8_t*>(&cfg) + sizeof(cfg), 0);
        return err;
    }

    static esp_err_t save_secret_string(std::string_view nspace,
                                        std::string_view key,
                                        std::string_view value) {
        nvs_handle_t raw_h{0};
        esp_err_t err = nvs_open(nspace.data(), NVS_READWRITE, &raw_h);
        if (err != ESP_OK) {
            return err;
        }
        NvsHandleWrapper handle(raw_h);

        err = nvs_set_str(handle.get(), key.data(), value.data());
        if (err == ESP_OK) {
            err = nvs_commit(handle.get());
        }
        return err;
    }
};

} // namespace storage
