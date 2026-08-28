#include <cstdint>

// Внесок одного біта k у вихід ідеальної R-2R лесенки (режим напруги).
// k = 0 — молодший біт, k = bits-1 — старший. Вага = Vref / 2^(bits - k).
double r2r_bit_weight(double vref, uint8_t bits, uint8_t k)
{
    uint8_t shift = (uint8_t)(bits - k);     // N - k
    return vref / (double)((uint32_t)1 << shift);
}

// Вихід через суму ваг увімкнених бітів — пряме втілення суперпозиції.
// Має збігтися з компактною формулою vref*code/2^bits до похибки double.
double r2r_voltage_by_bits(double vref, uint8_t bits, uint32_t code)
{
    double v = 0.0;
    for (uint8_t k = 0; k < bits; ++k)
        if (code & ((uint32_t)1 << k))       // біт k увімкнений?
            v += r2r_bit_weight(vref, bits, k);
    return v;
}

// Та сама величина одним множенням — те, що довели на крокax 7-8.
double r2r_voltage(double vref, uint8_t bits, uint32_t code)
{
    return vref * (double)code / (double)((uint32_t)1 << bits);
}
// r2r_voltage_by_bits(3.3, 8, 200) -> ~2.578 В  (1.650 + 0.825 + 0.103)
// r2r_voltage       (3.3, 8, 200) -> ~2.578 В
