#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define ML_MODEL_MAGIC              0x4D4C5550U /* 'MLUP' */
#define ML_HEADER_VERSION           1U
#define ML_FLASH_SECTOR_SIZE        4096U
#define ML_MODEL_MAX_SIZE           (512U * 1024U)
#define ML_METADATA_MAGIC           0x4D455441U /* 'META' */
#define ML_MAX_TRIAL_BOOTS          3U

typedef enum {
    ML_SLOT_A = 0,
    ML_SLOT_B = 1,
    ML_SLOT_INVALID = 0xFF
} ml_slot_id_t;

typedef enum {
    ML_STATE_EMPTY = 0,
    ML_STATE_TRIAL = 1,
    ML_STATE_CONFIRMED = 2,
    ML_STATE_FAILED = 3
} ml_slot_state_t;

typedef enum {
    ML_OTA_OK = 0,
    ML_OTA_ERR_INVALID_MAGIC,
    ML_OTA_ERR_INCOMPATIBLE,
    ML_OTA_ERR_ARENA_OVERFLOW,
    ML_OTA_ERR_HASH_MISMATCH,
    ML_OTA_ERR_FLASH_IO,
    ML_OTA_ERR_OFFSET_GAP,
    ML_OTA_ERR_STATE
} ml_ota_status_t;

#pragma pack(push, 1)
typedef struct {
    uint32_t magic;
    uint16_t header_version;
    uint16_t model_version_major;
    uint16_t model_version_minor;
    uint16_t model_version_patch;
    uint32_t payload_size;
    uint32_t required_arena_size;
    uint32_t input_shape_hash;
    uint32_t output_shape_hash;
    uint16_t target_schema_version;
    uint16_t flags;
    uint8_t  sha256[32];
    uint8_t  signature[64];
} ml_model_header_t;

typedef struct {
    uint32_t meta_magic;
    uint32_t sequence_id;
    uint8_t  active_slot;
    uint8_t  slot_state[2];
    uint8_t  trial_boots_remaining;
    uint32_t crc32;
} ml_nv_metadata_t;
#pragma pack(pop)

/* Інтерфейс апаратного драйвера Flash-пам'яті */
typedef struct {
    bool (*read)(uint32_t addr, uint8_t *dst, uint32_t len);
    bool (*write)(uint32_t addr, const uint8_t *src, uint32_t len);
    bool (*erase_sector)(uint32_t sector_addr);
} ml_flash_driver_t;

/* Контекст стадійного сеансу OTA-оновлення */
typedef struct {
    const ml_flash_driver_t *flash;
    uint32_t nv_meta_addr;
    uint32_t slot_addrs[2];
    uint32_t max_sram_arena;
    
    ml_nv_metadata_t meta;
    ml_slot_id_t target_slot;
    uint32_t received_bytes;
    uint32_t total_expected_bytes;
    uint32_t current_sector_erased;
    bool session_active;
} ml_ota_context_t;
