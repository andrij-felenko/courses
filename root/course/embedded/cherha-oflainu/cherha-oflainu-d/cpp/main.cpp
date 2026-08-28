#include <cstdint>
#include <cstddef>
#include <span>
#include <optional>
#include <algorithm>

namespace storage {

inline constexpr uint16_t RecordMagic = 0xAA55;
inline constexpr size_t MaxPayloadSize = 512;

#pragma pack(push, 1)
struct RecordHeader {
    uint16_t magic{0};
    uint8_t  type{0};
    uint8_t  flags{0};
    uint32_t seq{0};
    uint64_t timestamp_ms{0};
    uint16_t payload_len{0};
    uint16_t reserved{0};
};
#pragma pack(pop)

struct ValidatedRecord {
    RecordHeader header;
    std::span<const std::byte> payload;
    size_t total_bytes{0};
};

[[nodiscard]] constexpr uint32_t calculate_crc32(std::span<const std::byte> data) noexcept {
    uint32_t crc = 0xFFFFFFFFU;
    for (auto b : data) {
        crc ^= static_cast<uint8_t>(b);
        for (int i = 0; i < 8; ++i) {
            crc = (crc >> 1) ^ (0xEDB88320U & (-(static_cast<int32_t>(crc & 1))));
        }
    }
    return ~crc;
}

// Безпечна валідація зрізу пам'яті за допомогою C++20 span
[[nodiscard]] std::optional<ValidatedRecord> validate_record(std::span<const std::byte> buffer) noexcept {
    if (buffer.size() < sizeof(RecordHeader) + sizeof(uint32_t)) {
        return std::nullopt;
    }

    RecordHeader hdr{};
    std::copy_n(buffer.data(), sizeof(RecordHeader), reinterpret_cast<std::byte*>(&hdr));

    if (hdr.magic != RecordMagic || hdr.payload_len > MaxPayloadSize) {
        return std::nullopt;
    }

    const size_t total_len = sizeof(RecordHeader) + hdr.payload_len + sizeof(uint32_t);
    if (buffer.size() < total_len) {
        return std::nullopt;
    }

    uint32_t stored_crc = 0;
    std::copy_n(buffer.data() + total_len - sizeof(uint32_t), sizeof(uint32_t),
                reinterpret_cast<std::byte*>(&stored_crc));

    const auto data_for_crc = buffer.first(total_len - sizeof(uint32_t));
    if (calculate_crc32(data_for_crc) != stored_crc) {
        return std::nullopt; // Збій контрольної суми — неповний запис після brownout
    }

    return ValidatedRecord{
        .header = hdr,
        .payload = buffer.subspan(sizeof(RecordHeader), hdr.payload_len),
        .total_bytes = total_len
    };
}

} // namespace storage
