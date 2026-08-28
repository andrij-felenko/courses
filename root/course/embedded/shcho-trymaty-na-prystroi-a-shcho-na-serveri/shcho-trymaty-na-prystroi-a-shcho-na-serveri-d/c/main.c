#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define CONFIG_MAGIC 0x43464731U /* "CFG1" */
#define MAX_DEVICE_NAME_LEN 32

/* Апаратні обмеження безпеки */
#define MIN_TARGET_TEMP_C   (-20.0f)
#define MAX_TARGET_TEMP_C   (80.0f)
#define MIN_INTERVAL_SEC    (5U)
#define MAX_INTERVAL_SEC    (86400U)

/* Коди результатів синхронізації */
typedef enum {
    SYNC_OK = 0,
    SYNC_ERR_INVALID_MAGIC,
    SYNC_ERR_CRC_MISMATCH,
    SYNC_ERR_STALE_VERSION,
    SYNC_ERR_OUT_OF_RANGE,
    SYNC_ERR_STORAGE_FAIL
} sync_status_t;

/* Структура конфігурації (зберігається в NVM) */
typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint32_t version;
    float    target_temperature_c;
    uint32_t telemetry_interval_sec;
    bool     auto_valve_enabled;
    char     device_alias[MAX_DEVICE_NAME_LEN];
    uint32_t crc32;
} device_nvm_config_t;

/* Структура дельти, що приходить від сервера */
typedef struct {
    uint32_t version;
    bool     has_target_temp;
    float    target_temperature_c;
    bool     has_interval;
    uint32_t telemetry_interval_sec;
    bool     has_auto_valve;
    bool     auto_valve_enabled;
    bool     has_device_alias;
    const char *device_alias;
} shadow_delta_t;

/* Фактичний операційний стан для звітування в хмару */
typedef struct {
    uint32_t applied_version;
    float    current_temperature_c;
    float    active_target_temp_c;
    uint32_t active_interval_sec;
    bool     active_valve_state;
    sync_status_t last_sync_status;
} shadow_reported_state_t;

/* Розрахунок CRC32 (поліном IEEE 802.3 0xEDB88320) */
static uint32_t calculate_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; ++j) {
            if (crc & 1U) {
                crc = (crc >> 1) ^ 0xEDB88320U;
            } else {
                crc >>= 1;
            }
        }
    }
    return ~crc;
}

/* Імітація низькорівневого інтерфейсу Flash/FRAM (HAL) */
static uint8_t g_simulated_nvm_storage[sizeof(device_nvm_config_t)];

static bool hal_nvm_read(void *dest, size_t size) {
    if (size != sizeof(device_nvm_config_t)) return false;
    memcpy(dest, g_simulated_nvm_storage, size);
    return true;
}

static bool hal_nvm_write(const void *src, size_t size) {
    if (size != sizeof(device_nvm_config_t)) return false;
    memcpy(g_simulated_nvm_storage, src, size);
    return true;
}

/* Модуль синхронізатора */
typedef struct {
    device_nvm_config_t active_config;
    bool is_initialized;
} state_synchronizer_t;

static state_synchronizer_t g_sync_mgr;

