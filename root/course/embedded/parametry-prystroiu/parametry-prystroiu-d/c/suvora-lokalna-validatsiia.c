// Валідація конфігурації на основі таблиці дескрипторів (C99)
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef enum {
    VAL_OK = 0,
    VAL_ERR_BOUNDS,
    VAL_ERR_STRING_LEN,
    VAL_ERR_READ_ONLY,
    VAL_ERR_RELATION
} val_result_t;

typedef struct {
    uint16_t key_id;
    uint8_t  type;
    uint16_t offset;
    uint16_t size;
    int32_t  min_val;
    int32_t  max_val;
    uint16_t flags;
} param_desc_t;

typedef struct {
    char     wifi_ssid[32];
    uint32_t report_interval_s;
    uint32_t timeout_s;
    uint16_t mqtt_port;
    uint8_t  tls_enable;
    uint32_t device_serial; // Read-Only
} __attribute__((packed)) app_config_t;

static const param_desc_t CONFIG_SCHEMA[] = {
    { 0x0001, 5 /* STRING */, offsetof(app_config_t, wifi_ssid), 32, 1, 31, 0 },
    { 0x0002, 3 /* UINT32 */, offsetof(app_config_t, report_interval_s), 4, 1, 86400, 0 },
    { 0x0003, 3 /* UINT32 */, offsetof(app_config_t, timeout_s), 4, 5, 3600, 0 },
    { 0x0004, 3 /* UINT32 */, offsetof(app_config_t, mqtt_port), 2, 1, 65535, 0 },
    { 0x0005, 1 /* BOOL */,   offsetof(app_config_t, tls_enable), 1, 0, 1, 0 },
    { 0x0006, 3 /* UINT32 */, offsetof(app_config_t, device_serial), 4, 0, 0, 0x0001 /* READ_ONLY */ }
};

#define SCHEMA_PARAMS_COUNT (sizeof(CONFIG_SCHEMA) / sizeof(CONFIG_SCHEMA[0]))

val_result_t validate_config_candidate(const app_config_t *cand, const app_config_t *active) {
    const uint8_t *base = (const uint8_t*)cand;

    for (size_t i = 0; i < SCHEMA_PARAMS_COUNT; ++i) {
        const param_desc_t *d = &CONFIG_SCHEMA[i];
        const void *field_ptr = base + d->offset;

        // 1. Заборона модифікації Read-Only параметрів
        if (d->flags & 0x0001) {
            const uint8_t *act_base = (const uint8_t*)active;
            if (memcmp(field_ptr, act_base + d->offset, d->size) != 0) {
                return VAL_ERR_READ_ONLY;
            }
            continue;
        }

        // 2. Перевірка цілочисельних меж
        if (d->type == 3 /* UINT32 */) {
            uint32_t val = (d->size == 2) ? *(const uint16_t*)field_ptr : *(const uint32_t*)field_ptr;
            if ((int32_t)val < d->min_val || (int32_t)val > d->max_val) {
                return VAL_ERR_BOUNDS;
            }
        } else if (d->type == 5 /* STRING */) {
            size_t len = strnlen((const char*)field_ptr, d->size);
            if (len < (size_t)d->min_val || len > (size_t)d->max_val || len == d->size) {
                return VAL_ERR_STRING_LEN; // Рядок не null-термінований або виходить за межі
            }
        }
    }

    // 3. Крос-параметричні правила (Relational Constraints)
    if (cand->timeout_s <= (cand->report_interval_s * 2)) {
        return VAL_ERR_RELATION; // Таймаут зобов'язаний бути більшим за подвійний період звітування
    }

    if (cand->tls_enable && cand->mqtt_port == 1883) {
        return VAL_ERR_RELATION; // 1883 - відкритий незахищений порт, несумісний із TLS
    }

    return VAL_OK;
}
