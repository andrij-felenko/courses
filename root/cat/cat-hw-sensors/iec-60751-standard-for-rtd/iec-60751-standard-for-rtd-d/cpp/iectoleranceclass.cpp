#include <cmath>
#include <stdexcept>

enum class IecToleranceClass {
    ClassAA,
    ClassA,
    ClassB,
    ClassC
};

class Iec60751Tolerance {
public:
    static double getToleranceDegC(IecToleranceClass tolClass, double tempC) noexcept {
        const double absT = std::abs(tempC);
        switch (tolClass) {
            case IecToleranceClass::ClassAA: return 0.10 + 0.0017 * absT;
            case IecToleranceClass::ClassA:  return 0.15 + 0.0020 * absT;
            case IecToleranceClass::ClassB:  return 0.30 + 0.0050 * absT;
            case IecToleranceClass::ClassC:  return 0.60 + 0.0100 * absT;
        }
        return 0.0;
    }

    static bool isWithinTolerance(double measuredT, double referenceT, IecToleranceClass tolClass) noexcept {
        const double maxDev = getToleranceDegC(tolClass, referenceT);
        return std::abs(measuredT - referenceT) <= maxDev;
    }
};
