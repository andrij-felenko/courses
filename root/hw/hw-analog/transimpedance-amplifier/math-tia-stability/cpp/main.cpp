#include <cmath>

constexpr float TWO_PI = 2.0f * static_cast<float>(M_PI);

struct Tia {
    float Rf;       // резистор перетворення, Ом
    float Cin;      // повна вхідна ємність (діод + ОП + монтаж), Ф
    float Cf;       // конденсатор компенсації, Ф
    float f_gbw;    // добуток підсилення на смугу ОП, Гц
};

// Частоти зламів коефіцієнта зворотного зв'язку
static float fz_of(const Tia &t) {            // нуль 1/β від вхідної ємності
    return 1.0f / (TWO_PI * t.Rf * (t.Cin + t.Cf));
}
static float fp_of(const Tia &t) {            // полюс 1/β від Cf = смуга −3 дБ
    return 1.0f / (TWO_PI * t.Rf * t.Cf);
}

// |A|·β = 1: ОП з одним домінантним полюсом має |A(f)| ≈ f_gbw / f.
// 1/β(f) на полиці прямує до (Cin+Cf)/Cf; точну криву беремо з полюса й нуля.
static float crossover_hz(const Tia &t) {
    float fz = fz_of(t), fp = fp_of(t);
    // |A(f)| = f_gbw/f;  |1/β(f)| = sqrt(1+(f/fz)^2) / sqrt(1+(f/fp)^2)
    // шукаємо f, де f_gbw/f = |1/β|, простим діленням навпіл по логарифму
    float lo = fp * 0.05f, hi = t.f_gbw;      // перетин гарантовано в цьому вікні
    for (int i = 0; i < 60; ++i) {
        float f  = std::sqrt(lo * hi);        // середина в лог-масштабі
        float A  = t.f_gbw / f;
        float ib = std::sqrt(1.0f + (f/fz)*(f/fz)) / std::sqrt(1.0f + (f/fp)*(f/fp));
        if (A > ib) lo = f; else hi = f;      // |A| ще вище за 1/β → перетин правіше
    }
    return std::sqrt(lo * hi);
}

// Запас фази (градуси) при поточному Cf
static float phase_margin_deg(const Tia &t) {
    float fz = fz_of(t), fp = fp_of(t), fc = crossover_hz(t);
    constexpr float deg = 180.0f / static_cast<float>(M_PI);
    // фаза петлі: −90° (полюс ОП) − atan(fc/fz) (нуль 1/β) + atan(fc/fp) (полюс 1/β)
    float phase = -90.0f - std::atan(fc/fz)*deg + std::atan(fc/fp)*deg;
    return 180.0f + phase;                    // запас до −180°
}

// Cf-орієнтир максимально плоского відгуку (полюс у геом. середині fz та f_gbw)
static float cf_butterworth(float Rf, float Cin, float f_gbw) {
    return std::sqrt(Cin / (TWO_PI * Rf * f_gbw));
}

// Приклад: Rf = 1 МОм, Cin = 60 пФ, f_gbw = 10 МГц
void check_example() {
    Tia t{ .Rf = 1.0e6f, .Cin = 60.0e-12f, .Cf = 0.0f, .f_gbw = 10.0e6f };
    t.Cf = cf_butterworth(t.Rf, t.Cin, t.f_gbw);   // ≈ 0.98 пФ
    float pm = phase_margin_deg(t);                // ≈ 45° — мінімально безпечно
    float bw = fp_of(t);                           // смуга −3 дБ ≈ 162 кГц
    if (pm < 45.0f) {
        // запас замалий: побільшити Cf (нижчий полюс, тихіше) або взяти швидший ОП
    }
    (void)pm; (void)bw;
}
