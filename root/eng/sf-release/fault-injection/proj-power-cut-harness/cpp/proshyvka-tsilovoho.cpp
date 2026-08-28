#include <cstdint>
#include <array>
#include <span>
#include <numeric>

namespace TargetDUT {

struct alignas(4) FlashPageBlock {
    std::uint32_t magic{0xAA55AA55};
    std::uint32_t sequenceId{0};
    std::uint32_t checksum{0};
    std::array<std::uint8_t, 256> payload{};

    [[nodiscard]] std::uint32_t computeChecksum() const noexcept {
        std::uint32_t crc = 0xFFFFFFFF;
        const auto feedByte = [&crc](std::uint8_t byte) noexcept {
            crc ^= byte;
            for (std::uint8_t j = 0; j < 8; ++j) {
                crc = (crc >> 1) ^ (0xEDB88320 & -(crc & 1));
            }
        };

        const auto* seqBytes = reinterpret_cast<const std::uint8_t*>(&sequenceId);
        for (std::size_t i = 0; i < sizeof(sequenceId); ++i) {
            feedByte(seqBytes[i]);
        }
        for (const auto b : payload) {
            feedByte(b);
        }
        return ~crc;
    }
};

class FlashTransactionScope {
public:
    explicit FlashTransactionScope(std::uint32_t triggerPinMask) noexcept
        : pinMask_(triggerPinMask) {
        // Виставляємо тригерний пін у HIGH (вхід у вразливу зону)
        setPin(pinMask_, true);
    }

    ~FlashTransactionScope() noexcept {
        // Скидаємо тригерний пін у LOW (вихід із зони)
        setPin(pinMask_, false);
    }

    FlashTransactionScope(const FlashTransactionScope&) = delete;
    FlashTransactionScope& operator=(const FlashTransactionScope&) = delete;

private:
    std::uint32_t pinMask_;

    static void setPin([[maybe_unused]] std::uint32_t pin, [[maybe_unused]] bool state) noexcept {
        // Прямий запис у регістри порту DUT
    }
};

void performProtectedFlashWrite(std::uint32_t address, std::uint32_t seqId) noexcept {
    FlashPageBlock block;
    block.sequenceId = seqId;
    block.payload.fill(0x5A);
    block.checksum = block.computeChecksum();

    // RAII охоплення зони запису тригерним імпульсом
    {
        FlashTransactionScope triggerScope(1U << 12);
        
        // Симуляція стирання та запису SPI Flash
        // spiFlashEraseSector(address);
        // spiFlashWritePage(address, reinterpret_cast<const std::uint8_t*>(&block), sizeof(block));
    }
}

} // namespace TargetDUT
