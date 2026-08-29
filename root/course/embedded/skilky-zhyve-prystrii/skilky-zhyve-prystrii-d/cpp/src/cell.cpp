#include "cell.hpp"

#include <algorithm>
#include <cmath>
#include <functional>
#include <iterator>

namespace autonomy {
namespace {

constexpr double kHoursPerYear = 8766.0;   // 365.25 доби · 24 год
constexpr double kKelvinZero   = 273.15;
constexpr double kKelvinRef    = 293.15;   // +20 °C — умови паспортних вимірювань
constexpr double kArrheniusQ10 = 2.0;      // подвоєння швидкості на кожні 10 °C

double lerp_at(double x, double x0, double y0, double x1, double y1) noexcept
{
    const double span = x1 - x0;
    if (span == 0.0) {
        return y1;
    }
    return y0 + (x - x0) / span * (y1 - y0);
}

}  // namespace

std::string_view describe(Error e) noexcept
{
    switch (e) {
    case Error::CapacityNotPositive:      return "ємність або еталонний струм не додатні";
    case Error::VoltageNotPositive:       return "напруга або внутрішній опір не додатні";
    case Error::CurveTooShort:            return "у розрядній кривій менше двох точок";
    case Error::CurveNotDescending:       return "розрядна крива не впорядкована за спаданням напруги";
    case Error::TemperatureTableBroken:   return "температурна таблиця не впорядкована за зростанням";
    case Error::PeukertOutOfRange:        return "експонента Пейкерта поза межами [1.0, 2.0]";
    case Error::NoPhases:                 return "у робочому циклі немає жодної активної фази";
    case Error::PhaseDurationNotPositive: return "тривалість фази не додатна";
    case Error::NegativeCurrent:          return "від'ємний струм фази";
    case Error::PeriodTooShort:           return "активні фази не влазять у період циклу";
    case Error::CutoffAboveFresh:         return "поріг відсічки вищий за напругу свіжої комірки";
    case Error::SafetyFactorOutOfRange:   return "коефіцієнт запасу поза межами (0, 1]";
    case Error::NoDrain:                  return "сумарний струм нульовий — час життя нескінченний";
    }
    return "невідома помилка";
}

std::expected<Cell, Error> Cell::create(Spec spec)
{
    if (spec.capacity_mah <= 0.0 || spec.reference_current_ma <= 0.0) {
        return std::unexpected{Error::CapacityNotPositive};
    }
    if (spec.ocv_fresh_v <= 0.0 || spec.r_int_20c_ohm <= 0.0) {
        return std::unexpected{Error::VoltageNotPositive};
    }
    if (spec.peukert_k < 1.0 || spec.peukert_k > 2.0) {
        return std::unexpected{Error::PeukertOutOfRange};
    }
    if (spec.curve.size() < 2 || spec.temperature.size() < 2) {
        return std::unexpected{Error::CurveTooShort};
    }

    // Напруга мусить спадати, віддана частка — не спадати.
    const bool curve_ok = std::ranges::is_sorted(spec.curve, std::greater<>{}, &CurvePoint::ocv_v) &&
                          std::ranges::adjacent_find(spec.curve, std::greater<>{}, &CurvePoint::delivered) ==
                              spec.curve.end() &&
                          spec.curve.front().delivered >= 0.0 &&
                          spec.curve.back().delivered <= 1.0;
    if (!curve_ok) {
        return std::unexpected{Error::CurveNotDescending};
    }

    const bool temp_ok = std::ranges::is_sorted(spec.temperature, std::less<>{}, &TempPoint::temp_c) &&
                         std::ranges::all_of(spec.temperature, [](const TempPoint& p) {
                             return p.factor >= 0.0 && p.factor <= 1.0;
                         });
    if (!temp_ok) {
        return std::unexpected{Error::TemperatureTableBroken};
    }

    return Cell{std::move(spec)};
}

double Cell::internal_resistance(double temp_c) const
{
    // Нижче цієї межі електроліт уже не рідина — модель не працює, але й
    // ділити на нуль не даємо.
    const double t_k = std::max(temp_c + kKelvinZero, 100.0);

    // R(T) = R20 · exp(B · (1/T − 1/293.15)): за B ≈ 6300 K це дає паспортні
    // 0.5 Ом за +20 °C і майже 15 Ом за −20 °C.
    return spec_.r_int_20c_ohm * std::exp(spec_.r_int_beta_k * (1.0 / t_k - 1.0 / kKelvinRef));
}

double Cell::passivation_factor(Days idle) const
{
    if (spec_.passivation_onset <= Days{0} || spec_.passivation_max_factor <= 1.0 || idle <= Days{0}) {
        return 1.0;
    }

    // Плівка LiCl росте приблизно як корінь із часу спокою: товща плівка сама
    // гальмує реакцію, що її нарощує.
    const double ratio = std::clamp(idle / spec_.passivation_onset, 0.0, 1.0);
    return 1.0 + (spec_.passivation_max_factor - 1.0) * std::sqrt(ratio);
}

double Cell::delivered_above(double ocv_v) const
{
    const auto& curve = spec_.curve;

    // Поріг вищий за напругу свіжої комірки — вона мертва з першого дня.
    if (ocv_v >= curve.front().ocv_v) {
        return curve.front().delivered;
    }
    if (ocv_v <= curve.back().ocv_v) {
        return curve.back().delivered;
    }

    const auto next = std::ranges::find_if(curve, [ocv_v](const CurvePoint& p) { return p.ocv_v <= ocv_v; });
    const auto prev = std::prev(next);
    return lerp_at(ocv_v, prev->ocv_v, prev->delivered, next->ocv_v, next->delivered);
}

double Cell::ocv_at(double delivered) const
{
    const auto& curve = spec_.curve;

    if (delivered <= curve.front().delivered) {
        return curve.front().ocv_v;
    }
    if (delivered >= curve.back().delivered) {
        return curve.back().ocv_v;
    }

    const auto next =
        std::ranges::find_if(curve, [delivered](const CurvePoint& p) { return p.delivered >= delivered; });
    const auto prev = std::prev(next);
    return lerp_at(delivered, prev->delivered, prev->ocv_v, next->delivered, next->ocv_v);
}

double Cell::temperature_factor(double temp_c) const
{
    const auto& table = spec_.temperature;

    if (temp_c <= table.front().temp_c) {
        return table.front().factor;
    }
    if (temp_c >= table.back().temp_c) {
        return table.back().factor;
    }

    const auto next = std::ranges::find_if(table, [temp_c](const TempPoint& p) { return p.temp_c >= temp_c; });
    const auto prev = std::prev(next);
    return lerp_at(temp_c, prev->temp_c, prev->factor, next->temp_c, next->factor);
}

double Cell::self_discharge_ma(double temp_c) const
{
    const double accel = std::pow(kArrheniusQ10, (temp_c - 20.0) / 10.0);
    const double pct_year = spec_.self_discharge_pct_year * accel;

    // Річний відсоток втрати ємності — це постійний віртуальний струм витоку.
    return spec_.capacity_mah * pct_year / 100.0 / kHoursPerYear;
}

double Cell::peukert_cost(double current_ma) const
{
    if (current_ma <= spec_.reference_current_ma) {
        return 1.0;
    }
    return std::pow(current_ma / spec_.reference_current_ma, spec_.peukert_k - 1.0);
}

}  // namespace autonomy
