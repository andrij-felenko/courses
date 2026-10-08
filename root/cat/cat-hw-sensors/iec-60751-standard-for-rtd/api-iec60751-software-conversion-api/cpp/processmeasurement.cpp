// Комплексна обробка вимірювання та діагностика на мові C++
#include "rtd_api.hpp"

namespace Sensors {

RtdStatus processMeasurement(const RtdSensor& sensor, double rMeas, double iMeasA, double& tempOut, double& tolOut) {
    // 1. Контроль апаратних відмов (обрив / коротке замикання)
    if (rMeas <= 0.0) return RtdStatus::ShortCircuit;
    if (rMeas > 500.0 && sensor.getType() == RtdType::Pt100) return RtdStatus::OpenCircuit;

    // 2. Лінеаризація та перетворення
    RtdStatus status = rtdRToTemp(sensor, rMeas, tempOut);
    if (status != RtdStatus::Ok) {
        return status;
    }

    // 3. Розрахунок допуску
    double tolTemp = 0.0;
    getTolerance(RtdClass::A, tempOut, tolTemp);
    tolOut = tolTemp;

    return RtdStatus::Ok;
}

} // namespace Sensors
