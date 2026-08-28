// Ті самі структури ESRT у C++20 з фіксованими типами stdint
#include <cstdint>
#include <array>

struct alignas(8) EfiGuid {
    std::uint32_t data1;
    std::uint16_t data2;
    std::uint16_t data3;
    std::array<std::uint8_t, 8> data4;
};

struct alignas(8) EfiSystemResourceTable {
    std::uint32_t fw_resource_count;
    std::uint32_t fw_resource_count_max;
    std::uint64_t fw_resource_version;
};

struct alignas(8) EfiSystemResourceEntry {
    EfiGuid       fw_class;
    std::uint32_t fw_type;
    std::uint32_t fw_version;
    std::uint32_t lowest_supported_fw_version;
    std::uint32_t capsule_flags;
    std::uint32_t last_attempt_version;
    std::uint32_t last_attempt_status;
};
