#include <iostream>
#include <array>

int main() {
    HardwareResourceManager mgr;

    // Сценарій 1: Коректна конфігурація з авторозв'язанням колізії DMA
    std::array valid_quad_pins = {
        PinResource{"PA8",  1, 1, 2, 5, 7,    6, ProtocolType::DShot600}, // Motor 1 (DMA2_S5, alt S7)
        PinResource{"PA9",  1, 2, 2, 2, 0xFF, 6, ProtocolType::DShot600}, // Motor 2 (DMA2_S2)
        PinResource{"PA10", 1, 3, 2, 6, 0xFF, 6, ProtocolType::DShot600}, // Motor 3 (DMA2_S6)
        PinResource{"PA11", 1, 4, 2, 4, 0xFF, 6, ProtocolType::DShot600}, // Motor 4 (DMA2_S4)
        PinResource{"PB0",  3, 1, 1, 4, 0xFF, 5, ProtocolType::Ws2812Led},// LED Strip (DMA1_S4)
        PinResource{"PA5",  0, 0, 2, 0, 0xFF, 3, ProtocolType::SpiImu},   // Gyro SPI1_RX (DMA2_S0)
        PinResource{"PA7",  0, 0, 2, 5, 3,    3, ProtocolType::SpiImu}    // Gyro SPI1_TX (DMA2_S5)
    };

    auto res = mgr.validate_and_resolve(valid_quad_pins);
    if (res.has_value()) {
        std::cout << "Тест 1 успішний: конфігурацію валідовано, усунуто колізій DMA: " 
                  << res.value() << '\n';
    } else {
        std::cout << "Тест 1 провалено з помилкою: " << static_cast<int>(res.error()) << '\n';
    }

    // Сценарій 2: Фатальний таймерний конфлікт
    HardwareResourceManager bad_mgr;
    std::array invalid_pins = {
        PinResource{"PB0",  3, 1, 1, 4, 0xFF, 5, ProtocolType::Ws2812Led},
        PinResource{"PB1",  3, 4, 1, 2, 0xFF, 5, ProtocolType::DShot600},
        PinResource{"PA5",  0, 0, 2, 0, 0xFF, 3, ProtocolType::SpiImu}
    };

    auto bad_res = bad_mgr.validate_and_resolve(invalid_pins);
    if (!bad_res.has_value() && bad_res.error() == ValidationError::TimerProtocolConflict) {
        std::cout << "Тест 2 успішний: таймерний конфлікт своєчасно заблоковано валідатором.\n";
    } else {
        std::cout << "Тест 2 провалено: конфлікт не виявлено!\n";
    }

    return 0;
}
