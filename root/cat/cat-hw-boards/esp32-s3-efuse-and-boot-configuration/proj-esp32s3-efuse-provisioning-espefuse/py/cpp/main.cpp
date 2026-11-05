#include <iostream>
#include "esp_efuse.h"
#include "esp_efuse_table.h"
#include "esp_log.h"
#include "esp_secure_boot.h"

static const char *TAG = "EFUSE_DIAG_CPP";

class EfuseDiagnostic {
public:
    EfuseDiagnostic() {
        ESP_LOGI(TAG, "Ініціалізація підсистеми самодіагностики eFuse");
    }

    bool isSecureBootEnabled() const {
        return esp_secure_boot_enabled();
    }

    bool isJtagDisabled() const {
        return esp_efuse_read_field_bit(ESP_EFUSE_DIS_PAD_JTAG);
    }

    uint8_t getBlock4Purpose() const {
        uint8_t purpose = 0;
        if (esp_efuse_read_field_blob(ESP_EFUSE_KEY_PURPOSE_0, &purpose, 4) != ESP_OK) {
            ESP_LOGE(TAG, "Не вдалося зчитати призначення ключа");
            return 0; // 0 - USER / EMPTY
        }
        return purpose;
    }

    void printReport() const {
        std::cout << "\n--- Апаратний звіт безпеки ESP32-S3 ---\n";
        
        std::cout << "Статус Secure Boot v2: " 
                  << (isSecureBootEnabled() ? "АКТИВНО (завантаження перевірено)" : "ВИМКНЕНО (небезпека)") 
                  << "\n";
                  
        std::cout << "Статус JTAG інтерфейсу: " 
                  << (isJtagDisabled() ? "Блоковано" : "Відкрито") 
                  << "\n";
                  
        std::cout << "Призначення BLOCK4 (числове значення KEY_PURPOSE): " 
                  << static_cast<int>(getBlock4Purpose()) 
                  << "\n";
                  
        std::cout << "---------------------------------------\n\n";
    }
};

extern "C" void app_main() {
    EfuseDiagnostic diagnostic;
    diagnostic.printReport();
}
