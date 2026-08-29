#ifndef FW_HEADER_H
#define FW_HEADER_H

#include <stdint.h>
#include <stddef.h>

/* Магічне число дескриптора. 0x46574D46 — це ASCII 'F','W','M','F'
   (Firmware Manifest), виписані від старшого байта до молодшого. */
#define FW_HEADER_MAGIC          0x46574D46u

/* Версія формату САМОГО дескриптора. Завантажувач приймає лише ту, яку вміє
   читати: інакше поля означали б не те, що він думає, що вони означають. */
#define FW_HEADER_FORMAT_VERSION 1u

/* Підпис накладається рівно на перші 64 байти — усе, що лежить до поля
   signature. Геш тіла образу сидить усередині цих 64 байтів, тому підпис
   над заголовком автоматично засвідчує й весь бінарник. */
#define FW_HEADER_SIGNED_BYTES   64u
#define FW_HEADER_SIZE           128u

#define FW_SHA256_LEN            32u
#define FW_SIGNATURE_LEN         64u
#define FW_PUBKEY_LEN            32u

/* 128-байтний дескриптор, що фізично передує корисному навантаженню у Flash.
   Порядок байтів — little-endian: і хост-пакувальник, і ARM читають однаково.
   Структура packed, бо це не «зручна структура в пам'яті», а розкладка на
   носії: жодного вирівнювального байта компілятор дописати не має права. */
typedef struct {
    uint32_t magic_word;          /* 0x00 */
    uint32_t format_version;      /* 0x04 */
    uint32_t target_hw_id;        /* 0x08  код виробу, напр. 0x0000A110 */
    uint8_t  hw_rev_min;          /* 0x0C  нижня межа сумісних ревізій плати */
    uint8_t  hw_rev_max;          /* 0x0D  верхня межа */
    uint16_t flags;               /* 0x0E  зарезервовано, має бути 0 */
    uint8_t  ver_major;           /* 0x10 */
    uint8_t  ver_minor;           /* 0x11 */
    uint8_t  ver_patch;           /* 0x12 */
    uint8_t  ver_pre_flags;       /* 0x13  мітка передрелізу (rc/beta) */
    uint32_t security_version;    /* 0x14  монотонний індекс anti-rollback */
    uint32_t payload_size;        /* 0x18  довжина тіла образу в байтах */
    uint32_t load_address;        /* 0x1C  фізична адреса тіла у Flash */
    uint8_t  payload_sha256[FW_SHA256_LEN];  /* 0x20 */
    uint8_t  signature[FW_SIGNATURE_LEN];    /* 0x40  Ed25519 над 0x00..0x3F */
} __attribute__((packed)) fw_header_t;

_Static_assert(sizeof(fw_header_t) == FW_HEADER_SIZE,
               "дескриптор мусить займати рівно 128 байтів");
_Static_assert(offsetof(fw_header_t, payload_sha256) == 32,
               "геш образу стоїть за зсувом 0x20");
_Static_assert(offsetof(fw_header_t, signature) == FW_HEADER_SIGNED_BYTES,
               "підпис починається рівно там, де закінчується підписана частина");

/* Коди відмови. Числа стабільні: їх видно назовні — у діагностичному
   протоколі й у миготінні світлодіода на платі без відлагоджувача. */
typedef enum {
    FW_OK                  = 0,
    FW_ERR_BAD_MAGIC       = 1,
    FW_ERR_HW_INCOMPATIBLE = 2,
    FW_ERR_ROLLBACK        = 3,
    FW_ERR_BAD_GEOMETRY    = 4,
    FW_ERR_NO_ROOT_KEY     = 5,
    FW_ERR_BAD_SIGNATURE   = 6,
    FW_ERR_HASH_MISMATCH   = 7,
    FW_ERR_FLASH_IO        = 8
} fw_verify_t;

#endif /* FW_HEADER_H */