/* Завантаження та перевірка цілісності конфігурації з NVM */
sync_status_t state_sync_init(void) {
    device_nvm_config_t loaded_cfg;
    if (!hal_nvm_read(&loaded_cfg, sizeof(loaded_cfg))) {
        return SYNC_ERR_STORAGE_FAIL;
    }

    if (loaded_cfg.magic != CONFIG_MAGIC) {
        /* Перший старт: ініціалізація заводськими значеннями */
        memset(&g_sync_mgr.active_config, 0, sizeof(device_nvm_config_t));
        g_sync_mgr.active_config.magic = CONFIG_MAGIC;
        g_sync_mgr.active_config.version = 1;
        g_sync_mgr.active_config.target_temperature_c = 22.0f;
        g_sync_mgr.active_config.telemetry_interval_sec = 60;
        g_sync_mgr.active_config.auto_valve_enabled = true;
        strncpy(g_sync_mgr.active_config.device_alias, "Node-Default", MAX_DEVICE_NAME_LEN - 1);

        size_t payload_len = sizeof(device_nvm_config_t) - sizeof(uint32_t);
        g_sync_mgr.active_config.crc32 = calculate_crc32((const uint8_t *)&g_sync_mgr.active_config, payload_len);

        if (!hal_nvm_write(&g_sync_mgr.active_config, sizeof(device_nvm_config_t))) {
            return SYNC_ERR_STORAGE_FAIL;
        }
        g_sync_mgr.is_initialized = true;
        return SYNC_OK;
    }

    /* Перевірка контрольної суми */
    size_t payload_len = sizeof(device_nvm_config_t) - sizeof(uint32_t);
    uint32_t expected_crc = calculate_crc32((const uint8_t *)&loaded_cfg, payload_len);
    if (loaded_cfg.crc32 != expected_crc) {
        return SYNC_ERR_CRC_MISMATCH;
    }

    memcpy(&g_sync_mgr.active_config, &loaded_cfg, sizeof(device_nvm_config_t));
    g_sync_mgr.is_initialized = true;
    return SYNC_OK;
}

/* Обробка вхідної дельти конфігурації від сервера */
sync_status_t state_sync_apply_delta(const shadow_delta_t *delta) {
    if (!g_sync_mgr.is_initialized || delta == NULL) {
        return SYNC_ERR_STORAGE_FAIL;
    }

    /* Захист від застарілих або повторних повідомлень */
    if (delta->version <= g_sync_mgr.active_config.version) {
        return SYNC_ERR_STALE_VERSION;
    }

    /* Створення тіньової копії для перевірки меж */
    device_nvm_config_t candidate_cfg = g_sync_mgr.active_config;
    candidate_cfg.version = delta->version;

    if (delta->has_target_temp) {
        if (delta->target_temperature_c < MIN_TARGET_TEMP_C || 
            delta->target_temperature_c > MAX_TARGET_TEMP_C) {
            return SYNC_ERR_OUT_OF_RANGE;
        }
        candidate_cfg.target_temperature_c = delta->target_temperature_c;
    }

    if (delta->has_interval) {
        if (delta->telemetry_interval_sec < MIN_INTERVAL_SEC || 
            delta->telemetry_interval_sec > MAX_INTERVAL_SEC) {
            return SYNC_ERR_OUT_OF_RANGE;
        }
        candidate_cfg.telemetry_interval_sec = delta->telemetry_interval_sec;
    }

    if (delta->has_auto_valve) {
        candidate_cfg.auto_valve_enabled = delta->auto_valve_enabled;
    }

    if (delta->has_device_alias && delta->device_alias != NULL) {
        strncpy(candidate_cfg.device_alias, delta->device_alias, MAX_DEVICE_NAME_LEN - 1);
        candidate_cfg.device_alias[MAX_DEVICE_NAME_LEN - 1] = '\0';
    }

    /* Оновлення CRC та атомарний запис у Flash */
    size_t payload_len = sizeof(device_nvm_config_t) - sizeof(uint32_t);
    candidate_cfg.crc32 = calculate_crc32((const uint8_t *)&candidate_cfg, payload_len);

    if (!hal_nvm_write(&candidate_cfg, sizeof(device_nvm_config_t))) {
        return SYNC_ERR_STORAGE_FAIL;
    }

    /* Зміни успішно зафіксовані */
    g_sync_mgr.active_config = candidate_cfg;
    return SYNC_OK;
}

/* Формування стану Reported для публікації на сервер */
void state_sync_get_reported(float current_sensor_temp, 
                             bool current_valve_pin_state,
                             sync_status_t last_status,
                             shadow_reported_state_t *out_reported) {
    if (out_reported == NULL) return;

    out_reported->applied_version = g_sync_mgr.active_config.version;
    out_reported->current_temperature_c = current_sensor_temp;
    out_reported->active_target_temp_c = g_sync_mgr.active_config.target_temperature_c;
    out_reported->active_interval_sec = g_sync_mgr.active_config.telemetry_interval_sec;
    out_reported->active_valve_state = current_valve_pin_state;
    out_reported->last_sync_status = last_status;
}
