#pragma once

#include <chrono>
#include <cstdint>

namespace fm {

using Clock    = std::chrono::steady_clock;
using TimePoint = Clock::time_point;
using Millis   = std::chrono::milliseconds;

/* Параметри автомата. На відміну від сішної таблиці з окремою функцією
   ініціалізації, значення за замовчуванням живуть у самому типі, а часові
   пороги мають тип часу — сплутати мілісекунди з секундами компілятор не дасть. */
struct Params {
    // Супутникова навігація
    std::uint8_t gnssMinSats    = 6;
    std::uint8_t gnssMinFixType = 3;   // 3 = 3D Fix, 4/5 = RTK
    float gnssMaxHdop           = 1.5F;
    float gnssMaxVdop           = 2.0F;

    // Розширений фільтр Калмана
    float ekfMaxInnovPos      = 0.3F;
    float ekfMaxInnovVel      = 0.5F;
    float ekfGlitchInnov      = 1.0F;  // понад це виміри суперечать одні одним
    float compassMaxYawErrDeg = 15.0F;

    // Джерело цілевказівок
    Millis guidedTimeout{1000};

    // Заслінка газу
    float throttleDeadband  = 0.12F;
    float throttleSlewPerS  = 0.60F;

    // Детектор посадки
    float  landSpeed        = 0.7F;
    float  landVzEpsilon    = 0.2F;
    float  landThrMin       = 0.18F;   // частка тяги висіння
    float  landAccelVarMax  = 0.35F;
    Millis landContact{1000};
    Millis landConfirm{1500};
    float  landIdleThrottle = 0.05F;

    // Детектор польоту
    float  inAirAltM       = 1.5F;
    float  inAirMotorMin   = 0.25F;
    float  inAirAccelVar   = 0.20F;
    Millis inAirRise{300};
    Millis inAirFall{1000};

    // Втрата зв'язку
    Millis rcLoss{1500};
    Millis gcsLoss{3000};

    // Живлення
    float battLowCellV      = 3.5F;
    float battLowRemaining  = 0.25F;
    float battCritCellV     = 3.3F;
    float battCritRemaining = 0.10F;

    // Геозона й повернення
    float fenceRadiusM = 300.0F;
    float fenceAltM    = 120.0F;
    float rtlAltM      = 30.0F;

    // Гістерезис і перехоплення
    Millis guardStable{2000};
    float  pilotOverrideStick = 0.15F;
    float  missionMaxAltM     = 120.0F;
};

}  // namespace fm
