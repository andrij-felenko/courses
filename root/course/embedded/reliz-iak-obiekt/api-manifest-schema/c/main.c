#include <stdint.h>
#include <stdbool.h>

#define FW_HEADER_MAGIC 0x46574D46U /* "FWMF" */
#define FW_HEADER_VERSION 1U

#pragma pack(push, 1)
typedef struct {
    uint32_t magic_word;        /* 0x00: Магічне число "FWMF" */
    uint32_t header_version;     /* 0x04: Версія формату структури */
    uint32_t target_hw_id;      /* 0x08: Ідентифікатор сімейства плати */
    uint8_t  hw_rev_min;        /* 0x0C: Мінімальна сумісна ревізія заліза */
    uint8_t  hw_rev_max;        /* 0x0D: Максимальна сумісна ревізія заліза */
    uint16_t flags;             /* 0x0E: Прапорці пакування / шифрування */
    uint8_t  ver_major;         /* 0x10: SemVer Major */
    uint8_t  ver_minor;         /* 0x11: SemVer Minor */
    uint8_t  ver_patch;         /* 0x12: SemVer Patch */
    uint8_t  ver_pre_flags;     /* 0x13: Статус випуску (0 - release) */
    uint32_t security_version;  /* 0x14: Монотонний лічильник anti-rollback */
    uint32_t payload_size;      /* 0x18: Розмір бінарного коду в байтах */
    uint32_t load_address;      /* 0x1C: Цільова адреса у Flash пам'яті */
    uint8_t  payload_sha256[32];/* 0x20: SHA-256 дайджест тіла програми */
    uint8_t  signature[64];     /* 0x40: Ed25519 підпис полів 0x00..0x3F */
} firmware_header_t;
#pragma pack(pop)

_Static_assert(sizeof(firmware_header_t) == 128, "Розмір firmware_header_t повинен дорівнювати рівно 128 байтам");
