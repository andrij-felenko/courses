#pragma once

#include <array>
#include <cstdint>
#include <string_view>

namespace fm {

/* Польотні режими за зростанням автономності. Порядок значущий: за ним
   будується деградація, тож перелік не можна переставляти навмання. */
enum class Mode : std::uint8_t {
    Manual = 0,     // Acro: стіки задають кутові швидкості
    Stabilize,      // автогоризонт, тяга напряму зі стіка
    AltHold,        // + вертикальний регулятор положення
    PosHold,        // + горизонтальні регулятори швидкості й координат
    Guided,         // цілевказівки ззовні по MAVLink
    Auto,           // політ за завантаженим планом місії
    Rtl,            // повернення до точки старту
    Land,           // контрольований вертикальний спуск
    EmergencyLand,  // спуск без навігації
    Terminate       // відсічка живлення двигунів
};

/* Замість купки функцій-предикатів (як це роблять у C) — одна таблиця
   властивостей, доступна на етапі компіляції. Додати режим означає дописати
   рядок; забути про нього в одному з десятка switch-ів більше неможливо. */
struct ModeTraits {
    std::string_view name;
    bool needsAttitude;
    bool needsAltitude;
    bool needsPosition;
    bool autoThrottle;
    bool autonomous;   // скасовується рухом стіків
    bool failsafe;     // ставить арбітр аварій, а не оператор
};

inline constexpr std::array<ModeTraits, 10> kModeTraits{{
    //  назва          кути   висота  позиція  автотяга  автономний  аварійний
    { "Manual",        false, false,  false,   false,    false,      false },
    { "Stabilize",     true,  false,  false,   false,    false,      false },
    { "AltHold",       true,  true,   false,   true,     false,      false },
    { "PosHold",       true,  true,   true,    true,     false,      false },
    { "Guided",        true,  true,   true,    true,     true,       false },
    { "Auto",          true,  true,   true,    true,     true,       false },
    { "RTL",           true,  true,   true,    true,     false,      true  },
    { "Land",          true,  true,   false,   true,     false,      true  },
    { "EmergLand",     true,  false,  false,   true,     false,      true  },
    { "Terminate",     false, false,  false,   false,    false,      true  },
}};

[[nodiscard]] constexpr bool valid(Mode mode) noexcept
{
    return static_cast<std::size_t>(mode) < kModeTraits.size();
}

[[nodiscard]] constexpr const ModeTraits& traits(Mode mode) noexcept
{
    return kModeTraits[static_cast<std::size_t>(mode)];
}

[[nodiscard]] constexpr std::string_view name(Mode mode) noexcept
{
    return valid(mode) ? traits(mode).name : std::string_view{"Invalid"};
}

[[nodiscard]] constexpr bool manualThrottle(Mode mode) noexcept
{
    return mode == Mode::Manual || mode == Mode::Stabilize;
}

/* Сходинка вниз ієрархією. */
[[nodiscard]] constexpr Mode degrade(Mode mode) noexcept
{
    switch (mode) {
    case Mode::Auto:
    case Mode::Guided:
    case Mode::Rtl:
    case Mode::PosHold:
        return Mode::AltHold;
    case Mode::AltHold:
    case Mode::Land:
        return Mode::Stabilize;
    case Mode::Stabilize:
        return Mode::Manual;
    default:
        return mode;   // нижче падати нема куди
    }
}

/* Найвищий режим, забезпечений наявними оцінювачами. */
[[nodiscard]] constexpr Mode bestAvailable(bool attitudeOk, bool altitudeOk, bool positionOk) noexcept
{
    if (attitudeOk && altitudeOk && positionOk) {
        return Mode::PosHold;
    }
    if (attitudeOk && altitudeOk) {
        return Mode::AltHold;
    }
    return attitudeOk ? Mode::Stabilize : Mode::Manual;
}

}  // namespace fm
