#ifndef NVS_SECURITY_GUARD_HPP
#define NVS_SECURITY_GUARD_HPP

#include <cstdint>
#include <cstring>
#include <esp_err.h>
#include <esp_log.h>
#include <esp_timer.h>
#include <esp_partition.h>
#include <nvs_flash.h>
#include <nvs.h>

namespace security {

/**
 * @brief RAII-обгортка для безпечної ініціалізації та автоматичного розмонтування 
 * зашифрованої NVS-пам'яті (nvs_flash_secure_init_partition).
 */
class NvsSecurityGuard {
public:
    /**
     * @brief Конструктор RAII-вартівника NVS.
     * @param nvs_partition Назва цільового NVS розділу.
     * @param key_partition Назва розділу ключів.
     * @param timeout_ms Максимальний таймаут доступу до апаратури в мс.
     */
    explicit NvsSecurityGuard(const char* nvs_partition = "nvs",
                             const char* key_partition = "nvs_key",
                             uint32_t timeout_ms = 1000)
        : nvs_partition_(nvs_partition),
          key_partition_(key_partition),
          is_mounted_(false),
          last_error_(ESP_FAIL) {
        
        static const char* TAG = "NvsSecurityGuard";
        uint64_t start_us = esp_timer_get_time();
        ESP_LOGI(TAG, "Спроба безпечного монтування NVS розділу '%s' із ключами з '%s'...",
                 nvs_partition_, key_partition_);

        std::memset(&sec_cfg_, 0, sizeof(sec_cfg_));

        const esp_partition_t* key_part = esp_partition_find_first(
            ESP_PARTITION_TYPE_DATA, ESP_PARTITION_SUBTYPE_DATA_NVS_KEYS, key_partition_);

        if (key_part == nullptr) {
            ESP_LOGE(TAG, "КРИТИЧНО: Таблиця розділів не містить розділу ключів NVS '%s'!", key_partition_);
            last_error_ = ESP_ERR_NOT_FOUND;
            return;
        }

        esp_err_t err = nvs_flash_read_security_cfg(key_part, &sec_cfg_);
        if (err != ESP_OK) {
            ESP_LOGE(TAG, "Не вдалося зчитати конфігурацію безпеки NVS (код: 0x%X)", err);
            last_error_ = err;
            std::memset(&sec_cfg_, 0, sizeof(sec_cfg_));
            return;
        }

        uint64_t elapsed_us = esp_timer_get_time() - start_us;
        if (elapsed_us > (static_cast<uint64_t>(timeout_ms) * 1000ULL)) {
            ESP_LOGE(TAG, "Перевищено таймаут апаратного зчитування ключів NVS (%llu мкс)", elapsed_us);
            last_error_ = ESP_ERR_TIMEOUT;
            std::memset(&sec_cfg_, 0, sizeof(sec_cfg_));
            return;
        }

        err = nvs_flash_secure_init_partition(nvs_partition_, &sec_cfg_);

        if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
            ESP_LOGW(TAG, "Потрібне очищення NVS (код: 0x%X). Спроба стирання та повторної ініціалізації...", err);
            err = nvs_flash_erase_partition(nvs_partition_);
            if (err == ESP_OK) {
                err = nvs_flash_secure_init_partition(nvs_partition_, &sec_cfg_);
            }
        }

        if (err == ESP_OK) {
            is_mounted_ = true;
            last_error_ = ESP_OK;
            ESP_LOGI(TAG, "Зашифрований розділ NVS '%s' успішно змонтовано (час: %llu мкс).",
                     nvs_partition_, esp_timer_get_time() - start_us);
        } else {
            ESP_LOGE(TAG, "КРИТИЧНА ПОМИЛКА: Не вдалося змонтувати шифрований NVS '%s' (код: 0x%X)",
                     nvs_partition_, err);
            last_error_ = err;
            is_mounted_ = false;
        }

        std::memset(&sec_cfg_, 0, sizeof(sec_cfg_));
    }

    /**
     * @brief Деструктор RAII: здійснює обнулення RAM-структур та безпечне розмонтування NVS.
     */
    ~NvsSecurityGuard() {
        static const char* TAG = "NvsSecurityGuard";
        std::memset(&sec_cfg_, 0, sizeof(sec_cfg_));

        if (is_mounted_) {
            ESP_LOGI(TAG, "Автоматичне RAII-розмонтування зашифрованого NVS розділу '%s'...", nvs_partition_);
            esp_err_t err = nvs_flash_deinit_partition(nvs_partition_);
            if (err != ESP_OK) {
                ESP_LOGE(TAG, "Помилка при розмонтуванні NVS розділу '%s': 0x%X", nvs_partition_, err);
            }
            is_mounted_ = false;
        }
    }

    NvsSecurityGuard(const NvsSecurityGuard&) = delete;
    NvsSecurityGuard& operator=(const NvsSecurityGuard&) = delete;

    NvsSecurityGuard(NvsSecurityGuard&& other) noexcept
        : nvs_partition_(other.nvs_partition_),
          key_partition_(other.key_partition_),
          is_mounted_(other.is_mounted_),
          last_error_(other.last_error_) {
        std::memcpy(&sec_cfg_, &other.sec_cfg_, sizeof(sec_cfg_));
        std::memset(&other.sec_cfg_, 0, sizeof(sec_cfg_));
        other.is_mounted_ = false;
        other.last_error_ = ESP_FAIL;
    }

    NvsSecurityGuard& operator=(NvsSecurityGuard&& other) noexcept {
        if (this != &other) {
            if (is_mounted_) {
                nvs_flash_deinit_partition(nvs_partition_);
            }
            nvs_partition_ = other.nvs_partition_;
            key_partition_ = other.key_partition_;
            is_mounted_ = other.is_mounted_;
            last_error_ = other.last_error_;
            std::memcpy(&sec_cfg_, &other.sec_cfg_, sizeof(sec_cfg_));
            std::memset(&other.sec_cfg_, 0, sizeof(sec_cfg_));
            other.is_mounted_ = false;
            other.last_error_ = ESP_FAIL;
        }
        return *this;
    }

    /**
     * @brief Чи змонтовано NVS розділ успішно.
     */
    bool is_mounted() const { return is_mounted_; }

    /**
     * @brief Отримати останній код помилки.
     */
    esp_err_t get_last_error() const { return last_error_; }

private:
    const char* nvs_partition_{nullptr};
    const char* key_partition_{nullptr};
    bool is_mounted_{false};
    esp_err_t last_error_{ESP_FAIL};
    nvs_sec_cfg_t sec_cfg_{};
};

} // namespace security

#endif // NVS_SECURITY_GUARD_HPP
