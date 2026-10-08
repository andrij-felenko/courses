#include <cmath>
#include <stdexcept>

namespace rtd {

/**
 * @brief Клас для розрахунку параметрів збудження та похибок платинових RTD.
 */
class RtdExcitationOptimizer {
public:
    static constexpr double AlphaIEC = 0.003851; // Температурний коефіцієнт IEC 60751

    /**
     * @brief Обчислює максимальний струм збудження для збереження похибки самонагріву у заданих межах.
     */
    static double calculateMaxCurrent(double nominalR0, 
                                      double maxTemperatureC, 
                                      double allowedSelfHeatingErrC, 
                                      double dissipationFactorMwPerC) 
    {
        if (nominalR0 <= 0.0 || dissipationFactorMwPerC <= 0.0 || allowedSelfHeatingErrC <= 0.0) {
            throw std::invalid_argument("Параметри RTD повинні бути додатними числами.");
        }

        double estimatedResistance = nominalR0 * (1.0 + AlphaIEC * maxTemperatureC);
        double dissipationWattsPerC = dissipationFactorMwPerC * 1e-3;
        double maxPowerWatts = allowedSelfHeatingErrC * dissipationWattsPerC;

        return std::sqrt(maxPowerWatts / estimatedResistance);
    }
};

} // namespace rtd
