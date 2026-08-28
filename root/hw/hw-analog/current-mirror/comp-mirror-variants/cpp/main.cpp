#include <cmath>

// Підбір емітерного резистора джерела Відлара під заданий малий вихідний струм.
// Усе у вольтах і амперах; повертає опір в омах.
double widlar_emitter_resistor(double i_ref, double i_out)
{
    const double V_T = 0.026;                     // термічний потенціал при ~27 °C
    return (V_T * std::log(i_ref / i_out)) / i_out; // R_E = V_T·ln(I_REF/I_OUT)/I_OUT
}
// widlar_emitter_resistor(1.0e-3, 10.0e-6) -> ~12 кОм
