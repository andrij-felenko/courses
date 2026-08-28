#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define CHALLENGE_LEN     32
#define SIGNATURE_LEN     64
#define PUBLIC_KEY_LEN    64
#define MAX_LOG_ENTRIES   16

typedef enum {
    PART_TYPE_UNKNOWN   = 0,
    PART_TYPE_BATTERY   = 1,
    PART_TYPE_DISPLAY   = 2,
    PART_TYPE_CAMERA    = 3
} part_type_t;

typedef enum {
    TRUST_LEVEL_UNTRUSTED_FALLBACK = 0, /* Стороння деталь: безпечний лімітований режим */
    TRUST_LEVEL_GENERIC_QUALIFIED  = 1, /* Сертифікований сумісний аналог */
    TRUST_LEVEL_OEM_CERTIFIED      = 2  /* Оригінальний модуль з повним калібруванням */
} trust_level_t;

typedef struct {
    uint32_t max_charge_current_ma;
    bool fast_charge_allowed;
    bool extended_telemetry_enabled;
    bool high_refresh_rate_enabled;
} system_policy_t;

typedef struct {
    part_type_t type;
    uint32_t serial_number;
    uint8_t public_key[PUBLIC_KEY_LEN];
    uint32_t factory_calibration_crc;
} part_descriptor_t;

typedef struct {
    uint32_t timestamp_sec;
    part_type_t type;
    uint32_t serial_number;
    trust_level_t assigned_trust;
} replacement_log_entry_t;

static replacement_log_entry_t s_ledger[MAX_LOG_ENTRIES];
static size_t s_ledger_count = 0;

/* Емуляція перевірки криптографічного цифрового підпису ECDSA P-256 */
static bool crypto_verify_signature(const uint8_t *pub_key, const uint8_t *challenge,
                                    size_t challenge_len, const uint8_t *signature) {
    if (!pub_key || !challenge || !signature || challenge_len == 0) {
        return false;
    }
    /* Перевірка валідності відкритого ключа та підпису */
    return (pub_key[0] != 0x00 && signature[0] != 0x00);
}

/* Оцінка рівня довіри та реєстрація заміни у локальному журналі */
trust_level_t evaluate_part_trust(const part_descriptor_t *part,
                                 const uint8_t *challenge,
                                 const uint8_t *signature,
                                 uint32_t current_time) {
    if (!part) {
        return TRUST_LEVEL_UNTRUSTED_FALLBACK;
    }

    trust_level_t level = TRUST_LEVEL_UNTRUSTED_FALLBACK;

    bool sig_ok = crypto_verify_signature(part->public_key, challenge, CHALLENGE_LEN, signature);
    if (sig_ok) {
        /* Якщо підпис зійшовся і CRC калібрування валідне — визнаємо оригінал */
        if (part->factory_calibration_crc != 0) {
            level = TRUST_LEVEL_OEM_CERTIFIED;
        } else {
            level = TRUST_LEVEL_GENERIC_QUALIFIED;
        }
    } else {
        /* Підпис відсутній або не збігся: не блокуємо, переходимо у fallback */
        level = TRUST_LEVEL_UNTRUSTED_FALLBACK;
    }

    /* Фіксація в енергонезалежному журналі замін */
    if (s_ledger_count < MAX_LOG_ENTRIES) {
        s_ledger[s_ledger_count].timestamp_sec = current_time;
        s_ledger[s_ledger_count].type = part->type;
        s_ledger[s_ledger_count].serial_number = part->serial_number;
        s_ledger[s_ledger_count].assigned_trust = level;
        s_ledger_count++;
    }

    return level;
}

/* Застосування безпечної градуйованої політики без окірпичування виробу */
void apply_system_policy(part_type_t type, trust_level_t trust, system_policy_t *out_policy) {
    if (!out_policy) return;

    if (type == PART_TYPE_BATTERY) {
        switch (trust) {
            case TRUST_LEVEL_OEM_CERTIFIED:
                out_policy->max_charge_current_ma = 4500; /* Швидка зарядка 4.5A */
                out_policy->fast_charge_allowed = true;
                out_policy->extended_telemetry_enabled = true;
                break;
            case TRUST_LEVEL_GENERIC_QUALIFIED:
                out_policy->max_charge_current_ma = 3000; /* Стандартна зарядка 3.0A */
                out_policy->fast_charge_allowed = false;
                out_policy->extended_telemetry_enabled = true;
                break;
            case TRUST_LEVEL_UNTRUSTED_FALLBACK:
            default:
                out_policy->max_charge_current_ma = 1500; /* Безпечний ліміт 1.5A через NTC */
                out_policy->fast_charge_allowed = false;
                out_policy->extended_telemetry_enabled = false;
                break;
        }
    } else if (type == PART_TYPE_DISPLAY) {
        out_policy->high_refresh_rate_enabled = (trust != TRUST_LEVEL_UNTRUSTED_FALLBACK);
    }
}
