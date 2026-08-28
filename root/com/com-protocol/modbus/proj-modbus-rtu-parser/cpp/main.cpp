#include <cstdint>
#include <cstddef>
#include <span>
#include <optional>
#include <expected>

enum class ModbusError {
    FrameTooShort,
    AddressMismatch,
    CrcInvalid,
    ExceptionResponse
};

struct ModbusFrame {
    uint8_t slave_addr{0};
    uint8_t function_code{0};
    bool is_exception{false};
    uint8_t exception_code{0};
    std::span<const uint8_t> payload{};
};

class ModbusRtuParser {
public:
    static constexpr uint16_t calculate_crc(std::span<const uint8_t> data) noexcept {
        uint16_t crc = 0xFFFF;
        for (uint8_t byte : data) {
            crc ^= byte;
            for (int i = 0; i < 8; ++i) {
                if (crc & 0x0001) {
                    crc = (crc >> 1) ^ 0xA001;
                } else {
                    crc >>= 1;
                }
            }
        }
        return crc;
    }

    static std::expected<ModbusFrame, ModbusError> parse(
        std::span<const uint8_t> frame_bytes,
        uint8_t my_address = 0) noexcept 
    {
        if (frame_bytes.size() < 4) {
            return std::unexpected(ModbusError::FrameTooShort);
        }

        const size_t payload_and_hdr_len = frame_bytes.size() - 2;
        const uint16_t calculated_crc = calculate_crc(frame_bytes.first(payload_and_hdr_len));
        const uint16_t rx_crc = static_cast<uint16_t>(frame_bytes[frame_bytes.size() - 2]) |
                               (static_cast<uint16_t>(frame_bytes[frame_bytes.size() - 1]) << 8);

        if (calculated_crc != rx_crc) {
            return std::unexpected(ModbusError::CrcInvalid);
        }

        const uint8_t addr = frame_bytes[0];
        if (my_address != 0 && addr != my_address && addr != 0) {
            return std::unexpected(ModbusError::AddressMismatch);
        }

        ModbusFrame frame;
        frame.slave_addr = addr;
        const uint8_t raw_fc = frame_bytes[1];

        if (raw_fc & 0x80) {
            frame.function_code = raw_fc & 0x7F;
            frame.is_exception = true;
            frame.exception_code = (frame_bytes.size() > 4) ? frame_bytes[2] : 0;
            return std::unexpected(ModbusError::ExceptionResponse);
        }

        frame.function_code = raw_fc;
        frame.is_exception = false;
        frame.payload = frame_bytes.subspan(2, payload_and_hdr_len - 2);

        return frame;
    }
};
