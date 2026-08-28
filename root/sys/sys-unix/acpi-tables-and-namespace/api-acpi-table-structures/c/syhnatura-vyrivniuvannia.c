/* C Definition (Linux Kernel uapi style) */
#include <stdint.h>

#pragma pack(push, 1)

struct rsdp_descriptor_v1 {
    char     signature[8];     /* "RSD PTR " */
    uint8_t  checksum;         /* Сума перших 20 байтів = 0 */
    char     oem_id[6];        /* Ідентифікатор виробника OEM */
    uint8_t  revision;         /* 0 = ACPI 1.0, 2 = ACPI 2.0+ */
    uint32_t rsdt_physical_address; /* 32-бітна адреса RSDT */
};

struct rsdp_descriptor_v2 {
    struct rsdp_descriptor_v1 v1;
    uint32_t length;           /* Загальний розмір структури (36 байтів) */
    uint64_t xsdt_physical_address; /* 64-бітна адреса XSDT */
    uint8_t  extended_checksum;/* Сума всіх 36 байтів = 0 */
    uint8_t  reserved[3];      /* Зарезервовані байти */
};

#pragma pack(pop)
