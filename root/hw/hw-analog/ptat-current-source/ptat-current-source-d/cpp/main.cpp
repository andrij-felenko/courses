#include <cmath>

// Тепловий потенціал k*T/q при заданій абсолютній температурі (К), у вольтах.
double thermal_voltage(double T_kelvin)
{
    constexpr double k = 1.380649e-23;   // стала Больцмана, Дж/К
    constexpr double q = 1.602177e-19;   // заряд електрона, Кл
    return k * T_kelvin / q;             // U_T = k*T/q
}

// PTAT-струм ΔU_BE-джерела: I = U_T*ln(N)/R.
// N — відношення площ переходів, R — резистор у емітері (Ом).
double ptat_current(double T_kelvin, double N, double R_ohm)
{
    double u_t = thermal_voltage(T_kelvin);
    return u_t * std::log(N) / R_ohm;    // ∝ T, бо U_T ∝ T
}
// ptat_current(300.0, 8.0, 5400.0) -> ~9.96 мкА при 300 K (27 °C)
// ptat_current(398.0, 8.0, 5400.0) -> ~13.2 мкА при 398 K (125 °C)
