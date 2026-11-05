#ifndef SECURITY_VERIFIER_HPP
#define SECURITY_VERIFIER_HPP

#include <cstdint>
#include <esp_err.h>

namespace security {

/**
 * @brief Статуси перевірки безпеки мікроконтролера ESP32-S3.
 */
enum class SecurityStatus {
    Ok = 0,                         ///< Всі аудити безпеки пройдено успішно
    ErrSecureBootDisabled,          ///< Secure Boot V2 вимкнено
    ErrFlashEncryptionDisabled,     ///< Шифрування Flash-пам'яті вимкнено
    ErrEfuseAuditFailed,            ///< eFuse конфігурація незахищена (наприклад, JTAG увімкнений)
    ErrNvsEncryptionFailed,         ///< Ключі шифрування NVS відсутні або некоректні
    ErrTimeoutExceeded,             ///< Перевищено таймаут перевірки апаратного захисту
    ErrHardwareTampered             ///< Виявлено некоректний стан апаратних конфігурацій
};

/**
 * @brief Детальний звіт аудиту завантажувальної безпеки.
 */
struct BootAuditReport {
    bool secure_boot_enabled{false};       ///< Прапор активності Secure Boot V2
    bool flash_encryption_enabled{false};  ///< Прапор активності Flash Encryption
    bool nvs_encrypted{false};             ///< Прапор наявності шифрування NVS
    bool jtag_disabled{false};             ///< Апаратний JTAG заблоковано через eFuse
    bool dis_usb_jtag{false};              ///< USB-JTAG порт заблоковано через eFuse
    bool dis_direct_boot{false};           ///< Пряме завантаження (Direct Boot) заблоковано
    uint32_t spi_boot_crypt_cnt{0};        ///< Значення eFuse SPI_BOOT_CRYPT_CNT
    SecurityStatus status{SecurityStatus::ErrEfuseAuditFailed}; ///< Підсумковий статус
    uint64_t audit_duration_us{0};         ///< Тривалість виконання аудиту у мікросекундах
};

/**
 * @brief Системний клас для низькорівневого аудиту апаратного захисту ESP32-S3.
 */
class SecurityVerifier {
public:
    SecurityVerifier() = default;
    ~SecurityVerifier() = default;

    SecurityVerifier(const SecurityVerifier&) = delete;
    SecurityVerifier& operator=(const SecurityVerifier&) = delete;
    SecurityVerifier(SecurityVerifier&&) = delete;
    SecurityVerifier& operator=(SecurityVerifier&&) = delete;

    /**
     * @brief Виконати повний системний аудит апаратного захисту.
     * @param out_report Вихідна структура з результатами аудиту.
     * @param timeout_ms Максимально припустимий час аудиту у мілісекундах.
     * @return esp_err_t ESP_OK якщо аудит успішний, інакше код помилки ESP-IDF.
     */
    esp_err_t perform_full_audit(BootAuditReport& out_report, uint32_t timeout_ms = 1000);

    /**
     * @brief Аудит eFuse блоків безпеки (JTAG, USB-JTAG, Direct Boot, Crypt Cnt).
     * @param report Структура звіту для оновлення прапорів.
     * @return true Якщо eFuse налаштовано безпечно.
     */
    bool check_efuse_protection(BootAuditReport& report);

    /**
     * @brief Перевірка активності Secure Boot V2.
     * @param report Структура звіту для оновлення прапорів.
     * @return true Якщо Secure Boot V2 активний.
     */
    bool check_secure_boot_v2(BootAuditReport& report);

    /**
     * @brief Перевірка апаратного шифрування Flash-пам'яті.
     * @param report Структура звіту для оновлення прапорів.
     * @return true Якщо Flash Encryption увімкнено.
     */
    bool check_flash_encryption(BootAuditReport& report);

    /**
     * @brief Валідація наявності ключів шифрування NVS у вказаному розділі.
     * @param nvs_partition Назва розділу NVS (наприклад, "nvs").
     * @param key_partition Назва розділу ключів NVS (наприклад, "nvs_key").
     * @return esp_err_t ESP_OK при наявності валідних ключів.
     */
    esp_err_t verify_nvs_keys(const char* nvs_partition, const char* key_partition);

    /**
     * @brief Перетворення статусу безпеки у текстовий рядок.
     */
    static const char* status_to_string(SecurityStatus status);
};

/**
 * @brief RAII-обгортка для автоматичного контролю безпекової сесії під час завантаження.
 */
class SecurityGuard {
public:
    /**
     * @brief Конструктор безпекового вартівника.
     * @param verifier Посилання на системний аудитор SecurityVerifier.
     * @param max_allowed_timeout_ms Ліміт часу для сесії аудиту в мс.
     */
    explicit SecurityGuard(SecurityVerifier& verifier, uint32_t max_allowed_timeout_ms = 1000);

    /**
     * @brief Деструктор RAII: при невизначеному або незахищеному стані блокує запуск системи.
     */
    ~SecurityGuard();

    SecurityGuard(const SecurityGuard&) = delete;
    SecurityGuard& operator=(const SecurityGuard&) = delete;
    SecurityGuard(SecurityGuard&&) = delete;
    SecurityGuard& operator=(SecurityGuard&&) = delete;

    /**
     * @brief Запустити аудит у межах безпекової сесії.
     * @return SecurityStatus Підсумковий статус перевірки.
     */
    SecurityStatus execute_audit();

    /**
     * @brief Підтвердити успішне проходження всіх перевірок та авторизувати запуск.
     */
    void mark_passed();

    /**
     * @brief Примусово позначити аудит як провалений.
     */
    void mark_failed();

    /**
     * @brief Чи підтверджено захищеність системи.
     */
    bool is_secured() const { return audit_passed_; }

    /**
     * @brief Отримати поточний звіт аудиту.
     */
    const BootAuditReport& get_report() const { return report_; }

private:
    SecurityVerifier& verifier_;
    BootAuditReport report_{};
    uint32_t timeout_ms_{1000};
    uint64_t start_time_us_{0};
    bool audit_passed_{false};
    bool session_completed_{false};

    void enforce_security_halt();
};

} // namespace security

#endif // SECURITY_VERIFIER_HPP
