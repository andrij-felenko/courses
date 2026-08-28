#include <cstdint>
#include <array>
#include <span>

namespace security::audit {

constexpr uint32_t AuditMagic = 0x41554454; /* 'AUDT' */
constexpr size_t HashSize = 32;

#pragma pack(push, 1)
struct AuditRecordHeader {
    uint32_t magic{AuditMagic};
    uint16_t version{1};
    uint16_t header_size{sizeof(AuditRecordHeader)};
    uint64_t sequence_number{0};
    uint64_t timestamp_nanos{0};
    uint32_t payload_length{0};
    uint32_t key_epoch{0};
    std::array<uint8_t, HashSize> prev_hash{};
    std::array<uint8_t, HashSize> signature{};
    std::array<uint8_t, 16> reserved{};
};
#pragma pack(pop)

static_assert(sizeof(AuditRecordHeader) == 128, "Header size must be exactly 128 bytes");

} // namespace security::audit
