#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stddef.h>

#define CRYPTO_CHALLENGE_SIZE     32
#define CRYPTO_SIGNATURE_SIZE     64
#define CRYPTO_PUBKEY_SIZE        64
#define MAX_LEDGER_CAPACITY       32
#define LOG_ENTRY_MAGIC           0x52504C47UL /* 'RPLG' */

typedef enum {
    ERR_OK                  = 0,
    ERR_INVALID_ARG         = -1,
    ERR_SIG_VERIFY_FAIL     = -2,
    ERR_CRC_MISMATCH        = -3,
    ERR_LEDGER_FULL         = -4,
    ERR_HARDWARE_FAULT      = -5
} status_code_t;

typedef enum {
    MODULE_TYPE_UNKNOWN     = 0,
    MODULE_TYPE_BATTERY     = 1,
    MODULE_TYPE_DISPLAY     = 2,
    MODULE_TYPE_CAMERA      = 3,
    MODULE_TYPE_SENSOR_HUB  = 4
} module_type_t;

typedef enum {
    TRUST_UNTRUSTED_FALLBACK = 0, /* Невідомий або непідписаний модуль: безпечний лімітований режим */
    TRUST_GENERIC_QUALIFIED  = 1, /* Сертифікований сумісний модуль стороннього виробника */
    TRUST_OEM_CERTIFIED      = 2  /* Оригінальний модуль з повним фабричним профілем */
} module_trust_t;

typedef struct {
    int32_t offset_uv;          /* Зміщення нуля в мікровольтах */
    int32_t gain_err_ppm;       /* Похибка коефіцієнта підсилення в ppm */
    int16_t temp_drift_coeff;   /* Температурний коефіцієнт дрейфу */
    uint32_t calib_crc32;       /* Контрольна сума CRC32 калібрувального блоку */
} calibration_block_t;

typedef struct {
    module_type_t type;
    uint32_t hardware_rev;
    uint32_t serial_number;
    uint8_t public_key[CRYPTO_PUBKEY_SIZE];
    uint32_t max_safe_current_ma;
    uint8_t max_safe_temp_c;
    calibration_block_t calib;
} module_descriptor_t;

typedef struct {
    uint32_t magic;
    uint64_t timestamp_utc;
    uint32_t module_type;
    uint32_t serial_number;
    uint32_t assigned_trust;
    uint32_t checksum;
} log_entry_t;

typedef struct {
    uint32_t configured_max_current_ma;
    uint8_t max_allowed_temp_c;
    bool fast_charge_enabled;
    bool high_precision_mode;
    bool service_warning_active;
} active_power_policy_t;

typedef struct {
    log_entry_t entries[MAX_LEDGER_CAPACITY];
    size_t count;
    uint8_t active_challenge[CRYPTO_CHALLENGE_SIZE];
    bool challenge_in_flight;
} trust_subsystem_t;

static trust_subsystem_t s_trust_ctx;

/* Проста реалізація табличного CRC32 за стандартом IEEE 802.3 */
static uint32_t compute_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFUL;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int b = 0; b < 8; ++b) {
            crc = (crc >> 1) ^ ((crc & 1) ? 0xEDB88320UL : 0);
        }
    }
    return ~crc;
}

/* Ініціалізація підсистеми довіри та журналу замін */
status_code_t trust_subsystem_init(void) {
    memset(&s_trust_ctx, 0, sizeof(s_trust_ctx));
    return ERR_OK;
}

/* Генерація 256-бітного виклику для підтвердження свіжості сесії */
status_code_t trust_generate_challenge(uint8_t *out_challenge, size_t challenge_len) {
    if (!out_challenge || challenge_len != CRYPTO_CHALLENGE_SIZE) {
        return ERR_INVALID_ARG;
    }

    /* Емуляція апаратного TRNG: заповнюємо псевдовипадковими даними */
    for (size_t i = 0; i < CRYPTO_CHALLENGE_SIZE; ++i) {
        s_trust_ctx.active_challenge[i] = (uint8_t)((i * 37 + 0x5A) ^ 0xAA);
        out_challenge[i] = s_trust_ctx.active_challenge[i];
    }
    s_trust_ctx.challenge_in_flight = true;
    return ERR_OK;
}

/* Емуляція перевірки цифрового підпису ECDSA P-256 */
static bool verify_ecdsa_signature(const uint8_t *pub_key, const uint8_t *challenge,
                                   const uint8_t *signature) {
    if (!pub_key || !challenge || !signature) {
        return false;
    }
    /* Перевіряємо, що ключ і підпис не є повністю нульовими */
    return (pub_key[0] == 0x04 && signature[0] != 0x00);
}

