// Безпечна C++20 серіалізація бінарного кадру без динамічної пам'яті
#include <cstdint>
#include <span>
#include <expected>
#include <cstring>

enum class PacketError {
    BufferOverflow,
    CorruptedData
};

struct alignas(1) SensorPacket {
    std::uint8_t  magic{0xA5};
    std::uint8_t  msg_type{0x01};
    std::uint16_t seq_num{0};
    std::uint32_t timestamp{0};
    std::int16_t  temperature{0};
    std::uint16_t humidity{0};
    std::uint16_t vbat_mv{0};
    std::uint16_t crc16{0};
};

class BinaryPacketBuilder {
public:
    [[nodiscard]] static constexpr std::uint16_t 
    calculateCrc(std::span<const std::uint8_t> data) noexcept {
        std::uint16_t crc = 0xFFFF;
        for (const auto byte : data) {
            crc ^= static_cast<std::uint16_t>(byte) << 8;
            for (int i = 0; i < 8; ++i) {
                if ((crc & 0x8000) != 0) crc = (crc << 1) ^ 0x1021;
                else crc = crc << 1;
            }
        }
        return crc;
    }

    [[nodiscard]] static std::expected<std::size_t, PacketError>
    serialize(std::uint16_t seq, std::uint32_t ts, std::int16_t temp,
              std::uint16_t hum, std::uint16_t vbat,
              std::span<std::uint8_t> output_buffer) noexcept 
    {
        if (output_buffer.size() < sizeof(SensorPacket)) {
            return std::unexpected(PacketError::BufferOverflow);
        }

        SensorPacket pkt{
            .magic = 0xA5,
            .msg_type = 0x01,
            .seq_num = seq,
            .timestamp = ts,
            .temperature = temp,
            .humidity = hum,
            .vbat_mv = vbat,
            .crc16 = 0
        };

        const auto* raw_bytes = reinterpret_cast<const std::uint8_t*>(&pkt);
        constexpr std::size_t payload_len = sizeof(SensorPacket) - sizeof(std::uint16_t);
        pkt.crc16 = calculateCrc({raw_bytes, payload_len});

        std::memcpy(output_buffer.data(), &pkt, sizeof(SensorPacket));
        return sizeof(SensorPacket);
    }
};
