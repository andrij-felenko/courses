#pragma once

// Модель первинної хімічної комірки.
//
// Комірку не можна зібрати з довільних чисел: розрядна крива мусить спадати,
// температурна таблиця — зростати, ємність бути додатною. Тому конструктор
// закритий, а єдиний вхід — фабрика Cell::create, яка повертає або готову
// комірку, або код помилки. Зібраний об'єкт уже коректний за побудовою.

#include <chrono>
#include <expected>
#include <string>
#include <string_view>
#include <vector>

namespace autonomy {

using Seconds = std::chrono::duration<double>;
using Hours   = std::chrono::duration<double, std::ratio<3600>>;
using Days    = std::chrono::duration<double, std::ratio<86400>>;
using Years   = std::chrono::duration<double, std::ratio<31'557'600>>;  // 365.25 доби

enum class Error {
    CapacityNotPositive,
    VoltageNotPositive,
    CurveTooShort,
    CurveNotDescending,
    TemperatureTableBroken,
    PeukertOutOfRange,
    NoPhases,
    PhaseDurationNotPositive,
    NegativeCurrent,
    PeriodTooShort,
    CutoffAboveFresh,
    SafetyFactorOutOfRange,
    NoDrain,
};

std::string_view describe(Error e) noexcept;

// Точка розрядної кривої з даташиту: напруга розімкненого кола і частка
// паспортної ємності, вже віддана на момент, коли OCV впала до цієї позначки.
struct CurvePoint {
    double ocv_v;
    double delivered;
};

// Температурна залежність доступної ємності.
struct TempPoint {
    double temp_c;
    double factor;
};

class Cell {
public:
    struct Spec {
        std::string name;
        double capacity_mah{};
        double ocv_fresh_v{};
        double reference_current_ma{};   // струм, за якого міряли паспортну ємність
        double r_int_20c_ohm{};
        double r_int_beta_k{};           // B-константа температурної залежності опору
        double peukert_k{1.0};
        Seconds relax_time{};            // стала часу релаксації іонів між імпульсами
        double self_discharge_pct_year{};
        double passivation_max_factor{1.0};
        Days passivation_onset{};
        std::vector<CurvePoint> curve;       // за спаданням напруги
        std::vector<TempPoint> temperature;  // за зростанням температури
    };

    static std::expected<Cell, Error> create(Spec spec);

    const std::string& name() const noexcept { return spec_.name; }
    double capacity_mah() const noexcept { return spec_.capacity_mah; }
    double ocv_fresh_v() const noexcept { return spec_.ocv_fresh_v; }
    double self_discharge_pct_year() const noexcept { return spec_.self_discharge_pct_year; }
    Seconds relax_time() const noexcept { return spec_.relax_time; }

    // Внутрішній опір за заданої температури (Арреніус у NTC-формі).
    double internal_resistance(double temp_c) const;

    // Множник опору від пасиваційної плівки LiCl після спокою.
    double passivation_factor(Days idle) const;

    // η_cutoff: частка ємності, яку комірка встигає віддати, поки її OCV
    // падає до заданої позначки. Усе, що нижче, для схеми недосяжне.
    double delivered_above(double ocv_v) const;

    // Обернена задача: якою буде OCV, коли віддано частку delivered.
    double ocv_at(double delivered) const;

    double temperature_factor(double temp_c) const;

    // Еквівалентний струм саморозряду, мА. Швидкість реакції подвоюється
    // на кожні 10 °C.
    double self_discharge_ma(double temp_c) const;

    // У скільки разів дорожче обходиться заряд, узятий цим струмом (Пейкерт).
    // Нижче еталонного струму бонусу не рахуємо: паспорт його не гарантує.
    double peukert_cost(double current_ma) const;

private:
    explicit Cell(Spec spec) noexcept : spec_{std::move(spec)} {}

    Spec spec_;
};

}  // namespace autonomy
