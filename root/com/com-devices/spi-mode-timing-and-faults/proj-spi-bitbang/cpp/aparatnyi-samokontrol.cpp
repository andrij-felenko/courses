#include <array>
#include <cstdint>
#include <iostream>

template <SpiGpioPort Gpio>
bool run_spi_loopback_suite(Gpio& gpio) {
    constexpr std::array<uint8_t, 8> test_vectors{
        0x00, 0xFF, 0xAA, 0x55, 0xA5, 0x5A, 0x12, 0x89
    };

    const std::array<SpiMode, 4> all_modes{
        SpiMode::Mode0, SpiMode::Mode1, SpiMode::Mode2, SpiMode::Mode3
    };

    for (auto mode : all_modes) {
        SoftwareSpiMaster<Gpio> master(gpio, mode, 1000);

        for (uint8_t tx_val : test_vectors) {
            std::array<uint8_t, 1> tx_buf{tx_val};
            std::array<uint8_t, 1> rx_buf{0};

            master.transfer(tx_buf, rx_buf);

            if (rx_buf[0] != tx_val) {
                return false; // Помилка петльового тесту
            }
        }
    }
    return true;
}
