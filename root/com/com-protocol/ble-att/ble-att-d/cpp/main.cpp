// att_pdu.hpp
#include <cstdint>
#include <cstddef>
#include <span >
#include <vector>
#include <expected>

namespace ble::att {

enum class Opcode : uint8_t {
    ErrorRsp = 0x01,
    WriteReq = 0x12,
    WriteRsp = 0x13
};

enum class ParseError {
    BufferTooSmall,
    InvalidOpcode,
    MalformedPacket
};

// Безпечне пакування Write Request із поверненням готового вектора байтів
inline std::vector<uint8_t> build_write_request(uint16_t handle, std::span<const uint8_t> payload) {
    std::vector<uint8_t> packet;
    packet.reserve(3 + payload.size());

    packet.push_back(static_cast<uint8_t>(Opcode::WriteReq));
    packet.push_back(static_cast<uint8_t>(handle & 0xFF));
    packet.push_back(static_cast<uint8_t>((handle >> 8) & 0xFF));
    packet.insert(packet.end(), payload.begin(), payload.end());

    return packet;
}

// Валідація та десеріалізація вхідного буфера з використанням std::expected (C++23/C++20)
inline std::expected<void, uint8_t> parse_write_response(std::span<const uint8_t> packet) {
    if (packet.empty()) {
        return std::unexpected(0xFF); // Внутрішня помилка: порожній пакет
    }

    const uint8_t opcode = packet[0];
    if (opcode == static_cast<uint8_t>(Opcode::WriteRsp)) {
        return {}; // Успіх
    }

    if (opcode == static_cast<uint8_t>(Opcode::ErrorRsp)) {
        if (packet.size() >= 5) {
            return std::unexpected(packet[4]); // Повертаємо витягнутий ErrorCode
        }
        return std::unexpected(0xFE); // Пошкоджений пакет помилки
    }

    return std::unexpected(0xFD); // Неочікуваний код операції
}

} // namespace ble::att
