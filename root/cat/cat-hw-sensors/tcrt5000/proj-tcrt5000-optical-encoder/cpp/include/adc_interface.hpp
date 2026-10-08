#ifndef ADC_INTERFACE_HPP
#define ADC_INTERFACE_HPP

#include <cstddef>
#include <cstdint>
#include <span>

/**
 * @brief Абстрактний C++ інтерфейс для багатоканального зчитування даних АЦП.
 * 
 * Відокремлює обробку сигналів масиву TCRT5000 від апаратного забезпечення
 * конкретного мікроконтролера (STM32, ESP32, AVR тощо).
 */
class IAdcArrayReader {
public:
    virtual ~IAdcArrayReader() = default;

    /**
     * @brief Зчитує аналогові значення з усіх підключених каналів.
     * 
     * @param buffer Буфер span для збереження сирих вибірок АЦП.
     * @return true у разі успішного зчитування, false при апаратному збої.
     */
    virtual bool read_channels(std::span<std::uint16_t> buffer) = 0;

    /**
     * @brief Повертає кількість доступних аналогових каналів АЦП.
     */
    virtual std::size_t get_channel_count() const = 0;
};

#endif // ADC_INTERFACE_HPP
