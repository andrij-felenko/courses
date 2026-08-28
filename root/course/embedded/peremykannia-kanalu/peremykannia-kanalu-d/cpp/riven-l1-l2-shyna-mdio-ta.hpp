#include <cstdint>

namespace embedded::net {

struct [[nodiscard]] PhyStatus {
    bool linkUp{false};
    bool autoNegComplete{false};
};

class [[nodiscard]] MdioTransceiver {
public:
    static constexpr uint8_t RegBmsr = 0x01;
    static constexpr uint16_t BmsrLinkStatus = 1U << 2;
    static constexpr uint16_t BmsrAnComplete = 1U << 5;

    // Зовнішня функція апаратного рівня (HAL)
    static uint16_t readRegister(uint8_t phyAddr, uint8_t regAddr) noexcept;

    [[nodiscard]] static PhyStatus queryLinkState(uint8_t phyAddr) noexcept {
        // Очищаємо Latch-Low першим читанням
        [[maybe_unused]] auto discard = readRegister(phyAddr, RegBmsr);

        // Зчитуємо дійсний стан другим викликом
        const uint16_t bmsr = readRegister(phyAddr, RegBmsr);

        return PhyStatus{
            .linkUp = (bmsr & BmsrLinkStatus) != 0,
            .autoNegComplete = (bmsr & BmsrAnComplete) != 0
        };
    }
};

} // namespace embedded::net
