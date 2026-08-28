#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define CAL_MAGIC           0x43414C42U /* 'CALB' в ASCII */
#define CAL_SCHEMA_VERSION  1U
#define CAL_SLOT_COUNT      2U

/* Прапорці стану калібрування */
#define CAL_FLAG_FACTORY_VALID  (1U << 0)
#define CAL_FLAG_USER_TARED      (1U << 1)
#define CAL_FLAG_DEGRADED        (1U << 2)

/* Статуси роботи менеджера */
typedef enum {
    CAL_SUCCESS = 0,
    CAL_ERR_CORRUPTED,
    CAL_ERR_DEGRADED,
    CAL_ERR_STORAGE_IO,
    CAL_ERR_OUT_OF_BOUNDS
} cal_status_t;

/* Бінарне представлення коефіцієнтів (Payload) */
typedef struct __attribute__((packed, aligned(4))) {
    float offset_x;
    float offset_y;
    float offset_z;
    float gain_x;
    float gain_y;
    float gain_z;
    float poly_temp_a;
    float poly_temp_b;
    float poly_temp_c;
    float ref_temp_celsius;
    uint32_t sensor_serial_id;
    uint32_t reserved_zero;
} cal_payload_t;

/* Повний блок збереження у пам'яті (Header + Payload + Footer) */
typedef struct __attribute__((packed, aligned(4))) {
    uint32_t magic;
    uint16_t schema_version;
    uint16_t flags;
    uint32_t sequence_id;
    uint32_t timestamp;
    cal_payload_t data;
    uint32_t crc32;
} cal_block_t;

/* Апаратний інтерфейс носія пам'яті */
typedef struct {
    bool (*read_slot)(uint8_t slot_idx, uint8_t *dst, size_t size);
    bool (*write_slot)(uint8_t slot_idx, const uint8_t *src, size_t size);
    bool (*read_otp)(uint8_t *dst, size_t size);
} cal_storage_driver_t;

/* Стан менеджера в ОЗП */
typedef struct {
    cal_block_t active_block;
    uint8_t active_slot;
    bool is_initialized;
    bool is_degraded;
    const cal_storage_driver_t *driver;
} cal_manager_t;

/* Швидкий табличний / апаратний розрахунок CRC32 (IEEE 802.3) */
static uint32_t cal_crc32_calc(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < length; i++) {
        crc ^= (uint32_t)data[i];
        for (uint8_t b = 0; b < 8; b++) {
            uint32_t mask = -(int32_t)(crc & 1U);
            crc = (crc >> 1) ^ (0xEDB88320U & mask);
        }
    }
    return ~crc;
}

/* Дефолтні заводські константи на випадок катастрофічного Fallback */
static const cal_block_t DEFAULT_FALLBACK_BLOCK = {
    .magic = CAL_MAGIC,
    .schema_version = CAL_SCHEMA_VERSION,
    .flags = CAL_FLAG_DEGRADED,
    .sequence_id = 0,
    .timestamp = 0,
    .data = {
        .offset_x = 0.0f, .offset_y = 0.0f, .offset_z = 0.0f,
        .gain_x = 1.0f,   .gain_y = 1.0f,   .gain_z = 1.0f,
        .poly_temp_a = 0.0f, .poly_temp_b = 0.0f, .poly_temp_c = 0.0f,
        .ref_temp_celsius = 25.0f,
        .sensor_serial_id = 0,
        .reserved_zero = 0
    },
    .crc32 = 0
};

/* Перевірка фізичної адекватності чисел (Sanity Check) */
static bool cal_is_payload_sane(const cal_payload_t *p) {
    if (p->gain_x < 0.5f || p->gain_x > 1.5f) return false;
    if (p->gain_y < 0.5f || p->gain_y > 1.5f) return false;
    if (p->gain_z < 0.5f || p->gain_z > 1.5f) return false;
    if (p->offset_x < -500.0f || p->offset_x > 500.0f) return false;
    if (p->offset_y < -500.0f || p->offset_y > 500.0f) return false;
    if (p->offset_z < -500.0f || p->offset_z > 500.0f) return false;
    return true;
}

/* Перевірка цілісності конкретного слота */
static bool cal_validate_block(const cal_block_t *blk) {
    if (blk->magic != CAL_MAGIC) return false;
    if (blk->schema_version != CAL_SCHEMA_VERSION) return false;
    
    size_t payload_bytes = offsetof(cal_block_t, crc32);
    uint32_t calculated_crc = cal_crc32_calc((const uint8_t*)blk, payload_bytes);
    if (calculated_crc != blk->crc32) return false;
    
    return cal_is_payload_sane(&blk->data);
}

