// Обчислення допусків та калібрування на мові C++
#include "rtd_api.hpp"
#include <cmath>

namespace Sensors {

RtdStatus getTolerance(RtdClass rtdClass, double temp, double& tolTemp) {
    double absT = std::abs(temp);
    switch (rtdClass) {
        case RtdClass::AA: tolTemp = 0.10 + 0.0017 * absT; break;
        case RtdClass::A:  tolTemp = 0.15 + 0.0020 * absT; break;
        case RtdClass::B:  tolTemp = 0.30 + 0.0050 * absT; break;
        case RtdClass::C:  tolTemp = 0.60 + 0.0100 * absT; break;
        default:           tolTemp = 0.30 + 0.0050 * absT; break;
    }
    return RtdStatus::Ok;
}

} // namespace Sensors
