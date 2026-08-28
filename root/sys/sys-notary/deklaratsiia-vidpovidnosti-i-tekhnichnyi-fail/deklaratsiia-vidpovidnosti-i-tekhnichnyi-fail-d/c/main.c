#include <stdint.h>
#include <stdbool.h>

// Структура сертифікаційного маніфесту, інтегрована в завантажувач пристрою
typedef struct {
    uint32_t magic_header;       // Маркер валідності структури (0x54444631 = "TDF1")
    char     model_name[16];     // Назва моделі, точно як у DoC
    char     hw_revision[8];     // Апаратна ревізія плати
    char     certified_fw[16];   // Базова сертифікована версія прошивки
    int8_t   max_tx_power_dbm;   // Максимально допустимий ліміт EIRP для ЄС
    uint16_t allowed_bands_mask; // Бітова маска дозволених радіоканалів
    uint32_t doc_manifest_crc32; // CRC32 цифрового паспорта відповідності
} __attribute__((packed)) ComplianceProfile;

// Константний профіль для ринку ЄС за Директивою RED 2014/53/EU
static const ComplianceProfile EU_CERTIFIED_PROFILE = {
    .magic_header = 0x54444631,
    .model_name = "GW-100-PRO",
    .hw_revision = "HW_REV_C",
    .certified_fw = "FW_v2.4.0",
    .max_tx_power_dbm = 20,       // 20 dBm (100 мВт EIRP) за EN 300 328
    .allowed_bands_mask = 0x1FFF, // Канали 1..13 (2.4 ГГц)
    .doc_manifest_crc32 = 0x8A4F91C2
};

// Перевірка відповідності перед увімкненням радіоінтерфейсу
bool is_rf_configuration_compliant(int8_t requested_power, uint8_t channel) {
    if (requested_power > EU_CERTIFIED_PROFILE.max_tx_power_dbm) {
        return false; // Спроба перевищити задекларовану потужність блокується
    }
    if (channel < 1 || channel > 13) {
        return false; // Канал 14 у Європі суворо заборонений
    }
    return true;
}
