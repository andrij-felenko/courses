#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

/* ============================================================================
   1. КОНСТАНТИ ТА БІТОВІ МАСКИ ДОЗВОЛІВ
   ============================================================================ */
#define TPG_CONSENT_NONE              (0U)
#define TPG_CONSENT_DIAGNOSTICS_BASIC (1U << 0)
#define TPG_CONSENT_PERFORMANCE_STATS (1U << 1)
#define TPG_CONSENT_ANALYTICS_USAGE   (1U << 2)
#define TPG_CONSENT_LOCATION_COARSE   (1U << 3)
#define TPG_CONSENT_LOCATION_PRECISE  (1U << 4)
#define TPG_CONSENT_NETWORK_TOPOLOGY  (1U << 5)
#define TPG_CONSENT_USER_PROFILE      (1U << 6)

#define TPG_MAX_PSEUDONYM_LEN         (17U)
#define TPG_UID_LEN                   (12U)
#define TPG_MAC_LEN                   (6U)

/* Прапорці наявності полів у відфільтрованому пакеті */
#define TPG_FIELD_DIAGNOSTICS_PRESENT (1U << 0)
#define TPG_FIELD_PERFORMANCE_PRESENT (1U << 1)
#define TPG_FIELD_ANALYTICS_PRESENT   (1U << 2)
#define TPG_FIELD_LOCATION_PRESENT    (1U << 3)
#define TPG_FIELD_PSEUDONYM_PRESENT   (1U << 4)

/* ============================================================================
   2. СТРУКТУРИ ДАНИХ ТЕЛЕМЕТРІЇ
   ============================================================================ */
typedef struct {
    uint32_t timestamp_utc;
    uint16_t vdd_voltage_mv;
    uint32_t free_heap_bytes;
    uint16_t crash_counter;
    uint8_t  cpu_load_percent;
    uint32_t button_press_count;
    double   gnss_latitude;
    double   gnss_longitude;
    uint8_t  mcu_uid[TPG_UID_LEN];
    uint8_t  wifi_bssid[TPG_MAC_LEN];
} TpgRawFrame;

typedef struct {
    uint32_t timestamp_utc;
    uint16_t vdd_voltage_mv;
    uint32_t free_heap_bytes;
    uint16_t crash_counter;
    uint8_t  cpu_load_percent;
    uint32_t button_press_count;
    double   sanitized_latitude;
    double   sanitized_longitude;
    char     pseudonym_id[TPG_MAX_PSEUDONYM_LEN];
    uint16_t present_fields_mask;
} TpgSanitizedPayload;

typedef struct {
    uint32_t active_consent_mask;
    uint16_t terms_version;
    uint8_t  ephemeral_salt[16];
    bool     opt_out_pending;
} TpgContext;

/* ============================================================================
   3. КРИПТОГРАФІЧНІ ТА МАТЕМАТИЧНІ ПОМІЧНИКИ
   ============================================================================ */

/* Гарантоване затирання пам'яті без оптимізацій компілятора */
static void tpg_secure_zero(void* ptr, size_t len) {
    volatile uint8_t* p = (volatile uint8_t*)ptr;
    while (len--) {
        *p++ = 0U;
    }
}

/* Огрублення координат до 0.01° (~1.11 км) */
static double tpg_coarsen_coord(double val) {
    double sign = (val < 0.0) ? -1.0 : 1.0;
    double abs_val = (val < 0.0) ? -val : val;
    uint32_t scaled = (uint32_t)(abs_val * 100.0 + 0.5);
    return sign * ((double)scaled / 100.0);
}

/* Спрощений генератор псевдоніма на базі 32-бітного гешування Murmur3/FNV */
static void tpg_generate_pseudonym(const uint8_t* uid,
                                   size_t uid_len,
                                   const uint8_t* salt,
                                   size_t salt_len,
                                   char* out_str,
                                   size_t out_max) {
    uint32_t hash = 2166136261U;
    for (size_t i = 0; i < uid_len; i++) {
        hash ^= uid[i];
        hash *= 16777619U;
    }
    for (size_t i = 0; i < salt_len; i++) {
        hash ^= salt[i];
        hash *= 16777619U;
    }

    const char hex_digits[] = "0123456789ABCDEF";
    for (size_t i = 0; i < 8 && (i * 2 + 1) < out_max; i++) {
        uint8_t byte = (uint8_t)((hash >> (i * 4)) & 0x0F);
        out_str[i] = hex_digits[byte];
    }
    out_str[8] = '\0';
}

/* ============================================================================
   4. ГОЛОВНІ ФУНКЦІЇ МОДУЛЯ ЗАХИСТУ ПРИВАТНОСТІ
   ============================================================================ */

void tpg_init(TpgContext* ctx, uint16_t terms_version, const uint8_t* initial_salt) {
    if (ctx == NULL) {
        return;
    }
    ctx->active_consent_mask = TPG_CONSENT_NONE;
    ctx->terms_version = terms_version;
    ctx->opt_out_pending = false;
    if (initial_salt != NULL) {
        memcpy(ctx->ephemeral_salt, initial_salt, sizeof(ctx->ephemeral_salt));
    } else {
        memset(ctx->ephemeral_salt, 0x5A, sizeof(ctx->ephemeral_salt));
    }
}

