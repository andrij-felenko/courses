// C++ Idiomatic Definition
#include <cstdint>

#pragma pack(push, 1)

enum class AcpiAddressSpace : std::uint8_t {
    SystemMemory     = 0,
    SystemIO         = 1,
    PciConfig        = 2,
    EmbeddedControl  = 3,
    SmBus            = 4,
    SystemCmos       = 5,
    PciBarTarget     = 6,
    IPMI             = 7,
    GeneralPurposeIo = 8,
    GenericSerialBus = 9
};

struct alignas(1) AcpiGenericAddress {
    AcpiAddressSpace space_id;
    std::uint8_t     bit_width;
    std::uint8_t     bit_offset;
    std::uint8_t     access_width;
    std::uint64_t    address;
};

#pragma pack(pop)
