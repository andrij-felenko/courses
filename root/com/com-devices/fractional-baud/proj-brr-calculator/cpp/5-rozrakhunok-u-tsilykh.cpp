/* Цілочисельний розрахунок USART_BRR на етапі компіляції */
[[nodiscard]] constexpr uint16_t calc_stm32_brr_int(
    uint32_t f_ck, uint32_t baud, bool over8 = false) noexcept
{
    if (baud == 0) return 0;
    if (!over8) {
        return static_cast<uint16_t>(((2 * f_ck) + baud) / (2 * baud));
    }
    const uint32_t div = ((4 * f_ck) + baud) / (2 * baud);
    const uint32_t mantissa = div / 16;
    const uint32_t fraction = div % 16;
    return static_cast<uint16_t>((mantissa << 4) | ((fraction >> 1) & 0x07));
}
