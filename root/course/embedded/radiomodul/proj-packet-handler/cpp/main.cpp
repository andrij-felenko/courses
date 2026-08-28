#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>
#include <algorithm>

namespace RadioHardware {

class PacketEngine {
public:
    static constexpr uint8_t  PreambleByte   = 0xAA;
    static constexpr size_t   PreambleLength = 4;
    static constexpr uint16_t SyncWord       = 0xD391;
    static constexpr uint16_t Crc16Poly      = 0x1021;
    static constexpr uint16_t Crc16Init      = 0xFFFF;
    static constexpr uint8_t  LfsrSeed       = 0x7F;
    static constexpr size_t   MaxPayloadSize = 64;
    static constexpr size_t   MaxFrameSize   = PreambleLength + 2 + 1 + MaxPayloadSize + 2;

    struct DecodedPacket {
        std::array<uint8_t, MaxPayloadSize> payload{};
        size_t                              length{0};
    };

    // Статичний розрахунок CRC-16 CCITT
    static constexpr uint16_t updateCrc(uint16_t crc, uint8_t byte) noexcept {
        crc ^= static_cast<uint16_t>(byte) << 8;
        for (size_t i = 0; i < 8; ++i) {
            if ((crc & 0x8000U) != 0U) {
                crc = static_cast<uint16_t>((crc << 1) ^ Crc16Poly);
            } else {
                crc = static_cast<uint16_t>(crc << 1);
            }
        }
        return crc;
    }

    // Побітове скремблювання/дескремблювання LFSR (x^7 + x^4 + 1)
    static void applyWhitening(std::span<uint8_t> buffer) noexcept {
        uint8_t lfsr = LfsrSeed;
        for (auto& byte : buffer) {
            uint8_t whitened = 0;
            for (int bit = 7; bit >= 0; --bit) {
                const uint8_t lfsrOut  = (lfsr >> 6) & 0x01U;
                const uint8_t feedback = ((lfsr >> 6) ^ (lfsr >> 3)) & 0x01U;
                lfsr = static_cast<uint8_t>(((lfsr << 1) | feedback) & 0x7FU);

                const uint8_t inBit = (byte >> bit) & 0x01U;
                whitened |= static_cast<uint8_t>((inBit ^ lfsrOut) << bit);
            }
            byte = whitened;
        }
    }

    // Пакування кадру для передавача
    static std::optional<size_t> encode(
        std::span<const uint8_t> payload,
        std::span<uint8_t>       frameOut) noexcept 
    {
        if (payload.size() > MaxPayloadSize) return std::nullopt;
        const size_t totalNeeded = PreambleLength + 2 + 1 + payload.size() + 2;
        if (frameOut.size() < totalNeeded) return std::nullopt;

        size_t idx = 0;

        // 1. Преамбула
        for (size_t i = 0; i < PreambleLength; ++i) {
            frameOut[idx++] = PreambleByte;
        }

        // 2. Синхрослово
        frameOut[idx++] = static_cast<uint8_t>(SyncWord >> 8);
        frameOut[idx++] = static_cast<uint8_t>(SyncWord & 0xFFU);

        // 3. Довжина
        const auto lenByte = static_cast<uint8_t>(payload.size());
        frameOut[idx++] = lenByte;

        // 4. Копіювання та скремблювання корисних даних
        const size_t payloadStart = idx;
        std::copy(payload.begin(), payload.end(), frameOut.begin() + payloadStart);
        applyWhitening(frameOut.subspan(payloadStart, payload.size()));
        idx += payload.size();

        // 5. CRC-16
        uint16_t crc = Crc16Init;
        crc = updateCrc(crc, lenByte);
        for (size_t i = payloadStart; i < idx; ++i) {
            crc = updateCrc(crc, frameOut[i]);
        }

        frameOut[idx++] = static_cast<uint8_t>(crc >> 8);
        frameOut[idx++] = static_cast<uint8_t>(crc & 0xFFU);

        return idx;
    }

    // Розпакування та перевірка кадру
    static std::optional<DecodedPacket> decode(std::span<const uint8_t> frame) noexcept {
        constexpr size_t minFrameSize = PreambleLength + 2 + 1 + 2;
        if (frame.size() < minFrameSize) return std::nullopt;

        // 1. Пошук синхрослова
        size_t syncPos = 0;
        bool found = false;
        for (size_t i = 0; i + 1 < frame.size(); ++i) {
            const uint16_t sw = (static_cast<uint16_t>(frame[i]) << 8) | frame[i + 1];
            if (sw == SyncWord) {
                syncPos = i + 2;
                found = true;
                break;
            }
        }
        if (!found || syncPos >= frame.size()) return std::nullopt;

        // 2. Довжина payload
        const uint8_t payloadLen = frame[syncPos++];
        if (payloadLen > MaxPayloadSize || (syncPos + payloadLen + 2 > frame.size())) {
            return std::nullopt;
        }

        // 3. Перевірка CRC
        uint16_t calculatedCrc = Crc16Init;
        calculatedCrc = updateCrc(calculatedCrc, payloadLen);
        for (size_t i = 0; i < payloadLen; ++i) {
            calculatedCrc = updateCrc(calculatedCrc, frame[syncPos + i]);
        }

        const uint16_t receivedCrc = (static_cast<uint16_t>(frame[syncPos + payloadLen]) << 8) |
                                     frame[syncPos + payloadLen + 1];

        if (calculatedCrc != receivedCrc) {
            return std::nullopt;
        }

        // 4. Дескремблювання у вихідний результат
        DecodedPacket packet{};
        packet.length = payloadLen;
        std::copy_n(frame.data() + syncPos, payloadLen, packet.payload.begin());
        applyWhitening(std::span<uint8_t>(packet.payload.data(), packet.length));

        return packet;
    }
};

} // namespace RadioHardware
