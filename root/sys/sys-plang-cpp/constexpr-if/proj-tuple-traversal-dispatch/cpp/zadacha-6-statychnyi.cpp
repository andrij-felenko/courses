#include <cstdint>
#include <iostream>
#include <type_traits>

enum class BusProtocol { SPI, I2C, UART };

template<BusProtocol Proto>
class HardwareBusDriver {
public:
    void initialize() {
        if constexpr (Proto == BusProtocol::SPI) {
            // Налаштування SPI: ввімкнення тактування, конфігурація CPOL/CPHA
            std::cout << "Ініціалізація апаратного модуля SPI: швидкість 10 МГц\n";
        } else if constexpr (Proto == BusProtocol::I2C) {
            // Налаштування I2C: конфігурація підтягуючих резисторів, стандартний режим 400 кГц
            std::cout << "Ініціалізація апаратного модуля I2C: швидкість 400 кГц\n";
        } else if constexpr (Proto == BusProtocol::UART) {
            // Налаштування UART: швидкість 115200 бод, 8 біт даних, 1 стоп-біт
            std::cout << "Ініціалізація апаратного модуля UART: 115200 бод\n";
        }
    }

    template<typename BufferType>
    void transmit(const BufferType& buffer) {
        if constexpr (Proto == BusProtocol::SPI) {
            // Використання швидкого контролера прямого доступу до пам'яті DMA
            std::cout << "SPI: пряма передача блоку пам'яті через DMA\n";
        } else {
            // Побайтне надсилання через чергу переривань
            std::cout << "Побайтне надсилання в апаратний буфер FIFO\n";
        }
    }
};
