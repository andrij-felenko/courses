#include "guards.hpp"

#include <cmath>

#include "mission.hpp"

namespace fm::guard {

GuardResult imu(const VehicleState& s) noexcept
{
    if (!s.imu.gyroHealthy) {
        return std::unexpected(Deny::Imu);
    }
    return {};
}

GuardResult attitude(const VehicleState& s) noexcept
{
    if (auto base = imu(s); !base) {
        return base;
    }
    if (!s.imu.accelHealthy || !s.imu.attitudeValid) {
        return std::unexpected(Deny::Attitude);
    }
    return {};
}

GuardResult altitude(const VehicleState& s, const Params&) noexcept
{
    if (auto base = attitude(s); !base) {
        return base;
    }
    // Вертикальний контур живиться баро АБО далекоміром: втрата одного джерела
    // ще не позбавляє автомат висоти, втрата обох — позбавляє.
    if (!s.vertical.baroHealthy && !s.vertical.rangefinderHealthy) {
        return std::unexpected(Deny::AltEstimate);
    }
    if (!s.vertical.ekfPosValid) {
        return std::unexpected(Deny::AltEstimate);
    }
    if (std::isnan(s.vertical.altitudeRelM) || std::isnan(s.vertical.velocityMs)) {
        return std::unexpected(Deny::AltEstimate);
    }
    return {};
}

GuardResult position(const VehicleState& s, const Params& p) noexcept
{
    if (auto base = altitude(s, p); !base) {
        return base;
    }

    const HorizontalStatus& h = s.horizontal;

    // 1. Формальний супутниковий фікс.
    if (h.fixType < p.gnssMinFixType || h.sats < p.gnssMinSats) {
        return std::unexpected(Deny::NoGnssFix);
    }

    // 2. Геометрія сузір'я: шість супутників в одному секторі неба дають
    //    координату з похибкою в десятки метрів.
    if (std::isnan(h.hdop) || std::isnan(h.vdop) ||
        h.hdop > p.gnssMaxHdop || h.vdop > p.gnssMaxVdop) {
        return std::unexpected(Deny::BadDop);
    }

    // 3. Сходження оцінок фільтра. Інновація понад одиницю означає, що
    //    інерціальний прогноз і супутниковий вимір суперечать одне одному.
    if (std::isnan(h.innovPosNorm) || std::isnan(h.innovVelNorm) ||
        h.innovPosNorm >= p.ekfGlitchInnov || h.innovVelNorm >= p.ekfGlitchInnov) {
        return std::unexpected(Deny::EkfGlitch);
    }
    if (!h.ekfPosValid || h.innovPosNorm > p.ekfMaxInnovPos ||
        h.innovVelNorm > p.ekfMaxInnovVel) {
        return std::unexpected(Deny::EkfInnovation);
    }

    // 4. Курс: без нього вектор зміщення в системі Північ-Схід не перекладеться
    //    в систему координат апарата, і знос компенсуватиметься не туди.
    if (!h.compassHealthy || std::isnan(h.compassYawErrorDeg) ||
        std::fabs(h.compassYawErrorDeg) > p.compassMaxYawErrDeg) {
        return std::unexpected(Deny::Compass);
    }
    return {};
}

GuardResult guided(const VehicleState& s, const Params& p) noexcept
{
    if (auto base = position(s, p); !base) {
        return base;
    }
    // Мовчазний супровідний комп'ютер перетворює Guided на політ у нікуди за
    // останньою відомою точкою.
    if (s.age(s.links.lastGuidedSetpoint) > p.guidedTimeout) {
        return std::unexpected(Deny::GuidedLink);
    }
    return {};
}

GuardResult mission(const VehicleState& s, const Params& p)
{
    if (auto base = position(s, p); !base) {
        return base;
    }
    if (!s.home) {
        return std::unexpected(Deny::NoHome);
    }
    if (s.mission == nullptr || s.mission->empty()) {
        return std::unexpected(Deny::NoMission);
    }

    const auto verdict = s.mission->validate(*s.home, p.fenceRadiusM, p.missionMaxAltM);

    if (!verdict) {
        return std::unexpected(verdict.error() == MissionError::Empty ? Deny::NoMission
                                                                      : Deny::BadMission);
    }
    return {};
}

GuardResult rtl(const VehicleState& s, const Params& p) noexcept
{
    if (auto base = altitude(s, p); !base) {
        return base;
    }
    // Повертатися нема куди — це не «спробуємо якось»: без точки старту запит
    // перенаправляється в Land, і рішення це ухвалює викликач.
    if (!s.home) {
        return std::unexpected(Deny::NoHome);
    }
    if (!s.horizontal.ekfPosValid) {
        return std::unexpected(Deny::EkfInnovation);
    }
    return {};
}

GuardResult check(Mode target, const VehicleState& s, const Params& p)
{
    if (!valid(target)) {
        return std::unexpected(Deny::InvalidMode);
    }

    switch (target) {
    case Mode::Manual:        return imu(s);
    case Mode::Stabilize:     return attitude(s);
    case Mode::AltHold:       return altitude(s, p);
    case Mode::PosHold:       return position(s, p);
    case Mode::Guided:        return guided(s, p);
    case Mode::Auto:          return mission(s, p);
    case Mode::Rtl:           return rtl(s, p);
    // Посадка вимагає вертикальної оцінки; без неї лишається аварійний спуск
    // на самих кутах і фіксованій тязі.
    case Mode::Land:          return altitude(s, p);
    case Mode::EmergencyLand: return attitude(s);
    // Відсічка мусить спрацювати за будь-якого стану сенсорів.
    case Mode::Terminate:     return {};
    }
    return std::unexpected(Deny::InvalidMode);
}

}  // namespace fm::guard
