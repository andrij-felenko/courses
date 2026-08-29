// mpu6050.hpp — 6-осьовий IMU MPU-6050 на шині TWI.
//
// Адреси регістрів і масштаби — з паспорта InvenSense MPU-6000/6050
// (Register Map, rev. 4.2).

#pragma once

#include <cstdint>

#include "result.hpp"
#include "twi.hpp"

namespace gimbal {

// Вісь обертання підвісу — X гіроскопа; нахил дає пара Y/Z акселерометра.
struct ImuSample {
    float gyro_x_dps{0.0f};   // сира швидкість, зсув ще не знято
    float accel_y_g{0.0f};
    float accel_z_g{0.0f};
};

class Mpu6050 {
public:
    // AD0 на землі → 0x68, AD0 на живленні → 0x69.
    static constexpr DeviceAddress kAddress{0x68};

    explicit Mpu6050(Twi& bus) noexcept : bus_{bus} {}

    // Перевіряє WHO_AM_I, будить давач, ставить DLPF 44 Гц,
    // діапазони ±500 °/с і ±2 g, частоту вибірок 200 Гц.
    Result<void, TwiError> begin() noexcept;

    // Один пакетний обмін на 14 байтів: три окремі транзакції зшили б кут
    // із показів, знятих у різні миті, і фільтр отримав би неузгоджену пару.
    Result<ImuSample, TwiError> read() noexcept;

private:
    Twi& bus_;
};

}  // namespace gimbal
