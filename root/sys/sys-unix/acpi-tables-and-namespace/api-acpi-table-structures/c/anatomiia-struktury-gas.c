/* C Definition */
#include <stdint.h>

#pragma pack(push, 1)

struct acpi_generic_address {
    uint8_t  space_id;    /* 0=SystemMemory, 1=SystemIO, 2=PCI_Config, 3=EC */
    uint8_t  bit_width;   /* Розмір регістра у бітах (8, 16, 32, 64) */
    uint8_t  bit_offset;  /* Зсув першого біта */
    uint8_t  access_width;/* Розмір доступу: 0=Undefined, 1=Byte, 2=Word, 3=DWord, 4=QWord */
    uint64_t address;     /* 64-бітна фізична адреса або I/O порт */
};

#pragma pack(pop)