/* Ініціалізація та вибір дійсного слота */
cal_status_t cal_manager_init(cal_manager_t *mgr, const cal_storage_driver_t *drv) {
    if (!mgr || !drv) return CAL_ERR_STORAGE_IO;
    mgr->driver = drv;
    mgr->is_initialized = false;
    mgr->is_degraded = false;

    cal_block_t slot_blocks[CAL_SLOT_COUNT];
    bool slot_valid[CAL_SLOT_COUNT];

    /* Читаємо та валідуємо обидва слоти A/B */
    for (uint8_t i = 0; i < CAL_SLOT_COUNT; i++) {
        slot_valid[i] = false;
        if (mgr->driver->read_slot(i, (uint8_t*)&slot_blocks[i], sizeof(cal_block_t))) {
            slot_valid[i] = cal_validate_block(&slot_blocks[i]);
        }
    }

    if (slot_valid[0] && slot_valid[1]) {
        /* Обидва слоти валідні: беремо найновіший за sequence_id */
        if (slot_blocks[1].sequence_id > slot_blocks[0].sequence_id) {
            mgr->active_slot = 1;
        } else {
            mgr->active_slot = 0;
        }
        memcpy(&mgr->active_block, &slot_blocks[mgr->active_slot], sizeof(cal_block_t));
        mgr->is_initialized = true;
        return CAL_SUCCESS;
    } else if (slot_valid[0]) {
        mgr->active_slot = 0;
        memcpy(&mgr->active_block, &slot_blocks[0], sizeof(cal_block_t));
        mgr->is_initialized = true;
        return CAL_SUCCESS;
    } else if (slot_valid[1]) {
        mgr->active_slot = 1;
        memcpy(&mgr->active_block, &slot_blocks[1], sizeof(cal_block_t));
        mgr->is_initialized = true;
        return CAL_SUCCESS;
    }

    /* Якщо обидва слоти пошкоджені: спроба завантажити незмінні дані з OTP */
    if (mgr->driver->read_otp && mgr->driver->read_otp((uint8_t*)&mgr->active_block, sizeof(cal_block_t))) {
        if (cal_validate_block(&mgr->active_block)) {
            mgr->active_slot = 0;
            mgr->is_initialized = true;
            mgr->is_degraded = true;
            return CAL_ERR_DEGRADED;
        }
    }

    /* Фатальний fallback: перехід на зашиті дефолтні константи */
    memcpy(&mgr->active_block, &DEFAULT_FALLBACK_BLOCK, sizeof(cal_block_t));
    mgr->active_slot = 0;
    mgr->is_initialized = true;
    mgr->is_degraded = true;
    return CAL_ERR_DEGRADED;
}

/* Атомарний запис нового набору коефіцієнтів у протилежний слот */
cal_status_t cal_manager_update(cal_manager_t *mgr, const cal_payload_t *new_payload, uint32_t timestamp) {
    if (!mgr || !mgr->is_initialized) return CAL_ERR_STORAGE_IO;
    if (!cal_is_payload_sane(new_payload)) return CAL_ERR_OUT_OF_BOUNDS;

    uint8_t target_slot = (mgr->active_slot == 0) ? 1 : 0;
    cal_block_t next_block;

    next_block.magic = CAL_MAGIC;
    next_block.schema_version = CAL_SCHEMA_VERSION;
    next_block.flags = CAL_FLAG_FACTORY_VALID | CAL_FLAG_USER_TARED;
    next_block.sequence_id = mgr->active_block.sequence_id + 1;
    next_block.timestamp = timestamp;
    memcpy(&next_block.data, new_payload, sizeof(cal_payload_t));

    /* Розрахунок контрольної суми над Header + Payload */
    size_t payload_bytes = offsetof(cal_block_t, crc32);
    next_block.crc32 = cal_crc32_calc((const uint8_t*)&next_block, payload_bytes);

    /* Запис у неактивний слот */
    if (!mgr->driver->write_slot(target_slot, (const uint8_t*)&next_block, sizeof(cal_block_t))) {
        return CAL_ERR_STORAGE_IO;
    }

    /* Читання назад для верифікації */
    cal_block_t readback;
    if (!mgr->driver->read_slot(target_slot, (uint8_t*)&readback, sizeof(cal_block_t))) {
        return CAL_ERR_STORAGE_IO;
    }
    if (!cal_validate_block(&readback)) {
        return CAL_ERR_CORRUPTED;
    }

    /* Успіх: перемикаємо робочий слот */
    memcpy(&mgr->active_block, &next_block, sizeof(cal_block_t));
    mgr->active_slot = target_slot;
    mgr->is_degraded = false;
    return CAL_SUCCESS;
}

/* Застосування калібрування до сирого вимірювання з урахуванням температури */
float cal_apply_axis(float raw, float offset, float gain, float poly_a, float poly_b, float t_curr, float t_ref) {
    float dt = t_curr - t_ref;
    float temp_drift = (poly_a * dt * dt) + (poly_b * dt);
    float corrected_offset = offset + temp_drift;
    return (raw - corrected_offset) * gain;
}
