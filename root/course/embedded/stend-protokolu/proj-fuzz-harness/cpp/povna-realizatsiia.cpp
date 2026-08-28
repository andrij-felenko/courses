#include <cstdint>
#include <cstddef>
#include <cstring>
#include <span>
#include <optional>
#include <array>

namespace protocol_fuzzer {

constexpr uint8_t FRAME_MAGIC_BYTE = 0xAA;
constexpr size_t MAX_PAYLOAD_SIZE = 64;
constexpr size_t HEADER_SIZE = 3;
constexpr size_t CRC_SIZE = 2;

struct DecodedFrame {
    uint8_t msg_type{0};
    uint8_t payload_len{0};
    std::array<uint8_t, MAX_PAYLOAD_SIZE> payload{};
    uint16_t crc16{0};
};

[[nodiscard]] constexpr uint16_t crc16_ccitt(std::span<const uint8_t> data) noexcept {
    uint16_t crc = 0xFFFF;
    for (const uint8_t byte : data) {
        crc ^= static_cast<uint16_t>(byte) << 8;
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

[[nodiscard]] std::optional<DecodedFrame> parse_raw_stream(std::span<const uint8_t> stream) noexcept {
    if (stream.size() < (HEADER_SIZE + CRC_SIZE)) {
        return std::nullopt;
    }

    size_t cursor = 0;
    while (cursor < stream.size()) {
        if (stream[cursor] != FRAME_MAGIC_BYTE) {
            ++cursor;
            continue;
        }

        if (cursor + HEADER_SIZE > stream.size()) {
            break;
        }

        const uint8_t msg_type = stream[cursor + 1];
        const uint8_t payload_len = stream[cursor + 2];

        if (payload_len > MAX_PAYLOAD_SIZE) {
            ++cursor;
            continue;
        }

        const size_t total_frame_len = HEADER_SIZE + payload_len + CRC_SIZE;
        if (cursor + total_frame_len > stream.size()) {
            break;
        }

        const size_t crc_offset = cursor + HEADER_SIZE + payload_len;
        const uint16_t expected_crc = static_cast<uint16_t>(stream[crc_offset]) |
                                      (static_cast<uint16_t>(stream[crc_offset + 1]) << 8);

        const auto crc_data_span = stream.subspan(cursor + 1, (HEADER_SIZE - 1) + payload_len);
        const uint16_t calculated_crc = crc16_ccitt(crc_data_span);

        if (calculated_crc == expected_crc) {
            DecodedFrame frame{};
            frame.msg_type = msg_type;
            frame.payload_len = payload_len;
            if (payload_len > 0) {
                std::memcpy(frame.payload.data(), &stream[cursor + HEADER_SIZE], payload_len);
            }
            frame.crc16 = expected_crc;
            return frame;
        }

        ++cursor;
    }

    return std::nullopt;
}

} // namespace protocol_fuzzer

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    const std::span<const uint8_t> input_stream(data, size);
    auto result = protocol_fuzzer::parse_raw_stream(input_stream);
    (void)result;
    return 0;
}
