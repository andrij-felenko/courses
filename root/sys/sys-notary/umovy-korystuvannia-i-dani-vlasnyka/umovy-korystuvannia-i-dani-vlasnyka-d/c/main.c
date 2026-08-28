#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Бітові маски категорій згоди згідно з GDPR/CCPA */
#define PRIVACY_CONSENT_NONE              (0U)
#define PRIVACY_CONSENT_DIAGNOSTICS_BASIC (1U << 0) /* Рівень 1: напруга, heap, збої */
#define PRIVACY_CONSENT_ANALYTICS_USAGE   (1U << 1) /* Рівень 2: лічильники функцій */
#define PRIVACY_CONSENT_LOCATION_COARSE   (1U << 2) /* Рівень 2: огрублені координати */
#define PRIVACY_CONSENT_LOCATION_PRECISE  (1U << 3) /* Рівень 3: точний GNSS */
#define PRIVACY_CONSENT_NETWORK_TOPOLOGY  (1U << 4) /* Рівень 3: Wi-Fi BSSID / IP */
#define PRIVACY_CONSENT_USER_PROFILE      (1U << 5) /* Рівень 3: персональні дані */

/* Максимальні розміри буферів */
#define PRIVACY_MAX_ID_LEN       (32U)
#define PRIVACY_MAX_PAYLOAD_LEN  (256U)

/* Сирі телеметричні дані сенсорів та системи */
typedef struct {
    uint32_t timestamp_utc;
    float    battery_voltage;
    uint32_t free_heap_bytes;
    uint16_t crash_count;
    uint32_t button_press_count;
    double   gnss_latitude;
    double   gnss_longitude;
    char     device_serial[PRIVACY_MAX_ID_LEN];
    char     wifi_bssid[18];
} RawTelemetryData;

/* Відфільтрований пакет, готовий до відправки в хмару */
typedef struct {
    uint32_t timestamp_utc;
    float    battery_voltage;
    uint32_t free_heap_bytes;
    uint16_t crash_count;
    uint32_t button_press_count;
    double   sanitized_latitude;
    double   sanitized_longitude;
    char     anonymized_id[PRIVACY_MAX_ID_LEN];
    bool     has_location;
    bool     has_analytics;
} FilteredTelemetryPayload;

/* Контекст стану приватності пристрою */
typedef struct {
    uint32_t active_consent_mask;
    uint16_t terms_version;
    bool     opt_out_pending;
} PrivacyContext;

/* Огрублення координати: округлення до 0.01 градуса (~1.1 км) */
static double coarsen_coordinate(double raw_coord) {
    int32_t scaled = (int32_t)(raw_coord * 100.0 + (raw_coord >= 0 ? 0.5 : -0.5));
    return (double)scaled / 100.0;
}

/* Фільтрація телеметрії відповідно до маски дозволів */
bool privacy_filter_telemetry(const PrivacyContext* ctx,
                             const RawTelemetryData* in_raw,
                             FilteredTelemetryPayload* out_payload) {
    if (ctx == NULL || in_raw == NULL || out_payload == NULL) {
        return false;
    }

    /* Якщо активний прапорець повного Opt-Out — забороняємо вихідні дані */
    if (ctx->opt_out_pending || ctx->active_consent_mask == PRIVACY_CONSENT_NONE) {
        memset(out_payload, 0, sizeof(*out_payload));
        return false;
    }

    memset(out_payload, 0, sizeof(*out_payload));

    /* Базова технічна діагностика (Рівень 1 — Законний інтерес) */
    if (ctx->active_consent_mask & PRIVACY_CONSENT_DIAGNOSTICS_BASIC) {
        out_payload->timestamp_utc = in_raw->timestamp_utc;
        out_payload->battery_voltage = in_raw->battery_voltage;
        out_payload->free_heap_bytes = in_raw->free_heap_bytes;
        out_payload->crash_count = in_raw->crash_count;
    }

    /* Функціональна аналітика використання (Рівень 2 — Opt-in) */
    if (ctx->active_consent_mask & PRIVACY_CONSENT_ANALYTICS_USAGE) {
        out_payload->button_press_count = in_raw->button_press_count;
        out_payload->has_analytics = true;
    }

    /* Обробка геоданих залежно від рівня згоди */
    if (ctx->active_consent_mask & PRIVACY_CONSENT_LOCATION_PRECISE) {
        /* Точні координати (Рівень 3) */
        out_payload->sanitized_latitude = in_raw->gnss_latitude;
        out_payload->sanitized_longitude = in_raw->gnss_longitude;
        out_payload->has_location = true;
    } else if (ctx->active_consent_mask & PRIVACY_CONSENT_LOCATION_COARSE) {
        /* Огрублені координати (Рівень 2) */
        out_payload->sanitized_latitude = coarsen_coordinate(in_raw->gnss_latitude);
        out_payload->sanitized_longitude = coarsen_coordinate(in_raw->gnss_longitude);
        out_payload->has_location = true;
    }

    /* Псевдонімізація або повне вилучення серійного номера */
    if (ctx->active_consent_mask & PRIVACY_CONSENT_USER_PROFILE) {
        /* Дозволено повний серійний номер */
        strncpy(out_payload->anonymized_id, in_raw->device_serial, PRIVACY_MAX_ID_LEN - 1);
    } else {
        /* Анонімний клієнт: ідентифікатор не передається взагалі */
        out_payload->anonymized_id[0] = '\0';
    }

    return true;
}

/* Обробка запиту на негайне відкликання згоди (Opt-Out) */
void privacy_handle_opt_out(PrivacyContext* ctx) {
    if (ctx != NULL) {
        ctx->active_consent_mask = PRIVACY_CONSENT_NONE;
        ctx->opt_out_pending = true;
        /* Тут викликається скидання та затирання черг повідомлень у RAM */
    }
}
