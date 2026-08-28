#include <cstdint>

// Напруга на виході ідеальної R-2R лесенки для заданого коду.
// vref — опорна напруга (В); bits — розрядність (напр. 8); code — 0..2^bits-1.
double r2r_voltage(double vref, uint8_t bits, uint32_t code)
{
    uint32_t full = (uint32_t)1 << bits;   // 2^bits = число рівнів
    return vref * (double)code / (double)full;
}

// Зворотна задача: який код узяти, щоб дістати бажану напругу (з округленням).
uint32_t r2r_code(double vref, uint8_t bits, double v_target)
{
    uint32_t full = (uint32_t)1 << bits;
    double   raw  = v_target / vref * (double)full;   // дробовий «ідеальний» код
    if (raw < 0.0)         raw = 0.0;                 // не вийти за межі шкали
    if (raw > full - 1)    raw = full - 1;
    return (uint32_t)(raw + 0.5);                     // округлення до найближчого коду
}
// r2r_voltage(3.3, 8, 200) -> ~2.578 В
// r2r_code(3.3, 8, 2.578) -> 200
