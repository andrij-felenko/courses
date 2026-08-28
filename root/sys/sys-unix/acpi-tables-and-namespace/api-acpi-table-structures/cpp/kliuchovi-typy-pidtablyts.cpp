// C++ Subtable Definition
#include <cstdint>

#pragma pack(push, 1)

struct alignas(1) AcpiMadtSubtableHeader {
    std::uint8_t type;
    std::uint8_t length;
};

struct alignas(1) AcpiMadtLocalApic {
    AcpiMadtSubtableHeader header;
    std::uint8_t  processor_id;
    std::uint8_t  apic_id;
    std::uint32_t flags; // Bit 0: Enabled
};

struct alignas(1) AcpiMadtIoApic {
    AcpiMadtSubtableHeader header;
    std::uint8_t  io_apic_id;
    std::uint8_t  reserved;
    std::uint32_t io_apic_address;
    std::uint32_t global_system_interrupt_base;
};

#pragma pack(pop)
