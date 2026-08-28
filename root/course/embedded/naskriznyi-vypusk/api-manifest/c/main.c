#include <stdint.h>

#define SECURE_BOOT_HEADER_SIZE 128
#define SECURE_BOOT_MAGIC_VALUE 0x53424F54

typedef struct {
    uint32_t magic;
    uint32_t version_packed;
    uint32_t security_counter;
    uint32_t hw_mask;
    uint32_t payload_size;
    uint8_t  payload_digest[32];
    uint8_t  signature[64];
    uint8_t  reserved[12];
} __attribute__((packed, aligned(4))) SecureBootHeader;

_Static_assert(sizeof(SecureBootHeader) == SECURE_BOOT_HEADER_SIZE, "Header size must be 128 bytes");
