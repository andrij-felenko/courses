#include "drive.hpp"

#include <cmath>

namespace drive {
namespace {

// Скільки обмоток одночасно під струмом.
[[nodiscard]] double phaseFactor(Family family) noexcept {
    switch (family) {
    case Family::Stepper:   return 2.0;   // обидві фази статора
    case Family::Brushless: return 1.5;   // 3 * (I_peak / sqrt(2))^2 для синусоїдного FOC
    default:                return 1.0;   // один контур якоря
    }
}

}  // namespace

std::string_view familyName(Family family) noexcept {
    switch (family) {
    case Family::Brushed:   return "колекторний";
    case Family::Stepper:   return "кроковий";
    case Family::Brushless: return "безколекторний";
    case Family::Servo:     return "сервопривід";
    }
    return "невідомий";
}

double Motor::torqueConstant() const noexcept {
    return ratedCurrentA > 0.0 ? ratedTorqueNm / ratedCurrentA : 0.0;
}

double Motor::stallCurrentA() const noexcept {
    // У крокового пускового кидка немає: чоппер тримає струм на уставці.
    if (family == Family::Stepper) {
        return ratedCurrentA;
    }
    return phaseResistanceOhm > 0.0 ? supplyV / phaseResistanceOhm : 0.0;
}

double Motor::availableTorqueNm(double omegaRadS) const noexcept {
    const double rpm = radSToRpm(std::fabs(omegaRadS));
    if (noLoadSpeedRpm <= 0.0 || rpm > noLoadSpeedRpm) {
        return 0.0;
    }

    switch (family) {
    case Family::Brushed:
        // T(w) = T_stall * (1 - w / w_0): протиЕРС лінійно з'їдає напругу.
        return torqueConstant() * stallCurrentA() * (1.0 - rpm / noLoadSpeedRpm);

    case Family::Stepper: {
        // Індуктивність не дає струму наростати за час кроку: спад першого
        // порядку від частоти імпульсів зі зламом на cornerSpeedRpm.
        if (cornerSpeedRpm <= 0.0) {
            return ratedTorqueNm;
        }
        const double x = rpm / cornerSpeedRpm;
        return ratedTorqueNm / std::sqrt(1.0 + x * x);
    }

    case Family::Brushless:
        // До базової швидкості — сталий момент, вище — стала потужність.
        if (cornerSpeedRpm <= 0.0 || rpm <= cornerSpeedRpm) {
            return ratedTorqueNm;
        }
        return ratedTorqueNm * (cornerSpeedRpm / rpm);

    case Family::Servo:
        // Редуктор тримає паспортний момент аж до межі обертів.
        return ratedTorqueNm;
    }
    return 0.0;
}

double Motor::currentForTorqueA(double torqueNm) const noexcept {
    // Кроковий бере повний струм фази незалежно від навантаження — саме звідси
    // його нагрів тоді, коли він не робить жодної корисної роботи.
    if (family == Family::Stepper) {
        return ratedCurrentA;
    }
    const double kt = torqueConstant();
    return kt > 0.0 ? std::fabs(torqueNm) / kt : 0.0;
}

double Motor::copperLossW(double torqueNm, Regime regime) const noexcept {
    const double current = (family == Family::Stepper)
        ? ratedCurrentA * (regime == Regime::Standstill ? holdCurrentFraction : 1.0)
        : currentForTorqueA(torqueNm);
    return phaseFactor(family) * current * current * phaseResistanceOhm;   // P = k * I^2 * R
}

double Motor::windingTempC(double averageLossW, double ambientC) const noexcept {
    return ambientC + averageLossW * thermalResistanceCPerW;
}

std::optional<std::string_view> Motor::problem() const noexcept {
    if (name.empty()) {
        return "паспорт мотора без назви";
    }
    if (ratedTorqueNm <= 0.0) {
        return "номінальний момент має бути додатним";
    }
    if (ratedCurrentA <= 0.0) {
        return "номінальний струм має бути додатним";
    }
    if (noLoadSpeedRpm <= 0.0) {
        return "межа обертів має бути додатною";
    }
    if (phaseResistanceOhm <= 0.0) {
        return "опір обмотки має бути додатним";
    }
    if (thermalResistanceCPerW <= 0.0) {
        return "тепловий опір має бути додатним";
    }
    if (rotorInertiaKgm2 < 0.0) {
        return "момент інерції ротора від'ємний";
    }
    if (holdCurrentFraction < 0.0 || holdCurrentFraction > 1.0) {
        return "частка струму утримання поза межами 0..1";
    }
    if (stepResolutionDeg < 0.0) {
        return "дискрет положення від'ємний";
    }
    if ((family == Family::Stepper || family == Family::Brushless) &&
        (cornerSpeedRpm <= 0.0 || cornerSpeedRpm > noLoadSpeedRpm)) {
        return "злам кривої моменту поза робочим діапазоном";
    }
    if (family == Family::Brushed) {
        // k_e = k_t, тож холостий хід не має права розходитися з V / k_t.
        // Розходження означає, що числа зібрані з різних моторів.
        if (supplyV <= 0.0) {
            return "напруга живлення має бути додатною";
        }
        const double idealRpm = radSToRpm(supplyV / torqueConstant());
        if (noLoadSpeedRpm > 1.5 * idealRpm || noLoadSpeedRpm * 1.5 < idealRpm) {
            return "паспорт суперечливий: холостий хід не сходиться з V / k_t";
        }
    }
    return std::nullopt;
}

double Gearbox::reflectTorque(double loadTorqueNm) const noexcept {
    return loadTorqueNm / (ratio * efficiency);       // передача ділить момент на N * eta
}

double Gearbox::reflectInertia(double loadInertiaKgm2) const noexcept {
    return loadInertiaKgm2 / (ratio * ratio);         // а інерцію — на квадрат N
}

double Gearbox::heatLossW(double outputPowerW) const noexcept {
    if (efficiency <= 0.0) {
        return 0.0;
    }
    return std::fabs(outputPowerW) * (1.0 - efficiency) / efficiency;
}

std::optional<std::string_view> Gearbox::problem() const noexcept {
    if (ratio <= 0.0) {
        return "передавальне відношення має бути додатним";
    }
    if (efficiency <= 0.0 || efficiency > 1.0) {
        return "ККД передачі поза межами 0..1";
    }
    if (backlashDeg < 0.0) {
        return "люфт від'ємний";
    }
    return std::nullopt;
}

}  // namespace drive
