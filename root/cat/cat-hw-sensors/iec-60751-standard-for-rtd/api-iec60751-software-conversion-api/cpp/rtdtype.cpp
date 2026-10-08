// Реалізація C++ API для конфігурації Pt100/Pt1000
#ifndef RTD_API_HPP
#define RTD_API_HPP

#include <cstdint>
#include <cstdbool>

namespace Sensors {

enum class RtdType : uint16_t {
    Pt100  = 100,
    Pt1000 = 1000
};

enum class RtdClass : uint8_t {
    AA = 0,
    A,
    B,
    C,
    Custom
};

enum class RtdStatus : uint8_t {
    Ok = 0,
    OpenCircuit,
    ShortCircuit,
    OutOfRange,
    SelfHeating,
    InvalidParam
};

struct CvdCoefficients {
    double a{3.9083e-3};
    double b{-5.775e-7};
    double c{-4.183e-12};
};

class RtdSensor {
public:
    RtdSensor(RtdType type, RtdClass accuracyClass);
    
    RtdStatus setCustomCoefficients(const CvdCoefficients& customCoeff);
    const CvdCoefficients& getCoefficients() const { return m_coeff; }
    double getR0() const { return m_r0; }
    RtdType getType() const { return m_type; }

private:
    RtdType m_type;
    RtdClass m_class;
    double m_r0;
    CvdCoefficients m_coeff;
    double m_rMin;
    double m_rMax;
};

} // namespace Sensors

#endif // RTD_API_HPP
