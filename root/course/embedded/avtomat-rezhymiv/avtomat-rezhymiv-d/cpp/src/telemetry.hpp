#pragma once

#include <cstdint>
#include <optional>

#include "params.hpp"

namespace fm {

class MissionPlan;

/* Географічна точка в цілих одиницях MAVLink (градуси × 1e7). */
struct GeoPoint {
    std::int32_t lat1e7{};
    std::int32_t lon1e7{};
};

struct ImuStatus {
    bool  gyroHealthy{};
    bool  accelHealthy{};
    bool  attitudeValid{};
    float accelZVariance{};
};

struct VerticalStatus {
    bool  baroHealthy{};
    bool  rangefinderHealthy{};
    bool  ekfPosValid{};
    float altitudeRelM{};      // над точкою старту
    float velocityMs{};        // додатна вгору
};

struct HorizontalStatus {
    std::uint8_t fixType{};    // 0 нема, 2 = 2D, 3 = 3D, 4/5 = RTK
    std::uint8_t sats{};
    float hdop{};
    float vdop{};
    bool  ekfPosValid{};
    float innovPosNorm{};      // нормалізована інновація положення
    float innovVelNorm{};      // нормалізована інновація швидкості
    bool  compassHealthy{};
    float compassYawErrorDeg{};
    GeoPoint position{};
    float velNorthMs{};
    float velEastMs{};
};

struct Sticks {
    float throttle{};          // 0..1
    float roll{};              // -1..1
    float pitch{};
    float yaw{};
    bool  disarmCombo{};       // газ униз і рудер ліворуч, витримані
};

/* Канали зв'язку описані мітками часу, а не прапорцями «втрачено»: рішення про
   тайм-аут ухвалює автомат за своїм параметром, а не драйвер приймача. */
struct Links {
    TimePoint lastRcFrame{};
    TimePoint lastGcsHeartbeat{};
    TimePoint lastGuidedSetpoint{};
};

struct Battery {
    float cellVoltage{};
    float remaining{};         // 0..1
};

struct Propulsion {
    bool  armed{};             // силовий каскад справді генерує сигнали
    float motorOutput{};       // 0..1
    float hoverThrottle{0.5F};
};

/* Знімок стану борту на один такт. Заповнюється драйверами ДО виклику автомата
   й далі не міняється: усі охоронці бачать один і той самий вектор стану. */
struct VehicleState {
    TimePoint now{};

    ImuStatus        imu{};
    VerticalStatus   vertical{};
    HorizontalStatus horizontal{};
    Sticks           sticks{};
    Links            links{};
    Battery          battery{};
    Propulsion       propulsion{};

    /* Виділений апаратний тумблер відсічки. Він працює повз автомат, на рівні
       співпроцесора вводу-виводу; сюди приходить лише звістка, що це сталося. */
    bool killSwitch{};

    std::optional<GeoPoint> home{};   // немає значення — точку старту не зафіксовано
    const MissionPlan*      mission{nullptr};

    [[nodiscard]] Millis age(TimePoint stamp) const noexcept
    {
        return std::chrono::duration_cast<Millis>(now - stamp);
    }
};

}  // namespace fm
