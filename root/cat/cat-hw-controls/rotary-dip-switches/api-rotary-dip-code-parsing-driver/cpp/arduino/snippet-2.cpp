// C++ constexpr функція генерації маски 8-бітної кодової шини
constexpr uint8_t generateLutMask(uint8_t rawBus, uint8_t bitCount, uint8_t activeMask) noexcept {
    uint8_t result = 0;
    uint8_t targetBit = 0;
    for (uint8_t i = 0; i < 8; i++) {
        if (activeMask & (1U << i)) {
            if (rawBus & (1U << i)) {
                result |= static_cast<uint8_t>(1U << targetBit);
            }
            targetBit++;
            if (targetBit >= bitCount) break;
        }
    }
    return result;
}
