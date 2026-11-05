#include "security_verifier.hpp"

#include <esp_log.h>
#include <esp_system.h>
#include <esp_timer.h>
#include <esp_efuse.h>
#include <esp_efuse_table.h>
#include <esp_secure_boot.h>
#include <esp_flash_encrypt.h>
#include <esp_partition.h>
#include <nvs_flash.h>
#include <nvs.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

static const char* TAG = "SecurityVerifier";

namespace security {

const char* SecurityVerifier::status_to_string(SecurityStatus status) {
    switch (status) {
        case SecurityStatus::Ok:
            return "УСПІХ: Систему захищено повністю";
        case SecurityStatus::ErrSecureBootDisabled:
            return "ПОМИЛКА: Secure Boot V2 вимкнено в eFuse";
        case SecurityStatus::ErrFlashEncryptionDisabled:
            return "ПОМИЛКА: Апаратне шифрування Flash вимкнено";
        case SecurityStatus::ErrEfuseAuditFailed:
            return "ПОМИЛКА: Критичні eFuse-регістри відладки/завантаження не заблоковані";
        case SecurityStatus::ErrNvsEncryptionFailed:
            return "ПОМИЛКА: Шифрування розділу NVS не налаштовано або некоректні ключі";
        case SecurityStatus::ErrTimeoutExceeded:
            return "ПОМИЛКА: Перевищено допустимий таймаут аудиту безпеки";
        case SecurityStatus::ErrHardwareTampered:
            return "ПОМИЛКА: Виявлено некоректний стан апаратних конфігурацій";
        default:
            return "НЕВІДОМА ПОМИЛКА БЕЗПЕКИ";
    }
}

bool SecurityVerifier::check_efuse_protection(BootAuditReport& report) {
    ESP_LOGI(TAG, "Початок перевірки конфігурації eFuse для ESP32-S3...");

    size_t bit_out = 0;

#ifdef ESP_EFUSE_DIS_PAD_JTAG
    esp_err_t err_jtag = esp_efuse_read_field_cnt(ESP_EFUSE_DIS_PAD_JTAG, &bit_out);
    report.jtag_disabled = (err_jtag == ESP_OK && bit_out > 0);
#elif defined(ESP_EFUSE_DIS_JTAG)
    esp_err_t err_jtag = esp_efuse_read_field_cnt(ESP_EFUSE_DIS_JTAG, &bit_out);
    report.jtag_disabled = (err_jtag == ESP_OK && bit_out > 0);
#else
    report.jtag_disabled = true;
#endif

#ifdef ESP_EFUSE_DIS_USB_JTAG
    bit_out = 0;
    esp_err_t err_usb_jtag = esp_efuse_read_field_cnt(ESP_EFUSE_DIS_USB_JTAG, &bit_out);
    report.dis_usb_jtag = (err_usb_jtag == ESP_OK && bit_out > 0);
#else
    report.dis_usb_jtag = true;
#endif

#ifdef ESP_EFUSE_DIS_DIRECT_BOOT
    bit_out = 0;
    esp_err_t err_direct_boot = esp_efuse_read_field_cnt(ESP_EFUSE_DIS_DIRECT_BOOT, &bit_out);
    report.dis_direct_boot = (err_direct_boot == ESP_OK && bit_out > 0);
#else
    report.dis_direct_boot = true;
#endif

#ifdef ESP_EFUSE_SPI_BOOT_CRYPT_CNT
    uint32_t crypt_cnt = 0;
    esp_err_t err_crypt = esp_efuse_read_field_blob(ESP_EFUSE_SPI_BOOT_CRYPT_CNT, &crypt_cnt, 3);
    if (err_crypt == ESP_OK) {
        report.spi_boot_crypt_cnt = crypt_cnt;
    }
#endif

    ESP_LOGI(TAG, "Статус eFuse: PAD_JTAG_DIS=%d, USB_JTAG_DIS=%d, DIRECT_BOOT_DIS=%d, CRYPT_CNT=0x%lX",
             report.jtag_disabled, report.dis_usb_jtag, report.dis_direct_boot,
             (unsigned long)report.spi_boot_crypt_cnt);

    bool efuse_ok = report.jtag_disabled && report.dis_usb_jtag && report.dis_direct_boot;
    if (!efuse_ok) {
        ESP_LOGW(TAG, "ПОПЕРЕДЖЕННЯ: eFuse містить розблоковані інтерфейси відладки або завантаження!");
    }
    return efuse_ok;
}

bool SecurityVerifier::check_secure_boot_v2(BootAuditReport& report) {
    ESP_LOGI(TAG, "Аудит стану Secure Boot V2...");
    report.secure_boot_enabled = esp_secure_boot_enabled();

    if (report.secure_boot_enabled) {
        ESP_LOGI(TAG, "Secure Boot V2 АКТИВНИЙ. Підпис прошивки перевірено апаратно.");
    } else {
        ESP_LOGE(TAG, "КРИТИЧНО: Secure Boot V2 ВИМКНЕНО! Захист підпису прошивки відсутній.");
    }
    return report.secure_boot_enabled;
}

bool SecurityVerifier::check_flash_encryption(BootAuditReport& report) {
    ESP_LOGI(TAG, "Аудит стану Flash Encryption...");
    report.flash_encryption_enabled = esp_flash_encryption_enabled();

    if (report.flash_encryption_enabled) {
        esp_flash_enc_mode_t mode = esp_get_flash_encryption_mode();
        ESP_LOGI(TAG, "Flash Encryption АКТИВНЕ. Режим шифрування: %s",
                 (mode == ESP_FLASH_ENC_MODE_RELEASE) ? "RELEASE (Серійний)" : "DEVELOPMENT (Розробка)");
    } else {
        ESP_LOGE(TAG, "КРИТИЧНО: Апаратне шифрування Flash ВИМКНЕНО! Дані у SPI Flash відкриті.");
    }
    return report.flash_encryption_enabled;
}

esp_err_t SecurityVerifier::verify_nvs_keys(const char* nvs_partition, const char* key_partition) {
    ESP_LOGI(TAG, "Перевірка ключів шифрування NVS (розділ '%s', ключі '%s')...",
             nvs_partition ? nvs_partition : "null", key_partition ? key_partition : "null");

    if (!key_partition) {
        return ESP_ERR_INVALID_ARG;
    }

    const esp_partition_t* key_part = esp_partition_find_first(
        ESP_PARTITION_TYPE_DATA, ESP_PARTITION_SUBTYPE_DATA_NVS_KEYS, key_partition);

    if (key_part == nullptr) {
        ESP_LOGE(TAG, "Розділ ключів NVS '%s' не знайдено в таблиці розділів Flash!", key_partition);
        return ESP_ERR_NOT_FOUND;
    }

    nvs_sec_cfg_t cfg;
    esp_err_t err = nvs_flash_read_security_cfg(key_part, &cfg);
    if (err == ESP_ERR_NVS_KEYS_NOT_INITIALIZED) {
        ESP_LOGE(TAG, "Ключі NVS не ініціалізовано в розділі '%s'!", key_partition);
        return err;
    } else if (err != ESP_OK) {
        ESP_LOGE(TAG, "Збій читання ключів NVS із розділу '%s', помилка: 0x%X", key_partition, err);
        return err;
    }

    ESP_LOGI(TAG, "Ключі NVS знайдено та зчитано успішно.");
    return ESP_OK;
}

esp_err_t SecurityVerifier::perform_full_audit(BootAuditReport& out_report, uint32_t timeout_ms) {
    uint64_t start_us = esp_timer_get_time();
    out_report = BootAuditReport{};

    ESP_LOGI(TAG, "================ ПОЧАТОК СИСТЕМНОГО АУДИТУ БЕЗПЕКИ ===============");

    check_secure_boot_v2(out_report);
    check_flash_encryption(out_report);
    check_efuse_protection(out_report);

    esp_err_t nvs_err = verify_nvs_keys("nvs", "nvs_key");
    out_report.nvs_encrypted = (nvs_err == ESP_OK);

    uint64_t elapsed_us = esp_timer_get_time() - start_us;
    out_report.audit_duration_us = elapsed_us;

    uint64_t timeout_us = static_cast<uint64_t>(timeout_ms) * 1000ULL;
    if (elapsed_us > timeout_us) {
        ESP_LOGE(TAG, "Аудит безпеки перевищив часовий ліміт: %llu мкс > %llu мкс",
                 elapsed_us, timeout_us);
        out_report.status = SecurityStatus::ErrTimeoutExceeded;
        return ESP_ERR_TIMEOUT;
    }

    if (!out_report.secure_boot_enabled) {
        out_report.status = SecurityStatus::ErrSecureBootDisabled;
        return ESP_ERR_INVALID_STATE;
    }

    if (!out_report.flash_encryption_enabled) {
        out_report.status = SecurityStatus::ErrFlashEncryptionDisabled;
        return ESP_ERR_INVALID_STATE;
    }

    if (!out_report.jtag_disabled || !out_report.dis_usb_jtag || !out_report.dis_direct_boot) {
        out_report.status = SecurityStatus::ErrEfuseAuditFailed;
        return ESP_ERR_INVALID_STATE;
    }

    if (!out_report.nvs_encrypted) {
        out_report.status = SecurityStatus::ErrNvsEncryptionFailed;
        return ESP_ERR_NOT_FOUND;
    }

    out_report.status = SecurityStatus::Ok;
    ESP_LOGI(TAG, "Аудит безпеки завершено УСПІШНО за %llu мкс.", elapsed_us);
    ESP_LOGI(TAG, "==================================================================");
    return ESP_OK;
}

SecurityGuard::SecurityGuard(SecurityVerifier& verifier, uint32_t max_allowed_timeout_ms)
    : verifier_(verifier),
      timeout_ms_(max_allowed_timeout_ms),
      start_time_us_(esp_timer_get_time()),
      audit_passed_(false),
      session_completed_(false) {
    ESP_LOGI(TAG, "[SecurityGuard] Безпекову завантажувальну сесію відкрито (Таймаут: %lu мс)",
             (unsigned long)timeout_ms_);
}

SecurityGuard::~SecurityGuard() {
    if (!audit_passed_) {
        ESP_LOGE(TAG, "[SecurityGuard] ДЕСТРУКТОР: Безпекову сесію закрито БЕЗ підтвердження аудиту!");
        enforce_security_halt();
    } else {
        ESP_LOGI(TAG, "[SecurityGuard] ДЕСТРУКТОР: Сесію безпеки завершено коректно. Система захищена.");
    }
}

SecurityStatus SecurityGuard::execute_audit() {
    esp_err_t err = verifier_.perform_full_audit(report_, timeout_ms_);
    session_completed_ = true;

    if (err == ESP_OK && report_.status == SecurityStatus::Ok) {
        audit_passed_ = true;
    } else {
        audit_passed_ = false;
        ESP_LOGE(TAG, "[SecurityGuard] Аудит не пройдено. Статус: %s",
                 SecurityVerifier::status_to_string(report_.status));
    }

    return report_.status;
}

void SecurityGuard::mark_passed() {
    audit_passed_ = true;
    ESP_LOGI(TAG, "[SecurityGuard] Прапор авторизації встановлено: Апаратура безпечна.");
}

void SecurityGuard::mark_failed() {
    audit_passed_ = false;
    ESP_LOGW(TAG, "[SecurityGuard] Прапор авторизації скинуто: Апаратуру компрометовано!");
}

void SecurityGuard::enforce_security_halt() {
    ESP_LOGE(TAG, "################################################################");
    ESP_LOGE(TAG, "# КРИТИЧНИЙ БЕЗПЕКОВИЙ ІНЦИДЕНТ: СПРОБА ЗАПУСКУ НА НЕЗАХИЩЕНОМУ СЕНДВІЧІ!");
    ESP_LOGE(TAG, "# БЛОКУВАННЯ ВИКОНАННЯ ОСНОВНОЇ ПРОШИВКИ ТА ПРИМУСОВИЙ RESTART #");
    ESP_LOGE(TAG, "################################################################");

    vTaskDelay(pdMS_TO_TICKS(100));
    esp_restart();
}

} // namespace security
