# ⚙️ Програмний модуль децибельних розрахунків, зважування A/C та обробки SPL

У цифровій обробці звукових сигналів та акустичних вимірюваннях перетворення амплітудних вибірок АЦП у фізичні рівні звукового тиску (SPL), розрахунок потужностей у dBm/dBu та частотне зважування за кривими A й C є базовими операціями аналізу шуму.

При проектуванні вбудованих шумомірів, систем моніторингу виробничого шуму та аудіопроцесорів розробник стикається з необхідністю виконувати три взаємопов'язані класи завдань: логарифмічне шкалювання сигналів, цифрову частотну корекцію (фільтрацію A/C) та часове усереднення енергії (детектування Fast/Slow).

### 1. Архітектура цифрових зважувальних фільтрів IEC 61672-1

Стандарт IEC 61672-1 описує вагову криву A через неперервну передатну функцію в s-області з чотирма нулями у початку координат та шістьма полюсами (два на низьких частотах 20.6 Гц, два проміжних на 107.7 Гц та 737.9 Гц, і два високочастотних на 12.194 кГц).

Для вагового фільтра C передатна функція має спрощений вигляд лише з чотирма полюсами (два на 20.6 Гц та два на 12.194 кГц), що забезпечує практично пласку амплітудно-частотну характеристику в діапазоні від 63 Гц до 4 кГц.

Для реалізації цих фільтрів у цифровій формі на фіксованій частоті дискретизації `fs` застосовується білінійне z-перетворення:

```
s = 2 · fs · (1 − z⁻¹) / (1 + z⁻¹)
```

Отриманий цифровий фільтр розкладається на каскад із послідовних біквадратних ланок (секцій другого порядку, Biquad). Для забезпечення максимальної числової стійкості та мінімізації похибок округлення обрано транспоновану пряму форму II (Direct Form II Transposed).

Перевага транспонованої форми II полягає в тому, що її внутрішні змінні стану `s1` та `s2` оновлюються за допомогою інтегруючих акумуляторів, що запобігає переповненню розрядної сітки під час обробки сигналів із високою амплітудою низькочастотних складових.

Рівняння різницевої схеми кожної біквадратної секції мають вигляд:

```
y[n] = b0 · x[n] + s1[n−1]
s1[n] = b1 · x[n] − a1 · y[n] + s2[n−1]
s2[n] = b2 · x[n] − a2 · y[n]
```

### 2. Часові характеристики шумоміра: детектування Fast, Slow та Leq

Звуковий тиск нестаціонарних шумів постійно коливається в часі. Для отримання стабільного числового значення рівня шуму стандарт IEC 61672-1 визначає експоненційне часове зважування квадрата тиску:

```
p_w²(t) = (1 / τ) · ∫ p²(ξ) · e^( −(t − ξ) / τ ) dξ
```

Стандарт регламентує дві основні часові сталі інтегрування:
1. **Fast (швидко, `τ = 125 мс`):** реагує на швидкі зміни гучності, короткочасні сплески та окремі слова мовлення;
2. **Slow (повільно, `τ = 1000 мс = 1 с`):** згладжує випадкові пульсації та призначена для оцінки сталого фонового шуму приміщень чи технологічного обладнання.

У цифровій дискретній формі з кроком оновлення `Δt = 1 / fs` експоненційний інтегратор реалізується як рекурсивний фільтр першого порядку (IIR Leaky Integrator):

```
α = 1 − e^( −1 / (fs · τ) )
P_sq[n] = (1 − α) · P_sq[n−1] + α · x²[n]
```

Для інтегральної оцінки загальної дози акустичного навантаження за тривалий проміжок часу `T` (наприклад, 8-годинна робоча зміна) використовується **еквівалентний рівень звуку Leq** (англ. *Equivalent Continuous Sound Level*), що розраховується як лінійне середнє енергії без експоненційного згасання:

```
L_eq = 10 · log₁₀( (1 / N) · ∑ ( p²[n] / p₀² ) )
```

