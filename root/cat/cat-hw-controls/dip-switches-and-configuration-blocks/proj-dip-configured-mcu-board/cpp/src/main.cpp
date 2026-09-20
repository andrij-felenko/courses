#include <iostream>
#include "dip_configurator.hpp"

int main() {
    // Призначення GPIO пінів для 4-позиційного DIP-перемикача:
    // Pin 4 (BIT0), Pin 5 (BIT1), Pin 6 (BIT2), Pin 7 (BIT3)
    constexpr std::array<uint8_t, DipConfigurator::NUM_PINS> dip_pins = {4, 5, 6, 7};

    DipConfigurator configurator(dip_pins);
    configurator.init();

    std::cout << "=== Старт системи: Опитування DIP-перемикачів ===" << std::endl;

    ConfigResult config = configurator.readAndValidate();

    if (!config.is_valid) {
        std::cout << "[ПОПЕРЕДЖЕННЯ] Виявлено недопустиму конфігурацію DIP-перемикачів (0x"
                  << std::hex << static_cast<int>(config.raw_mask) << ")!" << std::endl;
        std::cout << "[INFO] Застосовано безпечний дефолтний профіль." << std::endl;
    } else {
        std::cout << "[ОК] Конфігурацію успішно прочитано та валідовано (Маска: 0x"
                  << std::hex << static_cast<int>(config.raw_mask) << ")." << std::endl;
    }

    std::cout << "--- Налаштування пристрою ---" << std::endl;
    std::cout << "ID пристрою:  0x" << std::hex << static_cast<int>(config.device_id) << std::endl;
    std::cout << "Швидкість:    " << std::dec << static_cast<uint32_t>(config.baud_rate) << " bps" << std::endl;
    std::cout << "Відлагодження: " << (config.debug_mode ? "УВІМКНЕНО" : "ВИМКНЕНО") << std::endl;

    return 0;
}
