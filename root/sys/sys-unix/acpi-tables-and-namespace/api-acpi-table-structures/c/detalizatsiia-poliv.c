/* C Definition */
#include <stdint.h>

#pragma pack(push, 1)

struct acpi_table_header {
    char     signature[4];     /* Наприклад "FACP", "APIC", "DSDT" */
    uint32_t length;           /* Довжина всієї таблиці включно із заголовком */
    uint8_t  revision;         /* Версія специфікації цієї таблиці */
    uint8_t  checksum;         /* Сума всіх байтів таблиці = 0 */
    char     oem_id[6];        /* OEM ID */
    char     oem_table_id[8];  /* Table ID виробника */
    uint32_t oem_revision;     /* Версія таблиці OEM */
    char     asl_compiler_id[4]; /* Сигнатура компілятора iASL */
    uint32_t asl_compiler_revision; /* Версія компілятора */
};

#pragma pack(pop)