### 3. Швидкі наближення логарифма для мікроконтролерів без FPU

На молодших мікроконтролерах (наприклад, ARM Cortex-M0/M0+/M3) виконання стандартної бібліотечної функції `log10()` подвійної або одинарної точності вимагає сотень або тисяч тактів процесора через програмну емуляцію плаваючої коми.

Для оптимізації потокових розрахунків застосовується апаратна інструкція підрахунку провідних нулів `CLZ` (англ. *Count Leading Zeros*), яка підтримується архітектурами ARM та RISC-V:

1. Двійковий порядок цілого числа `X` визначається як `E = 31 − CLZ(X)`;
2. Нормалізована мантиса апроксимується кусково-лінійним або сплайновим поліномом;
3. Десятковий логарифм отримується множенням двійкового логарифма на модуль переходу `log₁₀(2) ≈ 0.30102999566`:

```
log₁₀(X) = log₂(X) · log₁₀(2) ≈ ( E + Mantissa_frac ) · 0.30103
```

Такий підхід скорочує час обчислення рівня одного енергетичного блоку вибірок до 5–10 тактових циклів, зберігаючи похибку розрахунку децибелів у межах `±0.05 дБ`.

### 4. Калібрування та перерахунок вибірок цифрового мікрофона

Сучасні цифрові MEMS-мікрофони з інтерфейсом I2S або PDM видають нормалізовані цілочисельні або дробові вибірки у діапазоні від `-1.0` до `+1.0` (шкала повної цифрової амплітуди FS, Full Scale). Чутливість таких мікрофонів у технічній документації вказується у децибелах відносно повної шкали при дії стандартного акустичного тиску калібратора `p = 1.0 Па` (що відповідає 94.0 дБ SPL на частоті 1 кГц), наприклад, `S = −26 dBFS/Pa`.

Для перетворення амплітуди цифрового сигналу `x` у фізичний тиск у Паскалях використовується формула:

```
V_fs = 10^( S_dBFS / 20 )
p_Pa(t) = x(t) / V_fs
```

Для чутливості `-26 dBFS` коефіцієнт становить `V_fs = 10^(−26/20) ≈ 0.05012`. Отже, вибірка з амплітудою `0.05012` відповідає миттєвому тиску `1.0 Па`.

### 5. Програмна реалізація модулів на C та C++

Нижче наведено бібліотеку акустичних та радіотехнічних логарифмічних розрахунків: мовою C99 для систем реального часу та вбудованих мікроконтролерів і мовою C++20 із застосуванням сучасних стандартних концепцій, безпечних масивів `std::span` та об'єктно-орієнтованих фільтрів.

