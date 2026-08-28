#pragma once
#include <cstdint>
#include <cmath>
#include <span>
#include <expected>
#include <concepts>

namespace drivers {

// Типізований перелік можливих помилок драйвера
enum class BaroError : int8_t {
    CommunicationFailure = -1,
    InvalidChipId        = -2,
    DataNotReady         = -3,
    InvalidParameter     = -4
};

// Заводські калібрувальні коефіцієнти з плаваючою комою
struct BaroCalibCoeffs {
    double t1{}, t2{}, t3{};
    double p1{}, p2{}, p3{}, p4{}, p5{}, p6{}, p7{}, p8{}, p9{}, p10{}, p11{};
};

// Результат одного повного вимірювання
struct BaroSample {
    double pressure_pa;
    double temperature_c;
    double altitude_m;
};

} // namespace drivers
