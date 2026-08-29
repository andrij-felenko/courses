// bsp/accelerometer.hpp — акселерометр як інтерфейс і його втілення ADXL345.
// C ховає будову структури неповним типом, бо іншого способу не має.
// C++ ховає її ключовим словом private, а замість функції-створювача
// віддає std::optional: об'єкт або є й готовий до роботи, або його немає
// зовсім. Стану «дескриптор створено, але мікросхема не відповіла» тут
// не існує, тож і перевіряти його ніде не треба.
#pragma once

#include "hal/i2c_device.hpp"

#include <cmath>
#include <cstdint>
#include <expected>
#include <optional>

namespace bsp {

struct AccelSample {
    float x_g{0.0F};
    float y_g{0.0F};
    float z_g{0.0F};

    // Модуль вектора без складової тяжіння: нерухомий давач у будь-якій
    // орієнтації дає нуль, а хитання підшипника — справжню амплітуду.
    [[nodiscard]] float vibration_g() const noexcept
    {
        const float magnitude = std::sqrt(x_g * x_g + y_g * y_g + z_g * z_g);
        return std::abs(magnitude - 1.0F);
    }
};

enum class AccelRange : std::uint8_t { G2 = 0, G4 = 1, G8 = 2, G16 = 3 };

// Координатор бачить лише цей інтерфейс, тож у тесті на його місце стає
// підробка, що видає наперед задані коливання.
class IAccelerometer {
public:
    virtual ~IAccelerometer() = default;

    [[nodiscard]] virtual std::expected<AccelSample, hal::I2cError> read() = 0;
};

class Adxl345 final : public IAccelerometer {
public:
    // Піднімає мікросхему: звіряє ідентифікатор, ставить діапазон,
    // частоту 100 Гц і вмикає вимірювання. std::nullopt — на цій адресі
    // або нікого немає, або сидить хтось чужий.
    [[nodiscard]] static std::optional<Adxl345> create(hal::I2cDevice device,
                                                       AccelRange range);

    [[nodiscard]] std::expected<AccelSample, hal::I2cError> read() override;

    // Переводить мікросхему в очікування: логер у режимі сну не мусить
    // годувати давач своїми мікроамперами.
    void standby();

private:
    Adxl345(hal::I2cDevice device, AccelRange range) noexcept
        : device_{device}, range_{range} {}

    hal::I2cDevice device_;
    AccelRange     range_;
};

} // namespace bsp
