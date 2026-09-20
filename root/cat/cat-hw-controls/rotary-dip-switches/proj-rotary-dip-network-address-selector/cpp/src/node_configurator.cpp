#include "node_configurator.hpp"

NodeConfigurator::NodeConfigurator(RotaryDipSwitch& sw_high,
                                   RotaryDipSwitch& sw_low,
                                   RotaryDipSwitch& sw_baud)
    : sw_high_(sw_high),
      sw_low_(sw_low),
      sw_baud_(sw_baud) {}

Baudrate NodeConfigurator::parseBaudrate(uint8_t position) {
    switch (position) {
        case 0:
            return Baudrate::Baud125k;
        case 1:
            return Baudrate::Baud250k;
        case 2:
            return Baudrate::Baud500k;
        case 3:
            return Baudrate::Baud1000k;
        default:
            // Fallback за замовчуванням при перевищенні діапазону
            return Baudrate::Baud125k;
    }
}

NodeConfiguration NodeConfigurator::evaluateConfiguration(std::chrono::steady_clock::time_point now) {
    // Оновлюємо стан усіх трьох перемикачів з урахуванням дебаунсингу
    sw_high_.update(now);
    sw_low_.update(now);
    sw_baud_.update(now);

    uint8_t high_nibble = sw_high_.getDecodedValue();
    uint8_t low_nibble  = sw_low_.getDecodedValue();
    uint8_t baud_pos    = sw_baud_.getDecodedValue();

    // Обчислення 8-бітного Node ID (High << 4 | Low)
    uint8_t node_id = static_cast<uint8_t>((high_nibble << 4) | low_nibble);

    // Валідація за стандартом CANopen / Modbus RTU (адреса вузла в межах 1..127)
    bool is_valid = (node_id >= 1 && node_id <= 127);

    Baudrate baudrate = parseBaudrate(baud_pos);

    return NodeConfiguration{node_id, baudrate, is_valid};
}