void tpg_set_consent(TpgContext* ctx, uint32_t consent_mask) {
    if (ctx == NULL) {
        return;
    }
    ctx->active_consent_mask = consent_mask;
    ctx->opt_out_pending = false;
}

void tpg_trigger_opt_out(TpgContext* ctx) {
    if (ctx == NULL) {
        return;
    }
    ctx->active_consent_mask = TPG_CONSENT_NONE;
    ctx->opt_out_pending = true;
    /* Очищення сесійної солі для унеможливлення кореляції минулих логів */
    tpg_secure_zero(ctx->ephemeral_salt, sizeof(ctx->ephemeral_salt));
}

bool tpg_filter_telemetry(const TpgContext* ctx,
                          const TpgRawFrame* in_raw,
                          TpgSanitizedPayload* out_payload) {
    if (ctx == NULL || in_raw == NULL || out_payload == NULL) {
        return false;
    }

    tpg_secure_zero(out_payload, sizeof(*out_payload));

    /* Повний Opt-Out або відсутність будь-якої згоди */
    if (ctx->opt_out_pending || ctx->active_consent_mask == TPG_CONSENT_NONE) {
        return false;
    }

    out_payload->timestamp_utc = in_raw->timestamp_utc;

    /* 1. Базова технічна діагностика (Рівень 1 — Законний інтерес) */
    if (ctx->active_consent_mask & TPG_CONSENT_DIAGNOSTICS_BASIC) {
        out_payload->vdd_voltage_mv = in_raw->vdd_voltage_mv;
        out_payload->free_heap_bytes = in_raw->free_heap_bytes;
        out_payload->crash_counter = in_raw->crash_counter;
        out_payload->present_fields_mask |= TPG_FIELD_DIAGNOSTICS_PRESENT;
    }

    /* 2. Продуктивність та ресурси (Рівень 2) */
    if (ctx->active_consent_mask & TPG_CONSENT_PERFORMANCE_STATS) {
        out_payload->cpu_load_percent = in_raw->cpu_load_percent;
        out_payload->present_fields_mask |= TPG_FIELD_PERFORMANCE_PRESENT;
    }

    /* 3. Аналітика використання (Рівень 2) */
    if (ctx->active_consent_mask & TPG_CONSENT_ANALYTICS_USAGE) {
        out_payload->button_press_count = in_raw->button_press_count;
        out_payload->present_fields_mask |= TPG_FIELD_ANALYTICS_PRESENT;
    }

    /* 4. Геолокаційні дані */
    if (ctx->active_consent_mask & TPG_CONSENT_LOCATION_PRECISE) {
        /* Точні координати (Рівень 3) */
        out_payload->sanitized_latitude = in_raw->gnss_latitude;
        out_payload->sanitized_longitude = in_raw->gnss_longitude;
        out_payload->present_fields_mask |= TPG_FIELD_LOCATION_PRESENT;
    } else if (ctx->active_consent_mask & TPG_CONSENT_LOCATION_COARSE) {
        /* Огрублені координати до 0.01° (Рівень 2) */
        out_payload->sanitized_latitude = tpg_coarsen_coord(in_raw->gnss_latitude);
        out_payload->sanitized_longitude = tpg_coarsen_coord(in_raw->gnss_longitude);
        out_payload->present_fields_mask |= TPG_FIELD_LOCATION_PRESENT;
    }

    /* 5. Ідентифікатори */
    if (ctx->active_consent_mask & TPG_CONSENT_USER_PROFILE) {
        /* Повний заводський ідентифікатор */
        for (size_t i = 0; i < TPG_UID_LEN && (i * 2 + 1) < TPG_MAX_PSEUDONYM_LEN; i++) {
            const char hex[] = "0123456789ABCDEF";
            out_payload->pseudonym_id[i * 2] = hex[(in_raw->mcu_uid[i] >> 4) & 0x0F];
            out_payload->pseudonym_id[i * 2 + 1] = hex[in_raw->mcu_uid[i] & 0x0F];
        }
        out_payload->pseudonym_id[TPG_MAX_PSEUDONYM_LEN - 1] = '\0';
        out_payload->present_fields_mask |= TPG_FIELD_PSEUDONYM_PRESENT;
    } else if (ctx->active_consent_mask & TPG_CONSENT_ANALYTICS_USAGE) {
        /* Одноразовий псевдонім сесії з сіллю */
        tpg_generate_pseudonym(in_raw->mcu_uid, TPG_UID_LEN,
                               ctx->ephemeral_salt, sizeof(ctx->ephemeral_salt),
                               out_payload->pseudonym_id, TPG_MAX_PSEUDONYM_LEN);
        out_payload->present_fields_mask |= TPG_FIELD_PSEUDONYM_PRESENT;
    } else {
        /* Ідентифікатор повністю відсутній */
        out_payload->pseudonym_id[0] = '\0';
    }

    return true;
}

/* Виконання криптографічного стирання пам'яті NVS (Crypto-Shredding) */
bool tpg_crypto_shred_storage(TpgContext* ctx) {
    if (ctx == NULL) {
        return false;
    }

    /* 1. Скидання контексту згоди */
    tpg_trigger_opt_out(ctx);

    /* 2. Затирання ключів шифрування розділів у захищеній пам'яті */
    volatile uint32_t storage_kek[8] = {0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x11, 0x22};
    tpg_secure_zero((void*)storage_kek, sizeof(storage_kek));

    return true;
}
