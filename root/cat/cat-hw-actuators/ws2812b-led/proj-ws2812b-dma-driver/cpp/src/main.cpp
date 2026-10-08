#include "ws2812b.hpp"
#include "dma_spi_hardware.hpp"
#include <iostream>

int main() {
    using namespace embedded;

    std::cout << "=== Ініціалізація C++ Драйвера WS2812B (SPI + DMA RAII) ===" << std::endl;

    SpiDmaConfig config{};
    config.spi_peripheral_addr = 0x40013000;
    config.dma_channel = 3;
    config.gpio_pin = 7;
    config.baud_rate_prescaler = 8;

    DmaSpiHardware hw(config);
    if (!hw.init()) {
        std::cerr << "Помилка ініціалізації апаратури SPI/DMA!" << std::endl;
        return 1;
    }

    constexpr std::size_t LedCount = 64;
    Ws2812bDriver<LedCount> strip(hw);

    if (!strip.init()) {
        std::cerr << "Помилка ініціалізації драйвера WS2812B!" << std::endl;
        return 1;
    }

    strip.setBrightness(128);
    std::cout << "Драйвер ініціалізовано. Розмір фреймбуфера у пам'яті: "
              << sizeof(strip) << " байтів." << std::endl;

    std::cout << "\n[1] Запуск ефекту 'Веселка' (Rainbow effect)..." << std::endl;
    for (uint8_t step = 0; step < 5; ++step) {
        if (strip.isReady()) {
            strip.applyRainbow(step * 10);
            if (strip.renderAsync()) {
                std::cout << "  Крок " << static_cast<int>(step)
                          << ": Кадр передано у DMA фоновим режимом." << std::endl;
            }
            hw.handleTransferCompleteIsr();
        }
    }

    std::cout << "\n[2] Запуск ефекту 'Пульсація' (Breathing effect)..." << std::endl;
    Color cyan{0, 255, 255};
    for (uint8_t phase = 0; phase < 5; ++phase) {
        if (strip.isReady()) {
            strip.applyBreathing(cyan, phase * 30);
            if (strip.renderAsync()) {
                std::cout << "  Фаза " << static_cast<int>(phase)
                          << ": Кадр передано у DMA фоновим режимом." << std::endl;
            }
            hw.handleTransferCompleteIsr();
        }
    }

    std::cout << "\n[3] Запуск ефекту 'Біжучий вогонь' (Running Light)..." << std::endl;
    Color red{255, 0, 0};
    for (std::size_t pos = 0; pos < 5; ++pos) {
        if (strip.isReady()) {
            strip.applyRunningLight(red, pos * 10, 5);
            if (strip.renderAsync()) {
                std::cout << "  Позиція " << pos
                          << ": Кадр передано у DMA фоновим режимом." << std::endl;
            }
            hw.handleTransferCompleteIsr();
        }
    }

    std::cout << "\nЗавершення роботи програми. RAII-деструктори автоматично звільняють ресурси периферії." << std::endl;
    return 0;
}