:::tabs
```c
/* decibel_dsp.h — Акустичні та логарифмічні розрахунки на C99 */
#ifndef DECIBEL_DSP_H
#define DECIBEL_DSP_H

#include <math.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define DB_P0_AIR_PA       20.0e-6       /* Опорний тиск у повітрі: 20 мкПа */
#define DB_I0_AIR_W_M2     1.0e-12       /* Опорна інтенсивність: 1 пВт/м² */
#define DB_V0_DBU          0.7745966692  /* Опорна напруга 0 dBu (600 Ом, 1 мВт) */
#define DB_V0_DBV          1.0           /* Опорна напруга 0 dBV: 1.0 В */
#define DB_P0_DBM_W        1.0e-3        /* Опорна потужність 0 dBm: 1 мВт */

/* Часові константи детектора (секунди) */
#define DB_TIME_CONST_FAST 0.125         /* Fast: 125 мс */
#define DB_TIME_CONST_SLOW 1.000         /* Slow: 1000 мс */

/* Структура біквадратного цифрового фільтра Direct Form II Transposed */
typedef struct {
    double b0, b1, b2;
    double a1, a2;
    double s1, s2;
} biquad_filter_t;

/* Каскад зважувального фільтра A-weighting (3 біквадрати для fs = 48 кГц) */
typedef struct {
    biquad_filter_t stages[3];
} a_weighting_filter_t;

/* Структура детектора часового усереднення (Fast / Slow) */
typedef struct {
    double alpha;
    double mean_square;
} time_weighting_detector_t;

/* Базові логарифмічні перетворення */
static inline double db_from_power_ratio(double p, double p0) {
    if (p <= 0.0 || p0 <= 0.0) return -INFINITY;
    return 10.0 * log10(p / p0);
}

static inline double db_from_voltage_ratio(double v, double v0) {
    if (v <= 0.0 || v0 <= 0.0) return -INFINITY;
    return 20.0 * log10(v / v0);
}

static inline double power_ratio_from_db(double db) {
    return pow(10.0, db / 10.0);
}

static inline double voltage_ratio_from_db(double db) {
    return pow(10.0, db / 20.0);
}

/* Опорні шкали електроніки та радіотехніки */
static inline double voltage_to_dbu(double v_rms) {
    return db_from_voltage_ratio(v_rms, DB_V0_DBU);
}

static inline double dbu_to_voltage(double dbu) {
    return DB_V0_DBU * voltage_ratio_from_db(dbu);
}

static inline double voltage_to_dbv(double v_rms) {
    return db_from_voltage_ratio(v_rms, DB_V0_DBV);
}

static inline double dbv_to_voltage(double dbv) {
    return DB_V0_DBV * voltage_ratio_from_db(dbv);
}

static inline double power_to_dbm(double power_watts) {
    return db_from_power_ratio(power_watts, DB_P0_DBM_W);
}

static inline double dbm_to_power(double dbm) {
    return DB_P0_DBM_W * power_ratio_from_db(dbm);
}

static inline double voltage_to_dbm(double v_rms, double load_ohms) {
    if (load_ohms <= 0.0 || v_rms <= 0.0) return -INFINITY;
    double p_watts = (v_rms * v_rms) / load_ohms;
    return power_to_dbm(p_watts);
}

/* Акустичні розрахунки SPL */
static inline double pressure_to_spl(double p_rms_pa) {
    return db_from_voltage_ratio(p_rms_pa, DB_P0_AIR_PA);
}

static inline double spl_to_pressure(double spl_db) {
    return DB_P0_AIR_PA * voltage_ratio_from_db(spl_db);
}

/* Швидке наближення двійкового логарифма для цілих 32-бітних чисел */
static inline float fast_log2_u32(uint32_t val) {
    if (val == 0) return -128.0f;
    int clz = __builtin_clz(val);
    int exp = 31 - clz;
    float frac = (float)(val - (1u << exp)) / (float)(1u << exp);
    return (float)exp + (frac * (1.442695f - 0.442695f * frac));
}

static inline float fast_log10_u32(uint32_t val) {
    return fast_log2_u32(val) * 0.30102999566f;
}

/* Енергетичне підсумовування некогерентних джерел */
static inline double sum_noncoherent_spl(const double *levels_db, size_t count) {
    if (count == 0) return -INFINITY;
    double sum_linear = 0.0;
    for (size_t i = 0; i < count; ++i) {
        sum_linear += pow(10.0, levels_db[i] / 10.0);
    }
    return 10.0 * log10(sum_linear);
}

/* Розрахунок RMS та SPL за масивом вибірок тиску */
static inline double calculate_rms(const double *samples, size_t count) {
    if (count == 0) return 0.0;
    double sum_sq = 0.0;
    for (size_t i = 0; i < count; ++i) {
        sum_sq += samples[i] * samples[i];
    }
    return sqrt(sum_sq / (double)count);
}

/* Ініціалізація A-weighting фільтра для частоти дискретизації fs = 48 кГц */
static inline void a_weighting_init_48k(a_weighting_filter_t *f) {
    f->stages[0].b0 = 0.169994948147430;
    f->stages[0].b1 = 0.339989896294859;
    f->stages[0].b2 = 0.169994948147430;
    f->stages[0].a1 = -0.270409810398048;
    f->stages[0].a2 = -0.050478631380962;
    f->stages[0].s1 = 0.0;
    f->stages[0].s2 = 0.0;

    f->stages[1].b0 = 1.0;
    f->stages[1].b1 = -2.0;
    f->stages[1].b2 = 1.0;
    f->stages[1].a1 = -1.990047454833980;
    f->stages[1].a2 = 0.990072166948332;
    f->stages[1].s1 = 0.0;
    f->stages[1].s2 = 0.0;

    f->stages[2].b0 = 1.0;
    f->stages[2].b1 = 2.0;
    f->stages[2].b2 = 1.0;
    f->stages[2].a1 = -0.485685718742828;
    f->stages[2].a2 = 0.000000000000000;
    f->stages[2].s1 = 0.0;
    f->stages[2].s2 = 0.0;
}

/* Фільтрація однієї вибірки через A-weighting */
static inline double a_weighting_process_sample(a_weighting_filter_t *f, double in) {
    double x = in;
    for (int i = 0; i < 3; ++i) {
        biquad_filter_t *st = &f->stages[i];
        double out = st->b0 * x + st->s1;
        st->s1 = st->b1 * x - st->a1 * out + st->s2;
        st->s2 = st->b2 * x - st->a2 * out;
        x = out;
    }
    return x;
}

/* Ініціалізація детектора часового зважування Fast/Slow */
static inline void time_detector_init(time_weighting_detector_t *det, double tau_sec, double fs_hz) {
    det->alpha = 1.0 - exp(-1.0 / (fs_hz * tau_sec));
    det->mean_square = 0.0;
}

/* Оновлення детектора часового зважування однією вибіркою тиску (Па) */
static inline double time_detector_update(time_weighting_detector_t *det, double sample_pa) {
    double x2 = sample_pa * sample_pa;
    det->mean_square = (1.0 - det->alpha) * det->mean_square + det->alpha * x2;
    double p_rms = sqrt(det->mean_square);
    return pressure_to_spl(p_rms);
}

#endif /* DECIBEL_DSP_H */
```
```cpp
// decibel_dsp.hpp — Ідіоматична C++ бібліотека акустичних перетворень (C++20)
#pragma once

#include <bit>
#include <cmath>
#include <concepts>
#include <numbers>
#include <numeric>
#include <span>
#include <vector>

namespace dsp::acoustics {

// Опорні фізичні константи
inline constexpr double p0_air_pa       = 20.0e-6;      // Опорний звуковий тиск: 20 мкПа
inline constexpr double i0_air_w_m2     = 1.0e-12;      // Опорна інтенсивність: 1 пВт/м²
inline constexpr double v0_dbu          = 0.7745966692; // 0 dBu: 0.7746 В на 600 Ом
inline constexpr double v0_dbv          = 1.0;          // 0 dBV: строго 1.0 В RMS
inline constexpr double p0_dbm_watts    = 1.0e-3;       // 0 dBm: 1 мВт

// Часові константи детектора (секунди)
inline constexpr double tau_fast_sec    = 0.125;        // Fast: 125 мс
inline constexpr double tau_slow_sec    = 1.000;        // Slow: 1000 мс

// Базові логарифмічні функції
[[nodiscard]] constexpr double to_db_power(double p, double p0 = 1.0) noexcept {
    if (p <= 0.0 || p0 <= 0.0) {
        return -std::numeric_limits<double>::infinity();
    }
    return 10.0 * std::log10(p / p0);
}

[[nodiscard]] constexpr double to_db_amplitude(double v, double v0 = 1.0) noexcept {
    if (v <= 0.0 || v0 <= 0.0) {
        return -std::numeric_limits<double>::infinity();
    }
    return 20.0 * std::log10(v / v0);
}

[[nodiscard]] constexpr double from_db_power(double db) noexcept {
    return std::pow(10.0, db / 10.0);
}

[[nodiscard]] constexpr double from_db_amplitude(double db) noexcept {
    return std::pow(10.0, db / 20.0);
}

// Електричні опорні величини
[[nodiscard]] constexpr double voltage_to_dbu(double v_rms) noexcept {
    return to_db_amplitude(v_rms, v0_dbu);
}

[[nodiscard]] constexpr double dbu_to_voltage(double dbu) noexcept {
    return v0_dbu * from_db_amplitude(dbu);
}

[[nodiscard]] constexpr double voltage_to_dbv(double v_rms) noexcept {
    return to_db_amplitude(v_rms, v0_dbv);
}

[[nodiscard]] constexpr double dbv_to_voltage(double dbv) noexcept {
    return v0_dbv * from_db_amplitude(dbv);
}

[[nodiscard]] constexpr double power_to_dbm(double power_watts) noexcept {
    return to_db_power(power_watts, p0_dbm_watts);
}

[[nodiscard]] constexpr double dbm_to_power(double dbm) noexcept {
    return p0_dbm_watts * from_db_power(dbm);
}

[[nodiscard]] constexpr double voltage_to_dbm(double v_rms, double load_ohms) noexcept {
    if (load_ohms <= 0.0 || v_rms <= 0.0) {
        return -std::numeric_limits<double>::infinity();
    }
    const double p_watts = (v_rms * v_rms) / load_ohms;
    return power_to_dbm(p_watts);
}

// Акустичні розрахунки звукового тиску
[[nodiscard]] constexpr double pressure_to_spl(double p_rms_pa) noexcept {
    return to_db_amplitude(p_rms_pa, p0_air_pa);
}

[[nodiscard]] constexpr double spl_to_pressure(double spl_db) noexcept {
    return p0_air_pa * from_db_amplitude(spl_db);
}

// Швидке наближення двійкового та десяткового логарифмів (C++20 std::countl_zero)
[[nodiscard]] constexpr float fast_log2(uint32_t val) noexcept {
    if (val == 0) return -128.0f;
    const int clz = std::countl_zero(val);
    const int exp = 31 - clz;
    const float frac = static_cast<float>(val - (1u << exp)) / static_cast<float>(1u << exp);
    return static_cast<float>(exp) + (frac * (1.442695f - 0.442695f * frac));
}

[[nodiscard]] constexpr float fast_log10(uint32_t val) noexcept {
    return fast_log2(val) * 0.30102999566f;
}

// Енергетичне підсумовування некогерентних джерел звуку
[[nodiscard]] inline double sum_noncoherent_spl(std::span<const double> levels_db) noexcept {
    if (levels_db.empty()) {
        return -std::numeric_limits<double>::infinity();
    }
    const double sum_linear = std::accumulate(
        levels_db.begin(), levels_db.end(), 0.0,
        [](double acc, double db) noexcept {
            return acc + std::pow(10.0, db / 10.0);
        });
    return 10.0 * std::log10(sum_linear);
}

// Розрахунок середньоквадратичного значення (RMS)
[[nodiscard]] inline double calculate_rms(std::span<const double> samples) noexcept {
    if (samples.empty()) return 0.0;
    const double sum_sq = std::accumulate(
        samples.begin(), samples.end(), 0.0,
        [](double acc, double s) noexcept {
            return acc + s * s;
        });
    return std::sqrt(sum_sq / static_cast<double>(samples.size()));
}

// Цифровий біквадратний фільтр (Direct Form II Transposed)
class BiquadFilter {
public:
    constexpr BiquadFilter(double b0, double b1, double b2, double a1, double a2) noexcept
        : b0_{b0}, b1_{b1}, b2_{b2}, a1_{a1}, a2_{a2} {}

    constexpr void reset() noexcept {
        s1_ = 0.0;
        s2_ = 0.0;
    }

    [[nodiscard]] constexpr double process(double in) noexcept {
        const double out = b0_ * in + s1_;
        s1_ = b1_ * in - a1_ * out + s2_;
        s2_ = b2_ * in - a2_ * out;
        return out;
    }

private:
    double b0_, b1_, b2_;
    double a1_, a2_;
    double s1_{0.0};
    double s2_{0.0};
};

// Каскадний A-weighting фільтр за стандартом IEC 61672-1 (fs = 48 кГц)
class AWeightingFilter {
public:
    AWeightingFilter() noexcept {
        stages_.emplace_back(0.169994948147430, 0.339989896294859, 0.169994948147430,
                            -0.270409810398048, -0.050478631380962);
        stages_.emplace_back(1.0, -2.0, 1.0,
                            -1.990047454833980, 0.990072166948332);
        stages_.emplace_back(1.0, 2.0, 1.0,
                            -0.485685718742828, 0.0);
    }

    void reset() noexcept {
        for (auto& stage : stages_) {
            stage.reset();
        }
    }

    [[nodiscard]] double process(double sample) noexcept {
        double current = sample;
        for (auto& stage : stages_) {
            current = stage.process(current);
        }
        return current;
    }

    void process_buffer(std::span<const double> input, std::span<double> output) noexcept {
        const size_t n = std::min(input.size(), output.size());
        for (size_t i = 0; i < n; ++i) {
            output[i] = process(input[i]);
        }
    }

private:
    std::vector<BiquadFilter> stages_;
};

// Детектор експоненційного часового зважування (Fast / Slow)
class TimeWeightingDetector {
public:
    TimeWeightingDetector(double tau_sec, double fs_hz) noexcept
        : alpha_{1.0 - std::exp(-1.0 / (fs_hz * tau_sec))} {}

    void reset() noexcept {
        mean_square_ = 0.0;
    }

    [[nodiscard]] double update(double sample_pa) noexcept {
        const double x2 = sample_pa * sample_pa;
        mean_square_ = (1.0 - alpha_) * mean_square_ + alpha_ * x2;
        const double p_rms = std::sqrt(mean_square_);
        return pressure_to_spl(p_rms);
    }

private:
    double alpha_;
    double mean_square_{0.0};
};

} // namespace dsp::acoustics
```
:::

