#include <cstdint>
#include <cmath>

namespace {
    constexpr float R1_OHM   = 10.0f;    // легке навантаження, Ом
    constexpr float R2_OHM   = 2.7f;     // важче навантаження, Ом
    constexpr float ADC_VREF = 3.30f;    // опорна напруга АЦП, В
    constexpr float ADC_MAX  = 4095.0f;  // 12-бітний АЦП
    constexpr float ADC_GAIN = 11.0f;    // подільник входу: 10:1 (1+10k/1k) → діапазон до ~36 В
    constexpr std::uint32_t SETTLE_MS = 50;    // пауза на встановлення після перемикання
    constexpr std::uint8_t  N_AVG     = 32;    // скільки відліків усереднити
    constexpr float MIN_DI_A = 0.10f;    // мінімальна різниця струмів (інакше шум з'їсть знаменник)
}

enum class NortonStatus {          // результат вимірювання
    Ok,
    ErrDiTooSmall,                 // I₂−I₁ потонуло в шумі — точки замалі різні
    ErrNonlinear                   // R_n вийшов від'ємним/безглуздим
};

struct Norton {
    float i_n = 0.0f;              // струм Нортона (струм КЗ), А — дістаний екстраполяцією
    float r_n = 0.0f;             // опір Нортона (= R_th), Ом
    float v_oc = 0.0f;            // напруга холостого ходу, В — проміжне число
    NortonStatus status = NortonStatus::Ok;
};

// заглушки під вашу платформу:
extern std::uint16_t adc_read_raw();            // один сирий відлік АЦП
extern void          load_select(std::uint8_t n); // 1 → R1, 2 → R2, 0 → відключити геть
extern void          delay_ms(std::uint32_t ms);

// усереднене читання напруги на клемах (у вольтах), з урахуванням подільника входу
static float read_terminal_v() {
    std::uint32_t acc = 0;
    for (std::uint8_t i = 0; i < N_AVG; ++i)
        acc += adc_read_raw();
    const float v_adc = (static_cast<float>(acc) / N_AVG) * (ADC_VREF / ADC_MAX);
    return v_adc * ADC_GAIN;            // назад до напруги на клемах
}

// зняти одну точку (I, V) під заданим навантаженням
static void measure_point(std::uint8_t load, float r_ohm, float &v, float &i) {
    load_select(load);                  // під'єднати навантаження ключем
    delay_ms(SETTLE_MS);                // дочекатися сталого рівня
    v = read_terminal_v();
    i = v / r_ohm;                      // струм точки — навантаження ж відоме
}

Norton measure_norton() {
    Norton out;

    float v1, i1, v2, i2;
    measure_point(1, R1_OHM, v1, i1);   // легке навантаження → мала просадка
    measure_point(2, R2_OHM, v2, i2);   // важче навантаження → більша просадка
    load_select(0);                     // зняти навантаження — не гріти джерело!

    // запобіжник №1: точки мають давати ДОСИТЬ різні струми,
    // інакше знаменник (i2 − i1) тоне в шумі АЦП і R_n стрибає в безглуздя.
    if (std::fabs(i2 - i1) < MIN_DI_A) {
        out.status = NortonStatus::ErrDiTooSmall;
        return out;                     // повторити з помітніше різними навантаженнями
    }

    out.r_n  = (v1 - v2) / (i2 - i1);   // нахил прямої = внутрішній опір
    out.v_oc = v1 + i1 * out.r_n;       // екстраполяція вліво, до I = 0

    // запобіжник №2: на справді лінійному джерелі R_n > 0; від'ємний/нуль —
    // ознака грубого збою (переплутані навантаження, шум, нелінійність).
    if (out.r_n <= 0.0f) {
        out.status = NortonStatus::ErrNonlinear;
        return out;
    }

    out.i_n  = out.v_oc / out.r_n;      // екстраполяція вправо, до V = 0 → струм КЗ
    out.status = NortonStatus::Ok;
    return out;
}
