#ifndef EMERGENCY_FW_HEADER_H
#define EMERGENCY_FW_HEADER_H

#include <stdint.h>
#include <stdbool.h>

#define EMERGENCY_HEADER_MAGIC      0x454D4759U /* ASCII 'EMGY' (Emergency) */
#define EMERGENCY_HEADER_VERSION    1U
#define EMERGENCY_SIG_SIZE_BYTES    64U         /* ECDSA NIST P-256 (r, s) або Ed25519 */
#define EMERGENCY_SHA256_SIZE_BYTES 32U
#define EMERGENCY_HEADER_SIZE_BYTES 256U

/* Прапорці поведінки екстреного образу */
#define EMERGENCY_FLAG_CRITICAL_CVSS  (1U << 0) /* Критична вразливість безпеки (CVSS >= 9.0) */
#define EMERGENCY_FLAG_FORCE_APPLY    (1U << 1) /* Застосувати негайно без очікування простою */
#define EMERGENCY_FLAG_BURN_ROLLBACK  (1U << 2) /* Вимагає обов'язкового спалювання eFuse OTP */
#define EMERGENCY_FLAG_CANARY_TESTED  (1U << 3) /* Пройдено верифікацію на канарковій підгрупі */
#define EMERGENCY_FLAG_DUAL_CORE_SYNC (1U << 4) /* Містить образ для вторинного мережевого ядра */

#pragma pack(push, 1)
typedef struct {
    uint32_t magic;                   /* Магічне число: 'EMGY' (0x454D4759) */
    uint16_t header_version;          /* Версія формату заголовка (поточна = 1) */
    uint16_t header_size;             /* Загальний розмір заголовка (256 байтів) */
    
    /* Семантичні координати версії */
    uint8_t  ver_major;               /* Мажорна версія */
    uint8_t  ver_minor;               /* Мінорна версія */
    uint16_t ver_patch;               /* Патч-номер (збільшується для hotfix) */
    uint8_t  build_type;              /* 0 = Production Hotfix, 1 = Canary Trial */
    uint32_t commit_hash_prefix;      /* Перші 4 байти хешу коміту Git */
    
    /* Апаратна сумісність та адресація */
    uint32_t target_hw_id;            /* Унікальний ідентифікатор платформи (Platform ID) */
    uint16_t min_hw_rev;              /* Мінімальна сумісна ревізія заліза */
    uint16_t max_hw_rev;              /* Максимальна сумісна ревізія заліза */
    uint16_t target_core_id;          /* 0 = Cortex-M7 (Main), 1 = Cortex-M4 (Radio) */
    
    /* Безпека та захист від відкату */
    uint32_t security_counter;        /* Монотонний лічильник безпеки для eFuse */
    uint32_t flags;                   /* Бітова маска прапорців EMERGENCY_FLAG_* */
    
    /* Параметри корисного навантаження */
    uint32_t payload_offset;          /* Зміщення тіла прошивки від початку файлу */
    uint32_t payload_size;            /* Розмір тіла прошивки в байтах */
    uint32_t payload_entry_point;     /* Адреса точки входу Reset_Handler у Flash */
    uint32_t payload_crc32;           /* Апаратна контрольна сума IEEE 802.3 */
    
    /* Криптографічний контроль цілісності */
    uint8_t  payload_sha256[EMERGENCY_SHA256_SIZE_BYTES]; /* SHA-256 хеш тіла */
    uint8_t  header_signature[EMERGENCY_SIG_SIZE_BYTES];  /* Підпис полів заголовка */
    
    uint8_t  reserved[74];            /* Резерв для майбутніх розширень / вирівнювання */
} emergency_fw_header_t;
#pragma pack(pop)

/* Перевірка розміру структури на етапі компіляції */
_Static_assert(sizeof(emergency_fw_header_t) == EMERGENCY_HEADER_SIZE_BYTES,
               "emergency_fw_header_t must strictly be 256 bytes");

/* Числові коди помилок валідації екстреного заголовка */
typedef enum {
    EMERGENCY_VAL_OK                       = 0,
    EMERGENCY_VAL_ERR_BAD_MAGIC            = -1,
    EMERGENCY_VAL_ERR_UNSUPPORTED_VERSION  = -2,
    EMERGENCY_VAL_ERR_HW_MISMATCH          = -3,
    EMERGENCY_VAL_ERR_CORE_MISMATCH        = -4,
    EMERGENCY_VAL_ERR_ROLLBACK_BLOCKED     = -5,
    EMERGENCY_VAL_ERR_PAYLOAD_BOUNDS       = -6,
    EMERGENCY_VAL_ERR_CRC_MISMATCH         = -7,
    EMERGENCY_VAL_ERR_HASH_MISMATCH        = -8,
    EMERGENCY_VAL_ERR_SIGNATURE_INVALID    = -9,
    EMERGENCY_VAL_ERR_FLASH_WRITE_FAILURE  = -10
} emergency_validation_status_t;

#endif /* EMERGENCY_FW_HEADER_H */
