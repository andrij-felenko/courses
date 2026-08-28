#include <stdint.h>
#include <stdbool.h>

#define MANIFEST_MAGIC_VALUE        0x5346574D  /* "SFWM" */
#define MANIFEST_HEADER_VERSION_V2  0x0002
#define MANIFEST_HEADER_SIZE_BYTES  64

#define FLAG_ENCRYPTED              (1U << 0)
#define FLAG_BRIDGE_IMAGE           (1U << 1)
#define FLAG_COMMIT_ROTATION        (1U << 2)
#define FLAG_DUAL_SIGNED            (1U << 3)

typedef enum {
    CRYPTO_SUITE_ED25519_SHA256     = 0x01,
    CRYPTO_SUITE_ECDSA_P256_SHA256  = 0x02,
    CRYPTO_SUITE_RSA3072_PSS_SHA256 = 0x03,
    CRYPTO_SUITE_RSA4096_SHA384     = 0x04
} CryptoSuiteId;

#pragma pack(push, 1)
typedef struct {
    uint32_t magic;
    uint16_t header_version;
    uint16_t flags;
    uint32_t header_size;
    uint32_t payload_size;
    uint32_t security_version;
    uint32_t target_hardware_id;
    uint8_t  crypto_suite;
    uint8_t  key_slot_index;
    uint16_t cert_chain_length;
    uint8_t  payload_hash[32];
    uint32_t header_crc32;
} FirmwareEnvelopeHeader;
#pragma pack(pop)
