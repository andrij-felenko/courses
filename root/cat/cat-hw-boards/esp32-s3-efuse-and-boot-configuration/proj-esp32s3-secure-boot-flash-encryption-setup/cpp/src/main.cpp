#include "security_verifier.hpp"
#include "nvs_security_guard.hpp"

#include <esp_log.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

static const char* TAG = "MainApp";

extern "C" void app_main(void) {
    ESP_LOGI(TAG, "Ініціалізація точки входу app_main() системи ESP32-S3...");
    ESP_LOGI(TAG, "Запуск процедури перевірки апаратного захисту при завантаженні...");

    security::SecurityVerifier verifier;
    security::SecurityGuard boot_guard(verifier, 1500);

    security::SecurityStatus status = boot_guard.execute_audit();

    if (status != security::SecurityStatus::Ok) {
        ESP_LOGE(TAG, "Аудит безпеки ПРОВАЛЕНО з результатом: %s",
                 security::SecurityVerifier::status_to_string(status));
        return;
    }

    security::NvsSecurityGuard nvs_guard("nvs", "nvs_key", 500);

    if (!nvs_guard.is_mounted()) {
        ESP_LOGE(TAG, "Монтування зашифрованого NVS-розділу не вдалося! Блокування системи.");
        boot_guard.mark_failed();
        return;
    }

    boot_guard.mark_passed();

    ESP_LOGI(TAG, "==================================================================");
    ESP_LOGI(TAG, " УСПІХ: Апаратний аудит пройдено. Запуск захищеної системи! ");
    ESP_LOGI(TAG, "==================================================================");

    const auto& report = boot_guard.get_report();
    ESP_LOGI(TAG, "Деталі аудиту:");
    ESP_LOGI(TAG, " - Secure Boot V2:     %s", report.secure_boot_enabled ? "УВІМКНЕНО" : "ВИМКНЕНО");
    ESP_LOGI(TAG, " - Flash Encryption:   %s", report.flash_encryption_enabled ? "УВІМКНЕНО" : "ВИМКНЕНО");
    ESP_LOGI(TAG, " - NVS Encrypted:      %s", report.nvs_encrypted ? "ТАК" : "НІ");
    ESP_LOGI(TAG, " - JTAG Disabled:      %s", report.jtag_disabled ? "ТАК" : "НІ");
    ESP_LOGI(TAG, " - USB-JTAG Disabled:  %s", report.dis_usb_jtag ? "ТАК" : "НІ");
    ESP_LOGI(TAG, " - Direct Boot Dis:    %s", report.dis_direct_boot ? "ТАК" : "НІ");
    ESP_LOGI(TAG, " - Час аудиту:         %llu мкс", report.audit_duration_us);

    int cycle_counter = 0;
    while (true) {
        ESP_LOGI(TAG, "Основний захищений цикл системи виконується... Ітерація %d", ++cycle_counter);
        vTaskDelay(pdMS_TO_TICKS(5000));
    }
}
