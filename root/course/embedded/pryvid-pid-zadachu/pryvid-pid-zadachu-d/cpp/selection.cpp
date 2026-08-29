#include "selection.hpp"

#include <limits>

namespace drive {
namespace {

// Запас моменту, менше за який привід не беруть.
[[nodiscard]] double requiredMargin(Family family) noexcept {
    switch (family) {
    case Family::Stepper: return 2.0;   // open-loop: зрив кроку нікому помітити
    case Family::Servo:   return 1.5;   // пластик редуктора й нагрів у стопорі
    default:              return 1.3;   // є зворотний зв'язок — досить 30%
    }
}

}  // namespace

std::optional<std::string_view> Task::problem() const noexcept {
    if (label.empty()) {
        return "задача без назви";
    }
    if (targetSpeedRpm <= 0.0) {
        return "цільова швидкість має бути додатною";
    }
    if (accelTimeS <= 0.0) {
        return "час розгону має бути додатним";
    }
    if (loadTorqueNm < 0.0 || loadInertiaKgm2 < 0.0) {
        return "від'ємне навантаження";
    }
    if (moveDuty < 0.0 || moveDuty > 1.0) {
        return "частка часу в русі поза межами 0..1";
    }
    if (insulationLimitC <= ambientC) {
        return "межа ізоляції не вища за температуру середовища";
    }
    return std::nullopt;
}

std::string_view describe(Issue issue) noexcept {
    switch (issue) {
    case Issue::TorqueShort:    return "бракує моменту";
    case Issue::StepLoss:       return "ризик зриву кроків";
    case Issue::SpeedExceeded:  return "перевищено межу обертів";
    case Issue::Overheat:       return "перегрів обмотки";
    case Issue::PowerBudget:    return "не вкладається в бюджет живлення";
    case Issue::NoFeedback:     return "немає давача положення";
    case Issue::PrecisionShort: return "дискрет із люфтом грубші за допуск";
    case Issue::InrushSpike:    return "пусковий струм треба обмежувати драйвером";
    case Issue::TorqueFade:     return "працює в зоні обвалу моменту";
    case Issue::RunsHot:        return "температура близька до межі";
    }
    return "невідома причина";
}

std::string join(std::span<const Issue> issues) {
    std::string text;
    for (const Issue issue : issues) {
        if (!text.empty()) {
            text += ", ";
        }
        text += describe(issue);
    }
    return text;
}

std::expected<Report, BadInput> evaluate(const Unit& unit, const Task& task) {
    if (const auto bad = unit.motor.problem()) {
        return std::unexpected(BadInput{*bad});
    }
    if (const auto bad = unit.gear.problem()) {
        return std::unexpected(BadInput{*bad});
    }
    if (const auto bad = task.problem()) {
        return std::unexpected(BadInput{*bad});
    }

    const Motor& motor = unit.motor;
    const Gearbox& gear = unit.gear;

    const double omegaLoad = rpmToRadS(task.targetSpeedRpm);
    const double alphaLoad = omegaLoad / task.accelTimeS;
    const double omegaMotor = omegaLoad * gear.ratio;
    const double alphaMotor = alphaLoad * gear.ratio;

    Report report;
    report.motorSpeedRpm = radSToRpm(omegaMotor);

    // T_motor = T_load / (N * eta) + (J_rotor + J_load / N^2) * alpha_motor
    report.cruiseTorqueNm = gear.reflectTorque(task.loadTorqueNm);
    const double inertia = motor.rotorInertiaKgm2 + gear.reflectInertia(task.loadInertiaKgm2);
    report.peakTorqueNm = report.cruiseTorqueNm + inertia * alphaMotor;

    report.availableTorqueNm = motor.availableTorqueNm(omegaMotor);
    report.requiredMargin = requiredMargin(motor.family);
    report.margin = report.peakTorqueNm > 0.0
        ? report.availableTorqueNm / report.peakTorqueNm
        : std::numeric_limits<double>::infinity();

    if (report.motorSpeedRpm > motor.noLoadSpeedRpm) {
        report.failures.push_back(Issue::SpeedExceeded);
    }
    if (report.margin < report.requiredMargin) {
        report.failures.push_back(motor.family == Family::Stepper
            ? Issue::StepLoss
            : Issue::TorqueShort);
    }
    if (motor.family == Family::Stepper && report.availableTorqueNm < 0.5 * motor.ratedTorqueNm) {
        report.warnings.push_back(Issue::TorqueFade);
    }

    // Драйвер добирають за піком розгону, а не за середнім струмом.
    report.peakCurrentA = motor.currentForTorqueA(report.peakTorqueNm);
    report.stallCurrentA = motor.stallCurrentA();
    if (motor.family != Family::Stepper && report.stallCurrentA > 4.0 * motor.ratedCurrentA) {
        report.warnings.push_back(Issue::InrushSpike);
    }

    // Тепло: у русі гріє крейсерський момент, у паузі — утримання. Розгін
    // короткий і в середню потужність не входить. Кроковий гріється в паузі
    // завжди: фази лишаються під струмом, хай і зменшеним.
    const double holdTorque = task.holdsUnderLoad ? report.cruiseTorqueNm : 0.0;
    report.heat.moveW = motor.copperLossW(report.cruiseTorqueNm, Regime::Moving);
    report.heat.holdW = (task.holdsUnderLoad || motor.family == Family::Stepper)
        ? motor.copperLossW(holdTorque, Regime::Standstill)
        : 0.0;
    report.heat.averageW = task.moveDuty * report.heat.moveW
                         + (1.0 - task.moveDuty) * report.heat.holdW;
    report.heat.gearW = gear.heatLossW(task.loadTorqueNm * omegaLoad);
    report.heat.windingC = motor.windingTempC(report.heat.averageW, task.ambientC);

    const double hotThresholdC = task.ambientC + 0.85 * (task.insulationLimitC - task.ambientC);
    if (report.heat.windingC > task.insulationLimitC) {
        report.failures.push_back(Issue::Overheat);
    } else if (report.heat.windingC > hotThresholdC) {
        report.warnings.push_back(Issue::RunsHot);
    }

    // Оцінка входу: механіка на валу мотора (втрати передачі вже всередині
    // cruiseTorqueNm) плюс мідні втрати.
    report.electricalPowerW = report.cruiseTorqueNm * omegaMotor * task.moveDuty
                            + report.heat.averageW;
    if (task.powerBudgetW > 0.0 && report.electricalPowerW > task.powerBudgetW) {
        report.failures.push_back(Issue::PowerBudget);
    }

    // Дискрет на вихідному валу: редуктор ділить крок, але додає свій люфт.
    if (motor.stepResolutionDeg > 0.0) {
        report.outputResolutionDeg = motor.stepResolutionDeg / gear.ratio + gear.backlashDeg;
    }
    if (task.positionToleranceDeg > 0.0) {
        if (!report.outputResolutionDeg) {
            report.failures.push_back(Issue::NoFeedback);
        } else if (*report.outputResolutionDeg > task.positionToleranceDeg) {
            report.failures.push_back(Issue::PrecisionShort);
        }
    }

    return report;
}

std::optional<std::size_t> bestFit(std::span<const Unit> units, const Task& task) {
    std::optional<std::size_t> best;
    double bestMargin = 0.0;

    for (std::size_t i = 0; i < units.size(); ++i) {
        const auto report = evaluate(units[i], task);
        if (!report || !report->fits()) {
            continue;
        }
        if (!best || report->margin > bestMargin) {
            best = i;
            bestMargin = report->margin;
        }
    }
    return best;
}

}  // namespace drive
