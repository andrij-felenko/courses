#include "esp_log.h"
#include "esp_efuse.h"
#include "esp_efuse_table.h"
#include "esp_flash_encrypt.h"
#include "esp_secure_boot.h"

class EfuseValidator {
public:
    explicit EfuseValidator(const char* tag) : tag_(tag) {}

    void validate() const {
        ESP_LOGI(tag_, "Ініціалізація перевірки конфігурації безпеки eFuse (C++)...");
        
        checkFlashEncryption();
        checkSecureBoot();
        checkReadProtection();
        checkWriteProtection();
    }

private:
    const char* tag_;

    void checkFlashEncryption() const {
        if (esp_flash_encryption_enabled()) {
            ESP_LOGI(tag_, "Flash Encryption: УВІМКНЕНО");
        } else {
            ESP_LOGW(tag_, "Flash Encryption: ВИМКНЕНО");
        }
    }

    void checkSecureBoot() const {
        if (esp_secure_boot_enabled()) {
            ESP_LOGI(tag_, "Secure Boot V2: УВІМКНЕНО");
        } else {
            ESP_LOGW(tag_, "Secure Boot V2: ВИМКНЕНО");
        }
    }

    void checkReadProtection() const {
        // На ESP32-S3 ключ Flash Encryption зазвичай лежить у BLOCK_KEY0
        if (esp_efuse_read_field_bit(ESP_EFUSE_RD_DIS_KEY0)) {
            ESP_LOGI(tag_, "BLOCK_KEY0 (Flash Encryption): Читання заблоковано (RD_DIS). Безпечно.");
        } else {
            ESP_LOGE(tag_, "BLOCK_KEY0 (Flash Encryption): Читання ДОЗВОЛЕНО! Ключ може бути скомпрометовано.");
        }
    }

    void checkWriteProtection() const {
        if (esp_efuse_read_field_bit(ESP_EFUSE_WR_DIS_SECURE_BOOT_EN)) {
            ESP_LOGI(tag_, "Регістр SECURE_BOOT_EN: Запис заблоковано (WR_DIS). Налаштування захищено.");
        } else {
            ESP_LOGW(tag_, "Регістр SECURE_BOOT_EN: Запис дозволено. Зловмисник може змінити стан.");
        }
    }
};

extern "C" void app_main(void) {
    EfuseValidator validator("EfuseValidator");
    validator.validate();
}
