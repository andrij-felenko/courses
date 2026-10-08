#ifndef ADC_INTERFACE_HPP
#define ADC_INTERFACE_HPP

#include <cstdint>

/**
 * @brief Абстрактний інтерфейс аналогово-цифрового перетворювача (АЦП).
 * 
 * Забезпечує апаратну абстракцію C++ драйвера GP2Y0A21 від конкретної
 * платформи мікроконтролера (STM32, ESP32, AVR тощо) або тестових мок-об'єктів.
 */
class IAdcChannel {
public:
    virtual ~IAdcChannel() = default;

    /**
     * @brief Зчитує сире цифрове значення з каналу АЦП.
     * @return 10-бітове або 12-бітове значення АЦП (наприклад, 0..1023 для 10-біт).
     */
    virtual uint16_t readRaw() = 0;
};

#endif // ADC_INTERFACE_HPP