### 6. Верифікаційний стенд та тестування на еталонних сигналах

Для перевірки коректності фільтрації та обчислення рівнів створено тестову програму, яка генерує калібрувальний синусоїдальний сигнал частотою 1000 Гц із середньоквадратичним звуковим тиском `1.0 Па` (94.00 дБ SPL) та низькочастотний тон 100 Гц.

Згідно зі стандартом IEC 61672-1, на частоті 1 кГц фільтр A-weighting повинен давати нульове ослаблення (`0.0 дБ`), а на частоті 100 Гц — ослаблення на `-19.1 дБ`.

:::tabs
```c
#include "decibel_dsp.h"
#include <stdio.h>

int main(void) {
    printf("=== Перевірка модуля акустичних перетворень (C99) ===\n\n");

    /* 1. Перевірка калібратора 94 дБ SPL (1.0 Па) */
    double p_cal = 1.0; /* 1.0 Па RMS */
    double spl_cal = pressure_to_spl(p_cal);
    printf("Акустичний калібратор: тиск = %.3f Па -> SPL = %.2f дБ (очікується 94.00 дБ)\n", p_cal, spl_cal);

    /* 2. Перевірка опорних напруг dBu та dBV */
    printf("+4 dBu (студійний стандарт) = %.4f В RMS\n", dbu_to_voltage(4.0));
    printf("-10 dBV (побутовий стандарт) = %.4f В RMS (%.2f dBu)\n", 
           dbv_to_voltage(-10.0), voltage_to_dbu(dbv_to_voltage(-10.0)));

    /* 3. Некогерентне підсумовування двох джерел по 80 дБ */
    double sources[2] = {80.0, 80.0};
    double total_80 = sum_noncoherent_spl(sources, 2);
    printf("Сума 80 дБ + 80 дБ = %.2f дБ (очікується 83.01 дБ)\n", total_80);

    /* 4. Тестування фільтрації A-weighting на частоті 1 кГц */
    a_weighting_filter_t a_flt;
    a_weighting_init_48k(&a_flt);

    const size_t N = 48000; /* 1 секунда при fs = 48 кГц */
    double sig_1k[N], out_1k[N];
    for (size_t i = 0; i < N; ++i) {
        sig_1k[i] = sqrt(2.0) * 1.0 * sin(2.0 * M_PI * 1000.0 * (double)i / 48000.0);
        out_1k[i] = a_weighting_process_sample(&a_flt, sig_1k[i]);
    }
    double rms_in_1k = calculate_rms(&sig_1k[4800], N - 4800);
    double rms_out_1k = calculate_rms(&out_1k[4800], N - 4800);
    printf("A-зважування на 1 кГц: Вхід RMS = %.3f Па, Вихід RMS = %.3f Па (Зсув = %+.2f дБ)\n",
           rms_in_1k, rms_out_1k, db_from_voltage_ratio(rms_out_1k, rms_in_1k));

    /* 5. Перевірка швидкого цілочисельного логарифма */
    uint32_t test_val = 1000000;
    printf("Fast log10(1000000) = %.4f (точне значення: 6.0000)\n", fast_log10_u32(test_val));

    return 0;
}
```
```cpp
#include "decibel_dsp.hpp"
#include <iostream>
#include <vector>
#include <numbers>

int main() {
    using namespace dsp::acoustics;
    std::cout << "=== Перевірка модуля акустичних перетворень (C++20) ===\n\n";

    // 1. Перевірка калібратора 94 дБ SPL (1.0 Па)
    constexpr double p_cal = 1.0; // 1.0 Па RMS
    const double spl_cal = pressure_to_spl(p_cal);
    std::cout << "Акустичний калібратор: тиск = " << p_cal 
              << " Па -> SPL = " << spl_cal << " дБ (очікується 94.00 дБ)\n";

    // 2. Перевірка опорних напруг dBu та dBV
    std::cout << "+4 dBu (студійний стандарт) = " << dbu_to_voltage(4.0) << " В RMS\n";
    std::cout << "-10 dBV (побутовий стандарт) = " << dbv_to_voltage(-10.0) 
              << " В RMS (" << voltage_to_dbu(dbv_to_voltage(-10.0)) << " dBu)\n";

    // 3. Некогерентне підсумовування двох джерел по 80 дБ
    const std::vector<double> sources = {80.0, 80.0};
    std::cout << "Сума 80 дБ + 80 дБ = " << sum_noncoherent_spl(sources) 
              << " дБ (очікується 83.01 дБ)\n";

    // 4. Тестування фільтрації A-weighting на частоті 1 кГц
    AWeightingFilter filter;
    constexpr size_t fs = 48000;
    constexpr size_t num_samples = fs; // 1 секунда
    std::vector<double> sig_1k(num_samples);
    std::vector<double> out_1k(num_samples);

    for (size_t i = 0; i < num_samples; ++i) {
        sig_1k[i] = std::sqrt(2.0) * 1.0 * std::sin(2.0 * std::numbers::pi * 1000.0 * static_cast<double>(i) / fs);
    }
    filter.process_buffer(sig_1k, out_1k);

    std::span<const double> in_span{sig_1k.data() + 4800, num_samples - 4800};
    std::span<const double> out_span{out_1k.data() + 4800, num_samples - 4800};
    const double rms_in = calculate_rms(in_span);
    const double rms_out = calculate_rms(out_span);

    std::cout << "A-зважування на 1 кГц: Вхід RMS = " << rms_in 
              << " Па, Вихід RMS = " << rms_out 
              << " Па (Зсув = " << to_db_amplitude(rms_out, rms_in) << " дБ)\n";

    // 5. Перевірка швидкого логарифма
    constexpr uint32_t test_val = 1000000;
    std::cout << "Fast log10(1000000) = " << fast_log10(test_val) 
              << " (точне значення: 6.0000)\n";

    return 0;
}
```
:::
