#include "dip_configurator.hpp"

DipConfigurator::DipConfigurator(const std::array<uint8_t, NUM_PINS>& pin_map)
    : pins_(pin_map) {}

void DipConfigurator::init() {
    // В реальній прошивці (ESP-IDF / STM32 HAL / Arduino):
    // Налаштовуємо піни в режим INPUT з увімкненим pull-up резистором (INPUT_PULLUP)
    for (uint8_t pin : pins_) {
        // gpio_set_direction(static_cast<gpio_num_t>(pin), GPIO_MODE_INPUT);
        // gpio_set_pull_mode(static_cast<gpio_num_t>(pin), GPIO_PULLUP_ONLY);
        (void)pin;
    }
}

bool DipConfigurator::readPinState(uint8_t pin) const {
    // Читання стану фізичного піна.
    // При підтяжці PULLUP:
    // Перемикач замкнений на GND (ON) -> вивід читає 0 (LOW)
    // Перемикач відкритий (OFF) -> вивід завдяки підтяжці читає 1 (HIGH)
    (void)pin;
    return false; // Симуляція замкненого стану для прикладу
}

uint8_t DipConfigurator::readRawMask() const {
    uint8_t mask = 0;
    for (size_t i = 0; i < NUM_PINS; ++i) {
        // Оскільки DIP-перемикач замикає пін на GND,
        // інвертуємо рівень піна, щоб замкнений перемикач давав біт = 1
        bool is_closed = !readPinState(pins_[i]);
        if (is_closed) {
            mask |= static_cast<uint8_t>(1U << i);
        }
    }
    return mask;
}

bool DipConfigurator::validateConfig(uint8_t raw_mask) const {
    // Заборонені або зарезервовані комбінацій перемикачів:
    // 0b1111 (15) - зарезервовано для заводського самотестування
    // 0b1010 (10) - некоректна апаратна комбінація (конфлікт адрес)
    if (raw_mask == 0b1111 || raw_mask == 0b1010) {
        return false;
    }
    return true;
}

ConfigResult DipConfigurator::readAndValidate() const {
    uint8_t raw = readRawMask();
    ConfigResult result;
    result.raw_mask = raw;

    if (!validateConfig(raw)) {
        // Автоматичний фолбек на безпечний дефолтний профіль
        result.is_valid = false;
        result.device_id = 0x01;
        result.baud_rate = BaudRate::Baud115200;
        result.debug_mode = false;
        return result;
    }

    result.is_valid = true;

    // Маскування та виділення полів з маски:
    // Біти 0..1: ID пристрою (0..3)
    result.device_id = raw & 0x03;

    // Біт 2: Вибір швидкості (0 = 115200 bps, 1 = 1000000 bps)
    if ((raw & (1U << 2)) != 0) {
        result.baud_rate = BaudRate::Baud1000000;
    } else {
        result.baud_rate = BaudRate::Baud115200;
    }

    // Біт 3: Режим відлагодження
    result.debug_mode = (raw & (1U << 3)) != 0;

    return result;
}
