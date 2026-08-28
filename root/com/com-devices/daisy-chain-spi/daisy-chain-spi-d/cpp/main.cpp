#include <cstdint>
#include <array>
#include <span>

inline constexpr std::size_t ChainLength = 4;

/* Зовнішні апаратні виклики платформового рівня */
extern void hal_gpio_write_cs(bool level);
extern void hal_spi_transmit_receive(const std::uint8_t* tx, std::uint8_t* rx, std::size_t len);

/* Типобезпечна відправка масиву слів у каскад */
void daisyChainUpdate(std::span<const std::uint16_t, ChainLength> values,
                      std::span<std::uint16_t, ChainLength> feedback) noexcept {
    std::array<std::uint8_t, ChainLength * 2> txBuf{};
    std::array<std::uint8_t, ChainLength * 2> rxBuf{};

    // Заповнення буфера передачі у зворотному порядку (FIFO-компенсація)
    for (std::size_t i = 0; i < ChainLength; ++i) {
        std::size_t revIndex = (ChainLength - 1) - i;
        std::uint16_t word = values[revIndex];
        txBuf[i * 2 + 0] = static_cast<std::uint8_t>(word >> 8);
        txBuf[i * 2 + 1] = static_cast<std::uint8_t>(word & 0xFF);
    }

    // Початок транзакції
    hal_gpio_write_cs(false);

    hal_spi_transmit_receive(txBuf.data(), rxBuf.data(), txBuf.size());

    // Фіксація даних у вихідних засувках за фронтом CS
    hal_gpio_write_cs(true);

    // Розпакування зворотних діагностичних даних
    for (std::size_t i = 0; i < ChainLength; ++i) {
        std::size_t revIndex = (ChainLength - 1) - i;
        auto hi = static_cast<std::uint16_t>(rxBuf[i * 2 + 0]);
        auto lo = static_cast<std::uint16_t>(rxBuf[i * 2 + 1]);
        feedback[revIndex] = static_cast<std::uint16_t>((hi << 8) | lo);
    }
}
