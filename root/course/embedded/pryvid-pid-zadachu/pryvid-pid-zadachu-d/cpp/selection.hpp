#pragma once

#include "drive.hpp"

#include <cstddef>
#include <expected>
#include <optional>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace drive {

// Вимоги задачі — на ВИХІДНОМУ валу: саме там живе навантаження.
struct Task {
    std::string_view label{};
    double loadTorqueNm{};
    double loadInertiaKgm2{};
    double targetSpeedRpm{};
    double accelTimeS{};
    double moveDuty{1.0};              // частка часу в русі
    bool holdsUnderLoad{false};        // у паузах тримає позицію під навантаженням
    double positionToleranceDeg{0.0};  // 0 — позиціонування не потрібне
    double ambientC{25.0};
    double insulationLimitC{105.0};
    double powerBudgetW{0.0};          // 0 — бюджет не заданий

    [[nodiscard]] std::optional<std::string_view> problem() const noexcept;
};

enum class Issue {
    TorqueShort,
    StepLoss,
    SpeedExceeded,
    Overheat,
    PowerBudget,
    NoFeedback,
    PrecisionShort,
    // попередження: привід придатний, але про це кажуть уголос
    InrushSpike,
    TorqueFade,
    RunsHot
};

[[nodiscard]] std::string_view describe(Issue issue) noexcept;
[[nodiscard]] std::string join(std::span<const Issue> issues);

struct Heat {
    double moveW{};
    double holdW{};
    double averageW{};
    double gearW{};        // втрати передачі: гріють редуктор, не обмотку
    double windingC{};
};

struct Report {
    double motorSpeedRpm{};
    double cruiseTorqueNm{};      // лише статика, приведена до вала мотора
    double peakTorqueNm{};        // статика + інерція розгону
    double availableTorqueNm{};
    double margin{};
    double requiredMargin{};
    double peakCurrentA{};
    double stallCurrentA{};
    std::optional<double> outputResolutionDeg{};   // порожньо — давача немає
    double electricalPowerW{};
    Heat heat{};
    std::vector<Issue> failures{};
    std::vector<Issue> warnings{};

    [[nodiscard]] bool fits() const noexcept { return failures.empty(); }
};

// Помилка — це суперечливий паспорт або суперечлива задача. Недотягнутий
// привід помилкою НЕ є: це звичайний результат розрахунку з переліком причин.
struct BadInput {
    std::string_view what;
};

[[nodiscard]] std::expected<Report, BadInput> evaluate(const Unit& unit, const Task& task);

// Індекс кандидата з найбільшим запасом моменту серед тих, що проходять.
[[nodiscard]] std::optional<std::size_t> bestFit(std::span<const Unit> units, const Task& task);

}  // namespace drive
