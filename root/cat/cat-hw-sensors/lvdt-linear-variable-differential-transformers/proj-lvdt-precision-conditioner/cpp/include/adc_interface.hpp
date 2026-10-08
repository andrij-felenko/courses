#pragma once

#include <cstdint>

namespace lvdt {

/**
 * @brief Абстрактний інтерфейс драйвера АЦП для зчитування напруги кондиціонера LVDT.
 * 
 * Надає шар апаратної абстракції (HAL), що дозволяє відокремити обробку сигналу LVDT
 * від конкретної периферії мікроконтролера (наприклад, STM32 ADC, ESP32 ADC, ADS1115 тощо).
 */
class IAdcDriver {
public:
    virtual ~IAdcDriver() = default;

    /**
     * @brief Ініціалізація апаратного периферійного модуля АЦП.
     * @return true у разі успішної ініціалізації периферії, false при помилці.
     */
    virtual bool init() = 0;

    /**
     * @brief Зчитування поточної вибірки напруги (у Вольтах) з виходу кондиціонера.
     * @param[out] out_voltage_v Посилання для запису виміряної диференціальної напруги в Вольтах.
     * @return true у разі успішного зчитування, false при помилці АЦП.
     */
    virtual bool read_voltage(float& out_voltage_v) = 0;
};

} // namespace lvdt
