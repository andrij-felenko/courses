#ifndef ADC_INTERFACE_HPP
#define ADC_INTERFACE_HPP

#include <cstddef>
#include <cstdint>
#include <span>

/**
 * @brief Абстрактний інтерфейс для багатоканального зчитування АЦП.
 * 
 * Відокремлює високорівневу логіку обробки масиву TCRT5000 від конкретної
 * апаратної платформи (STM32, ESP32, AVR тощо).
 */
class IAdcArrayReader {
public:
    virtual ~IAdcArrayReader() = default;

    /**
     * @brief Зчитує аналогові значення з усіх підключених каналів давачів.
     * 
     * @param buffer Буфер для збереження сирих показань АЦП.
     * @return true Якщо зчитування пройшло успішно, false у разі апаратної помилки.
     */
    virtual bool read_channels(std::span<std::uint16_t> buffer) = 0;

    /**
     * @brief Повертає кількість доступних аналогових каналів.
     */
    virtual std::size_t get_channel_count() const = 0;
};

#endif // ADC_INTERFACE_HPP
