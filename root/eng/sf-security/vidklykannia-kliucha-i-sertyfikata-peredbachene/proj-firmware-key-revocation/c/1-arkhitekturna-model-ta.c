#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define OEM_KEY_SLOTS           4
#define SHA256_DIGEST_SIZE      32
#define SIGNATURE_SIZE          64
#define FW_MAGIC                0x53454355  /* "SECU" */

/* Заголовок образу прошивки */
typedef struct {
    uint32_t magic;
    uint32_t fw_version;
    uint32_t key_slot_index;
    uint32_t payload_length;
    uint8_t  public_key[64];       /* Відкритий ключ ECDSA P-256 (X, Y) */
    uint8_t  signature[SIGNATURE_SIZE]; /* Підпис заголовка та корисного навантаження */
    uint8_t  payload_sha256[SHA256_DIGEST_SIZE];
} __attribute__((packed)) FirmwareHeader;

/* Апаратний стан підсистеми eFuse мікроконтролера */
typedef struct {
    uint8_t  root_key_hashes[OEM_KEY_SLOTS][SHA256_DIGEST_SIZE];
    uint32_t revoked_keys_mask;     /* Біт i = 1: Слот i анульовано назавжди */
    uint32_t monotonic_version;     /* Мінімально допустима версія прошивки */
    bool     security_locked;       /* Блокування зміни заводських гешів */
} HardwareEfuseBank;

/* Результати валідації безпечного завантаження */
typedef enum {
    BOOT_OK = 0,
    BOOT_ERR_INVALID_MAGIC,
    BOOT_ERR_KEY_SLOT_OUT_OF_BOUNDS,
    BOOT_ERR_KEY_REVOKED,
    BOOT_ERR_KEY_HASH_MISMATCH,
    BOOT_ERR_VERSION_ROLLBACK,
    BOOT_ERR_PAYLOAD_CORRUPTED,
    BOOT_ERR_SIGNATURE_INVALID,
    BOOT_ERR_EFUSE_BURN_FAILED
} BootResult;
