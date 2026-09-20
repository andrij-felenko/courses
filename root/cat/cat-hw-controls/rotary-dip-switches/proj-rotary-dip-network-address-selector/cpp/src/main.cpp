#include "rotary_dip_switch.hpp"
#include "node_configurator.hpp"

#include <iostream>
#include <iomanip>
#include <thread>
#include <chrono>

/**
 * @brief Симуляція апаратного GPIO для зчитування ліній перемикача.
 */
class MockGpioReader : public IGpioReader {
public:
    explicit MockGpioReader(uint8_t initial_pins = 0x00) : pin_state_(initial_pins) {}

    void setPins(uint8_t pins) {
        pin_state_ = pins & 0x0F;
    }

    [[nodiscard]] uint8_t readPinGroup() const override {
        return pin_state_;
    }

private:
    uint8_t pin_state_{0};
};

int main() {
    std::cout << "=========================================================\n";
    std::cout << " Драйвер ротаційних DIP-перемикачів та NodeConfigurator \n";
    std::cout << "=========================================================\n\n";

    // Створення симуляторів апаратних шин GPIO
    MockGpioReader gpio_high(0x04); // SW1 = 0x4 (Старший нібл = 4)
    MockGpioReader gpio_low(0x02);  // SW2 = 0x2 (Молодший нібл = 2 в коді Ґрея: 0x2 -> 0x3)
    MockGpioReader gpio_baud(0x01); // SW3 = 0x1 (Позиція 1 -> 250 kbps)

    // Ініціалізація перемикачів із різними типами кодування
    RotaryDipSwitch sw_high(gpio_high, EncodingType::DirectBinary);
    RotaryDipSwitch sw_low(gpio_low, EncodingType::GrayCode);
    RotaryDipSwitch sw_baud(gpio_baud, EncodingType::DirectBinary);

    NodeConfigurator configurator(sw_high, sw_low, sw_baud);

    auto start_time = std::chrono::steady_clock::now();

    // Первинне зчитування конфігурації при подачі живлення
    NodeConfiguration config = configurator.evaluateConfiguration(start_time);

    std::cout << "[Ініціалізація при подачі живлення]\n";
    std::cout << "  High Nibble (Direct Binary) : 0x" << std::hex << static_cast<int>(sw_high.getDecodedValue()) << "\n";
    std::cout << "  Low Nibble  (Gray Code)     : 0x" << std::hex << static_cast<int>(sw_low.getDecodedValue()) << "\n";
    std::cout << "  Сформований Node ID         : 0x" << std::hex << std::uppercase
              << static_cast<int>(config.node_id) << " (" << std::dec << static_cast<int>(config.node_id) << ")\n";
    std::cout << "  Швидкість Baudrate          : " << static_cast<uint32_t>(config.baudrate) / 1000 << " kbps\n";
    std::cout << "  Статус конфігурації         : " << (config.is_valid ? "VALID" : "INVALID") << "\n\n";

    // Симуляція зміни положення перемикачів та обробки брязкоту
    std::cout << "[Симуляція повороту перемикача та брязкоту контактів]\n";

    // Зміна старшого розряду на 0x07 із брязкотом
    gpio_high.setPins(0x0F); // Тимчасовий сплеск брязкоту
    configurator.evaluateConfiguration(start_time + std::chrono::milliseconds(2));
    std::cout << "  Час +2 ms (під час брязкоту): Node ID = 0x" << std::hex << static_cast<int>(sw_high.getDecodedValue()) << " (не змінився)\n";

    gpio_high.setPins(0x07); // Встановлення стабільного нового стану 0x07
    // Зачекаємо закінчення часу дебаунсингу (15 ms)
    auto future_time = start_time + std::chrono::milliseconds(15);
    config = configurator.evaluateConfiguration(future_time);

    std::cout << "  Час +15 ms (після стабілізації):\n";
    std::cout << "    Новий High Nibble : 0x" << std::hex << static_cast<int>(sw_high.getDecodedValue()) << "\n";
    std::cout << "    Оновлений Node ID : 0x" << std::hex << std::uppercase
              << static_cast<int>(config.node_id) << " (" << std::dec << static_cast<int>(config.node_id) << ")\n";
    std::cout << "    Статус адреси     : " << (config.is_valid ? "VALID" : "INVALID") << "\n\n";

    std::cout << "=========================================================\n";
    std::cout << " Симуляція успішно завершена.\n";
    std::cout << "=========================================================\n";

    return 0;
}
