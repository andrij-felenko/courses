// Реалізація прямого та оберненого перетворення на мові C++
#include "rtd_api.hpp"
#include <cmath>

namespace Sensors {

RtdStatus rtdRToTemp(const RtdSensor& sensor, double rMeas, double& tempOut) {
    if (rMeas <= 0.0) return RtdStatus::ShortCircuit;

    const auto& coeff = sensor.getCoefficients();
    double r0 = sensor.getR0();
    
    double discriminant = coeff.a * coeff.a - 4.0 * coeff.b * (1.0 - rMeas / r0);
    if (discriminant < 0.0) return RtdStatus::OutOfRange;

    double temp = (-coeff.a + std::sqrt(discriminant)) / (2.0 * coeff.b);

    if (temp < 0.0) {
        for (int i = 0; i < 4; ++i) {
            double t2 = temp * temp;
            double t3 = t2 * temp;
            double f = r0 * (1.0 + coeff.a * temp + coeff.b * t2 + coeff.c * (temp - 100.0) * t3) - rMeas;
            double fPrime = r0 * (coeff.a + 2.0 * coeff.b * temp + coeff.c * (4.0 * t3 - 300.0 * t2));
            double delta = f / fPrime;
            temp -= delta;
            if (std::abs(delta) < 1e-5) break;
        }
    }

    tempOut = temp;
    return RtdStatus::Ok;
}

RtdStatus rtdTempToR(const RtdSensor& sensor, double temp, double& rOut) {
    if (temp < -200.0 || temp > 850.0) return RtdStatus::OutOfRange;

    const auto& coeff = sensor.getCoefficients();
    double r0 = sensor.getR0();

    if (temp >= 0.0) {
        rOut = r0 * (1.0 + coeff.a * temp + coeff.b * temp * temp);
    } else {
        double t2 = temp * temp;
        double t3 = t2 * temp;
        rOut = r0 * (1.0 + coeff.a * temp + coeff.b * t2 + coeff.c * (temp - 100.0) * t3);
    }

    return RtdStatus::Ok;
}

} // namespace Sensors
