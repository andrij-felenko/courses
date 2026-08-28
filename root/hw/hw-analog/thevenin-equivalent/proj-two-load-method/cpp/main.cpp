#include <cstdint>

// заглушки під вашу платформу:
extern std::uint16_t adc_read_raw();          // один сирий відлік АЦП
extern void          load_select(std::uint8_t n); // 1 → R1, 2 → R2, 0 → відключити
extern void          delay_ms(std::uint32_t ms);

struct Thevenin { float vth; float rth; };

namespace {
    constexpr float R1_OHM   = 10.0f;    // легке навантаження, Ом
    constexpr float R2_OHM   = 2.7f;     // важче навантаження, Ом
    constexpr float ADC_VREF = 3.30f;    // опорна напруга АЦП, В
    constexpr float ADC_MAX  = 4095.0f;  // 12-бітний АЦП
    constexpr std::uint32_t SETTLE_MS = 50;  // пауза на встановлення після перемикання
    constexpr std::uint8_t  N_AVG     = 16;  // скільки відліків усереднити

    // усереднене читання напруги на клемах (у вольтах)
    float read_terminal_v() {
        std::uint32_t acc = 0;
        for (std::uint8_t i = 0; i < N_AVG; ++i)
            acc += adc_read_raw();
        return (static_cast<float>(acc) / N_AVG) * (ADC_VREF / ADC_MAX);
    }
}

Thevenin measure_thevenin() {
    load_select(1);                 // легке навантаження
    delay_ms(SETTLE_MS);            // дочекатися встановлення
    const float v1 = read_terminal_v();
    const float i1 = v1 / R1_OHM;

    load_select(2);                 // важче навантаження
    delay_ms(SETTLE_MS);
    const float v2 = read_terminal_v();
    const float i2 = v2 / R2_OHM;

    load_select(0);                 // зняти навантаження — не гріти джерело

    Thevenin r;
    r.rth = (v1 - v2) / (i2 - i1);  // нахил прямої = внутрішній опір
    r.vth = v1 + i1 * r.rth;        // екстраполяція до I = 0
    return r;
}