/* Оцінка рівня довіри та реєстрація заміни у Flash-журналі */
status_code_t trust_evaluate_and_log(const module_descriptor_t *descriptor,
                                    const uint8_t *signature,
                                    size_t sig_len,
                                    uint64_t current_time_utc,
                                    module_trust_t *out_trust,
                                    active_power_policy_t *out_policy) {
    if (!descriptor || !signature || sig_len != CRYPTO_SIGNATURE_SIZE || !out_trust || !out_policy) {
        return ERR_INVALID_ARG;
    }

    if (!s_trust_ctx.challenge_in_flight) {
        return ERR_HARDWARE_FAULT;
    }

    module_trust_t trust = TRUST_UNTRUSTED_FALLBACK;
    bool sig_valid = verify_ecdsa_signature(descriptor->public_key,
                                            s_trust_ctx.active_challenge,
                                            signature);

    /* Перевірка цілісності блоку калібрування */
    uint32_t expected_crc = compute_crc32((const uint8_t *)&descriptor->calib,
                                          offsetof(calibration_block_t, calib_crc32));
    bool calib_valid = (expected_crc == descriptor->calib.calib_crc32);

    if (sig_valid && calib_valid) {
        /* Якщо відкритий ключ належить відомому діапазону OEM */
        if (descriptor->public_key[1] >= 0x80) {
            trust = TRUST_OEM_CERTIFIED;
        } else {
            trust = TRUST_GENERIC_QUALIFIED;
        }
    } else {
        /* При збої підпису не блокуємо пристрій, а переводимо у безпечний захисний режим */
        trust = TRUST_UNTRUSTED_FALLBACK;
    }

    /* Формування адаптивної безпечної політики без відключення системи */
    if (descriptor->type == MODULE_TYPE_BATTERY) {
        switch (trust) {
            case TRUST_OEM_CERTIFIED:
                out_policy->configured_max_current_ma = descriptor->max_safe_current_ma; /* Наприклад, 4500 мА */
                out_policy->max_allowed_temp_c = descriptor->max_safe_temp_c;           /* До 55 °C */
                out_policy->fast_charge_enabled = true;
                out_policy->high_precision_mode = true;
                out_policy->service_warning_active = false;
                break;
            case TRUST_GENERIC_QUALIFIED:
                out_policy->configured_max_current_ma = 3000;                           /* Обмеження 3.0 А */
                out_policy->max_allowed_temp_c = 50;                                    /* Консервативний ліміт */
                out_policy->fast_charge_enabled = false;
                out_policy->high_precision_mode = true;
                out_policy->service_warning_active = false;
                break;
            case TRUST_UNTRUSTED_FALLBACK:
            default:
                out_policy->configured_max_current_ma = 1500;                           /* Безпечний ліміт 1.5 А */
                out_policy->max_allowed_temp_c = 45;                                    /* Суворий контроль АЦП */
                out_policy->fast_charge_enabled = false;
                out_policy->high_precision_mode = false;
                out_policy->service_warning_active = true;
                break;
        }
    } else {
        out_policy->configured_max_current_ma = descriptor->max_safe_current_ma;
        out_policy->max_allowed_temp_c = descriptor->max_safe_temp_c;
        out_policy->fast_charge_enabled = false;
        out_policy->high_precision_mode = (trust != TRUST_UNTRUSTED_FALLBACK);
        out_policy->service_warning_active = (trust == TRUST_UNTRUSTED_FALLBACK);
    }

    /* Фіксація в енергонезалежному журналі замін */
    if (s_trust_ctx.count < MAX_LEDGER_CAPACITY) {
        log_entry_t *entry = &s_trust_ctx.entries[s_trust_ctx.count];
        entry->magic = LOG_ENTRY_MAGIC;
        entry->timestamp_utc = current_time_utc;
        entry->module_type = (uint32_t)descriptor->type;
        entry->serial_number = descriptor->serial_number;
        entry->assigned_trust = (uint32_t)trust;
        entry->checksum = compute_crc32((const uint8_t *)entry,
                                        offsetof(log_entry_t, checksum));
        s_trust_ctx.count++;
    }

    s_trust_ctx.challenge_in_flight = false;
    *out_trust = trust;
    return ERR_OK;
}
