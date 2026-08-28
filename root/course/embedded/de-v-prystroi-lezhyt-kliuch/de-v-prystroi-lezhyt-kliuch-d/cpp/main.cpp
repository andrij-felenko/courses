#include <array>
#include <cstdint>
#include <expected>
#include <functional>
#include <span>

namespace security {

enum class SecureElementError : uint8_t {
    CommunicationFailed,
    WakeupTimeout,
    InvalidResponseLength,
    ChecksumMismatch,
    ExecutionFailed
};

using Sha256Digest = std::array<uint8_t, 32>;
using EcdsaSignature = std::array<uint8_t, 64>;

struct HardwareInterface {
    std::function<bool(uint8_t addr, std::span<const uint8_t> data)> write;
    std::function<bool(uint8_t addr, std::span<uint8_t> data)> read;
    std::function<void()> triggerWakePulse;
    std::function<void(uint32_t ms)> delayMs;
};

class SecureElementClient {
public:
    static constexpr uint8_t DefaultAddress = 0x60;
    static constexpr uint8_t CommandWord = 0x03;
    static constexpr uint8_t SleepWord = 0x01;
    static constexpr uint8_t OpSign = 0x41;
    static constexpr uint8_t ModeExternalDigest = 0x80;

    explicit SecureElementClient(HardwareInterface hal) : hal_(std::move(hal)) {}

    ~SecureElementClient() noexcept {
        putToSleep();
    }

    SecureElementClient(const SecureElementClient&) = delete;
    SecureElementClient& operator=(const SecureElementClient&) = delete;
    SecureElementClient(SecureElementClient&&) noexcept = default;
    SecureElementClient& operator=(SecureElementClient&&) noexcept = default;

    [[nodiscard]] std::expected<EcdsaSignature, SecureElementError> sign(
        uint8_t slotId, const Sha256Digest& digest) noexcept {

        if (auto wakeRes = wakeUp(); !wakeRes) {
            return std::unexpected(wakeRes.error());
        }

        std::array<uint8_t, 40> txBuffer{};
        constexpr uint8_t packetCount = 39;

        txBuffer[0] = CommandWord;
        txBuffer[1] = packetCount;
        txBuffer[2] = OpSign;
        txBuffer[3] = ModeExternalDigest;
        txBuffer[4] = static_cast<uint8_t>(slotId & 0x0F);
        txBuffer[5] = 0x00;
        std::copy(digest.begin(), digest.end(), txBuffer.begin() + 6);

        const uint16_t txCrc = calculateCrc(std::span<const uint8_t>(txBuffer.data() + 1, 37));
        txBuffer[38] = static_cast<uint8_t>(txCrc & 0xFF);
        txBuffer[39] = static_cast<uint8_t>((txCrc >> 8) & 0xFF);

        if (!hal_.write(DefaultAddress, txBuffer)) {
            return std::unexpected(SecureElementError::CommunicationFailed);
        }

        hal_.delayMs(110); // Час обчислення точки на еліптичній кривій

        std::array<uint8_t, 67> rxBuffer{};
        if (!hal_.read(DefaultAddress, rxBuffer)) {
            return std::unexpected(SecureElementError::CommunicationFailed);
        }

        if (rxBuffer[0] != 67) {
            return std::unexpected(SecureElementError::InvalidResponseLength);
        }

        const uint16_t expectedCrc = static_cast<uint16_t>(rxBuffer[65] | (rxBuffer[66] << 8));
        if (calculateCrc(std::span<const uint8_t>(rxBuffer.data(), 65)) != expectedCrc) {
            return std::unexpected(SecureElementError::ChecksumMismatch);
        }

        EcdsaSignature signature{};
        std::copy_n(rxBuffer.begin() + 1, 64, signature.begin());

        putToSleep();
        return signature;
    }

private:
    HardwareInterface hal_;

    [[nodiscard]] std::expected<void, SecureElementError> wakeUp() noexcept {
        hal_.triggerWakePulse();
        hal_.delayMs(2);

        std::array<uint8_t, 4> wakeToken{};
        if (!hal_.read(DefaultAddress, wakeToken)) {
            return std::unexpected(SecureElementError::CommunicationFailed);
        }
        if (wakeToken[0] != 0x04 || wakeToken[1] != 0x11) {
            return std::unexpected(SecureElementError::WakeupTimeout);
        }
        return {};
    }

    void putToSleep() noexcept {
        const std::array<uint8_t, 1> sleepPacket{SleepWord};
        hal_.write(DefaultAddress, sleepPacket);
    }

    static constexpr uint16_t calculateCrc(std::span<const uint8_t> data) noexcept {
        uint16_t crc = 0x0000;
        for (uint8_t byte : data) {
            for (uint8_t shift = 0x01; shift > 0; shift <<= 1) {
                uint8_t dataBit = (byte & shift) ? 1 : 0;
                uint8_t crcBit = (crc >> 15) & 0x01;
                crc <<= 1;
                if (dataBit ^ crcBit) {
                    crc ^= 0x8005;
                }
            }
        }
        return crc;
    }
};

} // namespace security
