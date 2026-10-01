#include "dt838_processor.hpp"
#include <cmath>
#include <sstream>
#include <iomanip>

namespace dt838 {

MeasurementResult AdcConvertor::processRawAdc(int16_t rawAdcCount, MeasurementMode mode) const {
    MeasurementResult res;

    // АЦП ICL7106 мультиметра DT-838 показує 1999 при виході за межі вимірювання
    if (std::abs(rawAdcCount) >= 1999) {
        res.overflow = true;
        res.valid = false;
        res.value = 0.0;
        res.unit = "";
        res.description = "Перевищення межі вимірювання (Overflow)";
        return res;
    }

    switch (mode) {
        case MeasurementMode::VoltageDC_200mV:
            res.value = rawAdcCount * 0.1;
            res.unit = "мВ";
            res.description = "Постійна напруга (DC 200 мВ)";
            break;
        case MeasurementMode::VoltageDC_2000mV:
            res.value = rawAdcCount * 1.0;
            res.unit = "мВ";
            res.description = "Постійна напруга (DC 2000 мВ)";
            break;
        case MeasurementMode::VoltageDC_20V:
            res.value = rawAdcCount * 0.01;
            res.unit = "В";
            res.description = "Постійна напруга (DC 20 В)";
            break;
        case MeasurementMode::VoltageDC_200V:
            res.value = rawAdcCount * 0.1;
            res.unit = "В";
            res.description = "Постійна напруга (DC 200 В)";
            break;
        case MeasurementMode::VoltageDC_1000V:
            res.value = rawAdcCount * 1.0;
            res.unit = "В";
            res.description = "Постійна напруга (DC 1000 В)";
            break;
        case MeasurementMode::VoltageAC_200V:
            res.value = rawAdcCount * 0.1;
            res.unit = "В (змінна)";
            res.description = "Змінна напруга (AC 200 В)";
            break;
        case MeasurementMode::VoltageAC_750V:
            res.value = rawAdcCount * 1.0;
            res.unit = "В (змінна)";
            res.description = "Змінна напруга (AC 750 В)";
            break;
        case MeasurementMode::Resistance_200Ohm:
            res.value = rawAdcCount * 0.1;
            res.unit = "Ом";
            res.description = "Опір (200 Ом)";
            break;
        case MeasurementMode::Resistance_2000Ohm:
            res.value = rawAdcCount * 1.0;
            res.unit = "Ом";
            res.description = "Опір (2000 Ом)";
            break;
        case MeasurementMode::Resistance_20kOhm:
            res.value = rawAdcCount * 0.01;
            res.unit = "кОм";
            res.description = "Опір (20 кОм)";
            break;
        case MeasurementMode::Resistance_200kOhm:
            res.value = rawAdcCount * 0.1;
            res.unit = "кОм";
            res.description = "Опір (200 кОм)";
            break;
        case MeasurementMode::Resistance_2000kOhm:
            res.value = rawAdcCount * 1.0;
            res.unit = "кОм";
            res.description = "Опір (2000 кОм)";
            break;
        case MeasurementMode::DiodeTest:
            res.value = rawAdcCount * 1.0;
            res.unit = "мВ";
            res.description = "Діодний тест (пряме падіння)";
            break;
        case MeasurementMode::Temperature:
            res.value = rawAdcCount * 1.0;
            res.unit = "°C";
            res.description = "Вимірювання температури";
            break;
    }

    res.overflow = false;
    res.valid = true;
    return res;
}

SemiconductorState DiodeTester::evaluateJunction(double voltageDropmV) const {
    if (voltageDropmV < 100.0) {
        return SemiconductorState::ShortCircuit;
    } else if (voltageDropmV >= 150.0 && voltageDropmV <= 450.0) {
        return SemiconductorState::NormalGermanium;
    } else if (voltageDropmV > 450.0 && voltageDropmV <= 900.0) {
        return SemiconductorState::NormalSilicon;
    } else if (voltageDropmV > 1500.0) {
        return SemiconductorState::OpenCircuit;
    }
    return SemiconductorState::Unknown;
}

std::string_view DiodeTester::getStateDescription(SemiconductorState state) {
    switch (state) {
        case SemiconductorState::NormalSilicon:
            return "Справний кремнієвий p-n перехід (падіння 0.5–0.9 В)";
        case SemiconductorState::NormalGermanium:
            return "Справний германієвий p-n перехід або діод Шотткі (падіння 0.2–0.4 В)";
        case SemiconductorState::ShortCircuit:
            return "УВАГА: Коротке замикання або пробій p-n переходу (< 0.1 В)";
        case SemiconductorState::OpenCircuit:
            return "Обрив переходу або зворотне включення (зашкалювання / > 1.5 В)";
        case SemiconductorState::Unknown:
            return "Нетипове значення падіння напруги на переході";
    }
    return "Невідомий стан";
}

TemperatureEvaluator::TemperatureEvaluator(double minAllowedCelsius, double maxAllowedCelsius)
    : minTemp_(minAllowedCelsius), maxTemp_(maxAllowedCelsius) {}

void TemperatureEvaluator::setLimits(double minAllowed, double maxAllowed) {
    minTemp_ = minAllowed;
    maxTemp_ = maxAllowed;
}

TemperatureStatus TemperatureEvaluator::evaluate(double rawThermocoupleVoltagemV, double ambientTempCelsius) const {
    TemperatureStatus status;

    double thermocoupleDeltaTemp = rawThermocoupleVoltagemV / SeebeckCoefficientmVPerC;
    status.temperatureCelsius = ambientTempCelsius + thermocoupleDeltaTemp;

    if (status.temperatureCelsius > maxTemp_) {
        status.withinLimits = false;
        status.highAlarm = true;
        status.lowAlarm = false;
        std::ostringstream ss;
        ss << "ПЕРЕВИЩЕННЯ МАКСИМАЛЬНОЇ ТЕМПЕРАТУРИ: " 
           << std::fixed << std::setprecision(1) << status.temperatureCelsius 
           << " °C (межа: " << maxTemp_ << " °C)";
        status.message = ss.str();
    } else if (status.temperatureCelsius < minTemp_) {
        status.withinLimits = false;
        status.highAlarm = false;
        status.lowAlarm = true;
        std::ostringstream ss;
        ss << "ВИХІД ЗА НИЖНЮ МЕЖУ ТЕМПЕРАТУРИ: " 
           << std::fixed << std::setprecision(1) << status.temperatureCelsius 
           << " °C (межа: " << minTemp_ << " °C)";
        status.message = ss.str();
    } else {
        status.withinLimits = true;
        status.highAlarm = false;
        status.lowAlarm = false;
        std::ostringstream ss;
        ss << "Температура в нормі: " 
           << std::fixed << std::setprecision(1) << status.temperatureCelsius << " °C";
        status.message = ss.str();
    }

    return status;
}

} // namespace dt838
