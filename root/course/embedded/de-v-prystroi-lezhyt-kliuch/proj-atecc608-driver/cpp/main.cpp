#include <array>
#include <cstdint>
#include <expected>
#include <functional>
#include <span>

namespace security {

enum class AteccError : uint8_t {
    HalError,
    CrcMismatch,
    DeviceError,
    Timeout
};

using Signature = std::array<uint8_t, 64>;
using Digest = std::array<uint8_t, 32>;

struct I2cBus {
    std::function<bool(uint8_t, std::span<const uint8_t>)> write;
    std::function<bool(uint8_t, std::span<uint8_t>)> read;
    std::function<void()> wakePulse;
    std::function<void(uint32_t)> delayMs;
};

class SecureElementSession {
public:
    static constexpr uint8_t I2cAddress = 0x60;
    static constexpr uint8_t CmdWord = 0x03;
    static constexpr uint8_t SleepWord = 0x01;
    static constexpr uint8_t OpSign = 0x41;
    static constexpr uint8_t SignModeExternal = 0x80;

    explicit SecureElementSession(I2cBus bus) : bus_(std::move(bus)) {}

    ~SecureElementSession() noexcept {
        if (isAwake_) {
            const std::array<uint8_t, 1> sleepCmd{SleepWord};
            bus_.write(I2cAddress, sleepCmd);
        }
    }

    SecureElementSession(const SecureElementSession&) = delete;
    SecureElementSession& operator=(const SecureElementSession&) = delete;
    SecureElementSession(SecureElementSession&&) noexcept = default;
    SecureElementSession& operator=(SecureElementSession&&) noexcept = default;

    [[nodiscard]] std::expected<void, AteccError> wake() noexcept {
        bus_.wakePulse();
        bus_.delayMs(2);

        std::array<uint8_t, 4> resp{};
        if (!bus_.read(I2cAddress, resp)) {
            return std::unexpected(AteccError::HalError);
        }
        if (resp[0] != 0x04 || resp[1] != 0x11) {
            return std::unexpected(AteccError::DeviceError);
        }
        isAwake_ = true;
        return {};
    }

    [[nodiscard]] std::expected<Signature, AteccError> signDigest(
        uint8_t slotId, const Digest& digest) noexcept {
        
        if (!isAwake_) {
            if (auto res = wake(); !res) return std::unexpected(res.error());
        }

        std::array<uint8_t, 40> txBuf{};
        constexpr uint8_t count = 39;

        txBuf[0] = CmdWord;
        txBuf[1] = count;
        txBuf[2] = OpSign;
        txBuf[3] = SignModeExternal;
        txBuf[4] = static_cast<uint8_t>(slotId & 0x0F);
        txBuf[5] = 0x00;
        std::copy(digest.begin(), digest.end(), txBuf.begin() + 6);

        const uint16_t crc = calculateCrc(std::span<const uint8_t>(txBuf.data() + 1, count - 2));
        txBuf[38] = static_cast<uint8_t>(crc & 0xFF);
        txBuf[39] = static_cast<uint8_t>((crc >> 8) & 0xFF);

        if (!bus_.write(I2cAddress, txBuf)) {
            return std::unexpected(AteccError::HalError);
        }

        bus_.delayMs(115); // Очікування апаратного розрахунку точки кривої

        std::array<uint8_t, 67> rxBuf{};
        if (!bus_.read(I2cAddress, rxBuf)) {
            return std::unexpected(AteccError::HalError);
        }

        if (rxBuf[0] != 67) {
            return std::unexpected(AteccError::DeviceError);
        }

        const uint16_t expectedCrc = static_cast<uint16_t>(rxBuf[65] | (rxBuf[66] << 8));
        const uint16_t actualCrc = calculateCrc(std::span<const uint8_t>(rxBuf.data(), 65));
        if (expectedCrc != actualCrc) {
            return std::unexpected(AteccError::CrcMismatch);
        }

        Signature sig{};
        std::copy_n(rxBuf.begin() + 1, 64, sig.begin());
        return sig;
    }

private:
    I2cBus bus_;
    bool isAwake_{false};

    static constexpr uint16_t calculateCrc(std::span<const uint8_t> data) noexcept {
        uint16_t crc = 0x0000;
        for (uint8_t byte : data) {
            for (uint8_t shift = 0x01; shift > 0x00; shift <<= 1) {
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
