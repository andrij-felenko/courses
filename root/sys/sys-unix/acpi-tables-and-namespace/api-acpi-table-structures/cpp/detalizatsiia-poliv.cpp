// C++ Idiomatic Definition
#include <cstdint>
#include <array>

#pragma pack(push, 1)

struct alignas(1) AcpiTableHeader {
    std::array<char, 4> signature;     // 4-char signature
    std::uint32_t       length;        // Total table size in bytes
    std::uint8_t        revision;      // Table revision
    std::uint8_t        checksum;      // Entire table checksum (sum % 256 == 0)
    std::array<char, 6> oem_id;        // OEM ID
    std::array<char, 8> oem_table_id;  // OEM Table ID
    std::uint32_t       oem_revision;  // OEM Revision number
    std::array<char, 4> asl_compiler_id; // Compiler ID (e.g. "INTL")
    std::uint32_t       asl_compiler_revision;
};

#pragma pack(pop)
