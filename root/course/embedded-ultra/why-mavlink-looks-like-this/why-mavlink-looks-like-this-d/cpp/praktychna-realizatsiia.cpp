#include <cstdint>
#include <array>
#include <span>
#include <cstring>
#include <optional>

namespace mavlink {

constexpr uint8_t STX_V2 = 0xFD;
constexpr uint32_t MSG_ID_ATTITUDE = 30;
constexpr uint8_t CRC_EXTRA_ATTITUDE = 39;

// Структура орієнтації апарата з природним вирівнюванням
struct alignas(4) AttitudePayload {
    uint32_t time_boot_ms{0};
    float roll{0.0f};
    float pitch{0.0f};
    float yaw{0.0f};
    float rollspeed{0.0f};
    float pitchspeed{0.0f};
    float yawspeed{0.0f};
};

class Checksum {
public:
    constexpr Checksum() noexcept = default;

    void accumulate(uint8_t byte) noexcept {
        uint8_t tmp = byte ^ static_cast<uint8_t>(accum_ & 0xFF);
        tmp ^= (tmp << 4);
        accum_ = (accum_ >> 8) ^ (static_cast<uint16_t>(tmp) << 8)
               ^ (static_cast<uint16_t>(tmp) << 3) ^ (static_cast<uint16_t>(tmp) >> 4);
    }

    void accumulate(std::span<const uint8_t> bytes) noexcept {
        for (uint8_t b : bytes) {
            accumulate(b);
        }
    }

    [[nodiscard]] constexpr uint16_t value() const noexcept { return accum_; }

private:
    uint16_t accum_{0xFFFF};
};

class PacketEncoder {
public:
    static size_t pack_attitude(
        uint8_t sysid,
        uint8_t compid,
        uint8_t seq,
        const AttitudePayload& payload,
        std::span<uint8_t> out_buffer
    ) noexcept {
        constexpr uint8_t payload_len = sizeof(AttitudePayload);
        constexpr size_t total_len = 10 + payload_len + 2;

        if (out_buffer.size() < total_len) {
            return 0;
        }

        // Заповнення заголовка кадру MAVLink v2
        out_buffer[0] = STX_V2;
        out_buffer[1] = payload_len;
        out_buffer[2] = 0x00; // Incompat flags
        out_buffer[3] = 0x00; // Compat flags
        out_buffer[4] = seq;
        out_buffer[5] = sysid;
        out_buffer[6] = compid;
        out_buffer[7] = static_cast<uint8_t>(MSG_ID_ATTITUDE & 0xFF);
        out_buffer[8] = static_cast<uint8_t>((MSG_ID_ATTITUDE >> 8) & 0xFF);
        out_buffer[9] = static_cast<uint8_t>((MSG_ID_ATTITUDE >> 16) & 0xFF);

        // Копіювання корисних даних
        std::memcpy(&out_buffer[10], &payload, payload_len);

        // Обчислення CRC-16 над заголовком і даними
        Checksum crc;
        crc.accumulate(out_buffer.subspan(1, 9 + payload_len));
        crc.accumulate(CRC_EXTRA_ATTITUDE);

        out_buffer[10 + payload_len] = static_cast<uint8_t>(crc.value() & 0xFF);
        out_buffer[11 + payload_len] = static_cast<uint8_t>((crc.value() >> 8) & 0xFF);

        return total_len;
    }

    static std::optional<AttitudePayload> unpack_attitude(
        std::span<const uint8_t> payload_bytes
    ) noexcept {
        AttitudePayload result{};
        if (payload_bytes.size() > sizeof(AttitudePayload)) {
            return std::nullopt;
        }
        std::memcpy(&result, payload_bytes.data(), payload_bytes.size());
        return result;
    }
};

} // namespace mavlink
