/* C Subtable Header Definition */
#include <stdint.h>

#pragma pack(push, 1)

struct acpi_madt_subtable_header {
    uint8_t type;
    uint8_t length;
};

/* Type 0: Processor Local APIC */
struct acpi_madt_local_apic {
    struct acpi_madt_subtable_header header;
    uint8_t  processor_id; /* ACPI Processor ID */
    uint8_t  id;           /* Local APIC ID */
    uint32_t lapic_flags;  /* Bit 0 = Enabled, Bit 1 = Online Capable */
};

/* Type 1: I/O APIC */
struct acpi_madt_io_apic {
    struct acpi_madt_subtable_header header;
    uint8_t  id;           /* I/O APIC ID */
    uint8_t  reserved;
    uint32_t address;      /* Фізична адреса MMIO I/O APIC */
    uint32_t global_irq_base; /* Базовий номер GSI */
};

#pragma pack(pop)
