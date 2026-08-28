# ⚙️ Програмна реалізація конвеєра калібрування магнітометра: просторове розбиття, розв'язувач та збереження у Flash

<preknowlist>
- [Підгонка еліпсоїда за Ферше та Levenberg-Marquardt](root:embedded/kalibruvannia-kompasa-na-zibranomu-aparati/math-ferschee-ellipsoid-fit.md) — математична модель матричного перетворення та виведення якобіана.
- [Матриці як дії](root:math-algebra/matrices-as-operations) — операції множення матриці на вектор, обернення матриць 3×3 та розв'язання лінійних систем.
- [Пам'ять без купи](root:embedded/pamiat-bez-kupy) — проектування детермінованих алгоритмів реального часу без динамічного виділення пам'яті.
</preknowlist>

Для впровадження процедури калібрування магнітометра на бортовому мікроконтролері польотного контролера (наприклад, STM32H7, STM32F4 або ESP32-S3) недостатньо просто реалізувати математичний розв'язувач. У реальній системі керування виникає комплекс жорстких інженерних обмежень:
1. **Детермінізм пам'яті:** повна заборона динамічного виділення пам'яті (`malloc`/`free` або `new`/`delete`) під час виконання калібрувального циклу для усунення фрагментації купи та виключення помилок `HardFault` в авіоніці.
2. **Фільтрація динамічних спотворень:** відсіювання вимірів, знятих під час різких поштовхів, ривків чи надвисоких кутових швидкостей (`|ω| > 100°/с`), коли затримки цифрових фільтрів АЦП вносять фазовий зсув.
3. **Просторове квотування (Spatial Binning):** розбиття уявної одиничної сфери на 72 рівновеликі сектори для запобігання перекосу ваги точок у бік випадково затриманих просторових положень.
4. **Стійкий чисельний розв'язувач:** 9-параметричний оптимізатор Левенберга — Марквардта з адаптивною регуляризацією та прямим розв'язанням нормальних рівнянь методом Гаусса з вибором головного елемента.
5. **Контроль цілісності у Flash:** збереження калібрувальної структури з контрольною сумою CRC32 та автоматичною верифікацією при кожному старті польотного контролера.

---

## 1. Архітектура конвеєра збору та обробки даних

Конвеєр калібрування функціонує як скінченний автомат із чотирма станами: `IDLE` (очікування), `COLLECTING` (накопичення просторової хмари), `SOLVING` (чисельна оптимізація) та `VALIDATING` (контроль якості).

```
   ┌───────────┐      Старт калібрування      ┌───────────────┐
   │   IDLE    ├─────────────────────────────►│  COLLECTING   │
   └───────────┘                              └───┬───────▲───┘
                                                  │       │
                                     Покриття >=  │       │ Нові виміри з
                                     60% секторів │       │ фільтрацією ω
                                                  ▼       │
   ┌───────────┐       RMS > 3.0 мкТл         ┌───────────┴───┐
   │  REJECT   │◄─────────────────────────────┤    SOLVING    │
   └───────────┘                              └───┬───────────┘
                                                  │
                                       RMS <= 3.0 │ Збіжність LM
                                       мкТл       ▼ за 4..10 кроків
                                              ┌───────────────┐
                                              │  VALIDATING   │
                                              └───┬───────────┘
                                                  │
                                       cond(W) <  │ Запис у Flash
                                       2.5        ▼ із CRC32
                                              ┌───────────────┐
                                              │  SAVED / OK   │
                                              └───────────────┘
```

### Просторове розбиття сфери (Spatial Binning)

Кожен вектор сирих вимірів `B_raw = [x, y, z]ᵀ` переводиться у сферичні координати — кут місця (Elevation) `θ ∈ [−π/2, +π/2]` та азимут (Azimuth) `φ ∈ [−π, +π]`:

```
θ = arcsin( z / ‖B_raw‖ )
φ = arctan2( y, x )
```

Діапазон кута місця розбивається на 6 широтних поясів, а азимут — на 12 секторів. Це утворює 72 просторові комірки. У кожну комірку приймається фіксована кількість вимірів `SAMPLES_PER_BIN = 4`. Загальний обсяг накопичувача становить `72 × 4 = 288` тривимірних точок (близько 3.5 КБ оперативної пам'яті).

---

## 2. Повний вихідний код конвеєра на C та C++

:::tabs
```c
/* ==========================================================================
 *  mag_cal_pipeline.c — Вбудований конвеєр калібрування магнітометра (C99)
 * ========================================================================== */

#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define MAG_CAL_BINS_LAT        6
#define MAG_CAL_BINS_LON        12
#define MAG_CAL_TOTAL_BINS      (MAG_CAL_BINS_LAT * MAG_CAL_BINS_LON) /* 72 */
#define MAG_CAL_SAMPLES_PER_BIN 4
#define MAG_CAL_MAX_POINTS      (MAG_CAL_TOTAL_BINS * MAG_CAL_SAMPLES_PER_BIN) /* 288 */

#define MAG_CAL_MAX_ITERATIONS  20
#define MAG_CAL_DEFAULT_EARTH_B 45.0f /* мкТл */

typedef struct {
    float x, y, z;
} vec3_t;

typedef struct {
    float m[3][3];
} mat3_t;

typedef struct {
    vec3_t offset;          /* Hard Iron вектор V_0 (мкТл) */
    mat3_t soft_iron;       /* Soft Iron матриця W (безрозмірна) */
    float  earth_field;     /* Оцінений модуль поля Землі (мкТл) */
    float  rms_residual;    /* Середньоквадратична нев'язка (мкТл) */
    float  coverage_pct;    /* Відсоток заповнених секторів сфери (0..100) */
    float  condition_num;   /* Число зумовленості матриці W */
    uint32_t crc32;         /* Контрольна сума для збереження у Flash */
    bool   is_valid;        /* Прапорець успішності калібрування */
} mag_cal_result_t;

typedef struct {
    vec3_t samples[MAG_CAL_TOTAL_BINS][MAG_CAL_SAMPLES_PER_BIN];
    uint8_t sample_count[MAG_CAL_TOTAL_BINS];
    uint16_t total_points;
    float target_earth_field;
} mag_cal_collector_t;

/* --- Векторна та матрична алгебра --- */

static inline vec3_t vec3_sub(vec3_t a, vec3_t b) {
    return (vec3_t){ a.x - b.x, a.y - b.y, a.z - b.z };
}

static inline float vec3_dot(vec3_t a, vec3_t b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

static inline float vec3_norm(vec3_t a) {
    return sqrtf(vec3_dot(a, a));
}

static inline vec3_t mat3_mul_vec(const mat3_t *m, vec3_t v) {
    return (vec3_t){
        m->m[0][0] * v.x + m->m[0][1] * v.y + m->m[0][2] * v.z,
        m->m[1][0] * v.x + m->m[1][1] * v.y + m->m[1][2] * v.z,
        m->m[2][0] * v.x + m->m[2][1] * v.y + m->m[2][2] * v.z
    };
}

/* Обчислення індексу сферичної комірки (Spatial Binning) */
static int mag_cal_get_bin_index(vec3_t raw) {
    float norm = vec3_norm(raw);
    if (norm < 1e-3f) return -1;

    /* Кут місця (Elevation/Pitch) від -pi/2 до +pi/2 */
    float elev = asinf(raw.z / norm);
    /* Азимут (Azimuth/Yaw) від -pi до +pi */
    float azim = atan2f(raw.y, raw.x);

    int lat_idx = (int)((elev + 1.5707963f) / (3.1415926f / MAG_CAL_BINS_LAT));
    if (lat_idx < 0) lat_idx = 0;
    if (lat_idx >= MAG_CAL_BINS_LAT) lat_idx = MAG_CAL_BINS_LAT - 1;

    int lon_idx = (int)((azim + 3.1415926f) / (6.2831853f / MAG_CAL_BINS_LON));
    if (lon_idx < 0) lon_idx = 0;
    if (lon_idx >= MAG_CAL_BINS_LON) lon_idx = MAG_CAL_BINS_LON - 1;

    return lat_idx * MAG_CAL_BINS_LON + lon_idx;
}

/* Ініціалізація збирача зразків */
void mag_cal_collector_init(mag_cal_collector_t *col, float earth_b) {
    memset(col, 0, sizeof(mag_cal_collector_t));
    col->target_earth_field = (earth_b > 10.0f) ? earth_b : MAG_CAL_DEFAULT_EARTH_B;
}

/* Додавання виміру з динамічним фільтром */
bool mag_cal_collector_push(mag_cal_collector_t *col, vec3_t raw, vec3_t gyro_rad_s) {
    /* Відхиляємо виміри при надто високій кутовій швидкості */
    if (vec3_norm(gyro_rad_s) > 1.745f) { /* > 100 град/с */
        return false;
    }

    int bin_idx = mag_cal_get_bin_index(raw);
    if (bin_idx < 0 || bin_idx >= MAG_CAL_TOTAL_BINS) return false;

    uint8_t count = col->sample_count[bin_idx];
    if (count < MAG_CAL_SAMPLES_PER_BIN) {
        col->samples[bin_idx][count] = raw;
        col->sample_count[bin_idx] = count + 1;
        col->total_points++;
        return true;
    }
    return false;
}

/* Оцінка відсотка покриття сфери */
float mag_cal_collector_coverage(const mag_cal_collector_t *col) {
    int filled = 0;
    for (int i = 0; i < MAG_CAL_TOTAL_BINS; i++) {
        if (col->sample_count[i] > 0) filled++;
    }
    return ((float)filled / (float)MAG_CAL_TOTAL_BINS) * 100.0f;
}

/* Розрахунок апроксимованого числа зумовленості для симетричної матриці 3x3 */
static float mat3_condition_number(const mat3_t *m) {
    /* Оцінка норми Фробеніуса та діагональних елементів */
    float trace = fabsf(m->m[0][0]) + fabsf(m->m[1][1]) + fabsf(m->m[2][2]);
    float min_diag = fminf(fabsf(m->m[0][0]), fminf(fabsf(m->m[1][1]), fabsf(m->m[2][2])));
    if (min_diag < 1e-4f) return 999.0f;
    return (trace / 3.0f) / min_diag;
}

/* Розв'язувач Levenberg-Marquardt (оптимізація 9 параметрів) */
bool mag_cal_run_solver(const mag_cal_collector_t *col, mag_cal_result_t *out) {
    memset(out, 0, sizeof(mag_cal_result_t));
    out->coverage_pct = mag_cal_collector_coverage(col);

    /* Необхідно мінімум 60% покриття та щонайменше 40 точок */
    if (out->coverage_pct < 60.0f || col->total_points < 40) {
        out->is_valid = false;
        return false;
    }

    /* Вектор параметрів p = [x0, y0, z0, W11, W12, W13, W22, W23, W33] */
    float p[9];
    /* Початкове наближення: центр у вибірковому середньому, W = I */
    float sum_x = 0, sum_y = 0, sum_z = 0;
    for (int b = 0; b < MAG_CAL_TOTAL_BINS; b++) {
        for (int s = 0; s < col->sample_count[b]; s++) {
            sum_x += col->samples[b][s].x;
            sum_y += col->samples[b][s].y;
            sum_z += col->samples[b][s].z;
        }
    }
    p[0] = sum_x / (float)col->total_points;
    p[1] = sum_y / (float)col->total_points;
    p[2] = sum_z / (float)col->total_points;
    p[3] = 1.0f; p[4] = 0.0f; p[5] = 0.0f;
    p[6] = 1.0f; p[7] = 0.0f; p[8] = 1.0f;

    float lambda = 1.0f;
    float earth_b = col->target_earth_field;

    for (int iter = 0; iter < MAG_CAL_MAX_ITERATIONS; iter++) {
        float H[9][9];
        float g[9];
        memset(H, 0, sizeof(H));
        memset(g, 0, sizeof(g));

        mat3_t W = {{
            { p[3], p[4], p[5] },
            { p[4], p[6], p[7] },
            { p[5], p[7], p[8] }
        }};
        vec3_t V0 = { p[0], p[1], p[2] };

        float total_residual_sq = 0.0f;

        /* Накопичення градієнта та матриці нормальних рівнянь */
        for (int b = 0; b < MAG_CAL_TOTAL_BINS; b++) {
            for (int s = 0; s < col->sample_count[b]; s++) {
                vec3_t raw = col->samples[b][s];
                vec3_t d = vec3_sub(raw, V0);
                vec3_t cal = mat3_mul_vec(&W, d);
                float cal_norm = vec3_norm(cal);
                if (cal_norm < 1e-4f) cal_norm = 1e-4f;

                float r = cal_norm - earth_b;
                total_residual_sq += r * r;

                vec3_t u = { cal.x / cal_norm, cal.y / cal_norm, cal.z / cal_norm };

                /* Рядок Якобіана J (1x9) */
                float J[9];
                /* Похідні по V0: -u^T * W */
                J[0] = -(u.x * W.m[0][0] + u.y * W.m[1][0] + u.z * W.m[2][0]);
                J[1] = -(u.x * W.m[0][1] + u.y * W.m[1][1] + u.z * W.m[2][1]);
                J[2] = -(u.x * W.m[0][2] + u.y * W.m[1][2] + u.z * W.m[2][2]);

                /* Похідні по W_ij */
                J[3] = u.x * d.x;                      /* W11 */
                J[4] = u.x * d.y + u.y * d.x;          /* W12 */
                J[5] = u.x * d.z + u.z * d.x;          /* W13 */
                J[6] = u.y * d.y;                      /* W22 */
                J[7] = u.y * d.z + u.z * d.y;          /* W23 */
                J[8] = u.z * d.z;                      /* W33 */

                /* H += J^T * J, g += J^T * r */
                for (int j = 0; j < 9; j++) {
                    g[j] += J[j] * r;
                    for (int k = 0; k < 9; k++) {
                        H[j][k] += J[j] * J[k];
                    }
                }
            }
        }

        /* Демпфування Левенберга: H[i][i] += lambda * H[i][i] + 1e-3 */
        for (int i = 0; i < 9; i++) {
            H[i][i] += lambda * (H[i][i] + 1e-3f);
        }

        /* Розв'язання лінійної системи H * dp = -g (метод Гаусса 9x9) */
        float dp[9];
        for (int i = 0; i < 9; i++) dp[i] = -g[i];

        /* Прямий хід Гаусса з вибором головного елемента */
        bool singular = false;
        for (int i = 0; i < 9; i++) {
            int max_r = i;
            float max_val = fabsf(H[i][i]);
            for (int k = i + 1; k < 9; k++) {
                if (fabsf(H[k][i]) > max_val) {
                    max_val = fabsf(H[k][i]);
                    max_r = k;
                }
            }
            if (max_val < 1e-8f) { singular = true; break; }

            if (max_r != i) {
                for (int k = 0; k < 9; k++) {
                    float tmp = H[i][k]; H[i][k] = H[max_r][k]; H[max_r][k] = tmp;
                }
                float tmp = dp[i]; dp[i] = dp[max_r]; dp[max_r] = tmp;
            }

            for (int k = i + 1; k < 9; k++) {
                float factor = H[k][i] / H[i][i];
                for (int j = i; j < 9; j++) {
                    H[k][j] -= factor * H[i][j];
                }
                dp[k] -= factor * dp[i];
            }
        }

        if (singular) {
            lambda *= 10.0f;
            continue;
        }

        /* Зворотний хід Гаусса */
        for (int i = 8; i >= 0; i--) {
            for (int j = i + 1; j < 9; j++) {
                dp[i] -= H[i][j] * dp[j];
            }
            dp[i] /= H[i][i];
        }

        /* Оновлення вектора параметрів */
        float dp_norm = 0.0f;
        for (int i = 0; i < 9; i++) {
            p[i] += dp[i];
            dp_norm += dp[i] * dp[i];
        }

        if (sqrtf(dp_norm) < 1e-4f) {
            /* Збіжність досягнута */
            break;
        }
        lambda = fmaxf(lambda * 0.2f, 1e-6f);
    }

    /* Запис підсумкових результатів */
    out->offset = (vec3_t){ p[0], p[1], p[2] };
    out->soft_iron = (mat3_t){{
        { p[3], p[4], p[5] },
        { p[4], p[6], p[7] },
        { p[5], p[7], p[8] }
    }};
    out->earth_field = earth_b;
    out->condition_num = mat3_condition_number(&out->soft_iron);

    /* Розрахунок RMS залишкової нев'язки */
    float sum_err_sq = 0.0f;
    for (int b = 0; b < MAG_CAL_TOTAL_BINS; b++) {
        for (int s = 0; s < col->sample_count[b]; s++) {
            vec3_t cal = mat3_mul_vec(&out->soft_iron, vec3_sub(col->samples[b][s], out->offset));
            float err = vec3_norm(cal) - earth_b;
            sum_err_sq += err * err;
        }
    }
    out->rms_residual = sqrtf(sum_err_sq / (float)col->total_points);

    /* Багаторівневий гейт якості: RMS < 3.0 мкТл та зумовленість < 2.5 */
    out->is_valid = (out->rms_residual < 3.0f) && (out->condition_num < 2.5f);
    return out->is_valid;
}

/* Застосування калібрувальної моделі в реальному часі */
vec3_t mag_cal_apply(vec3_t raw, const mag_cal_result_t *cal) {
    if (!cal->is_valid) return raw;
    vec3_t centered = vec3_sub(raw, cal->offset);
    return mat3_mul_vec(&cal->soft_iron, centered);
}
```
```cpp
/* ==========================================================================
 *  mag_cal_pipeline.hpp — Ідіоматичний модульний C++ калібратор магнітометра
 * ========================================================================== */

#pragma once

#include <array>
#include <cmath>
#include <cstdint>
#include <optional>
#include <span>
#include <algorithm>

namespace drone::sensors {

struct Vector3f {
    float x{0.0f}, y{0.0f}, z{0.0f};

    [[nodiscard]] constexpr Vector3f operator-(const Vector3f& rhs) const noexcept {
        return { x - rhs.x, y - rhs.y, z - rhs.z };
    }
    [[nodiscard]] constexpr Vector3f operator+(const Vector3f& rhs) const noexcept {
        return { x + rhs.x, y + rhs.y, z + rhs.z };
    }
    [[nodiscard]] constexpr float dot(const Vector3f& rhs) const noexcept {
        return x * rhs.x + y * rhs.y + z * rhs.z;
    }
    [[nodiscard]] float norm() const noexcept {
        return std::sqrt(dot(*this));
    }
};

struct Matrix3f {
    std::array<std::array<float, 3>, 3> m{{{1,0,0}, {0,1,0}, {0,0,1}}};

    [[nodiscard]] constexpr Vector3f operator*(const Vector3f& v) const noexcept {
        return {
            m[0][0] * v.x + m[0][1] * v.y + m[0][2] * v.z,
            m[1][0] * v.x + m[1][1] * v.y + m[1][2] * v.z,
            m[2][0] * v.x + m[2][1] * v.y + m[2][2] * v.z
        };
    }

    [[nodiscard]] float condition_number() const noexcept {
        const float trace = std::abs(m[0][0]) + std::abs(m[1][1]) + std::abs(m[2][2]);
        const float min_diag = std::min({std::abs(m[0][0]), std::abs(m[1][1]), std::abs(m[2][2])});
        if (min_diag < 1e-4f) return 999.0f;
        return (trace / 3.0f) / min_diag;
    }
};

struct CalibrationResult {
    Vector3f offset{};          // Hard Iron V_0
    Matrix3f soft_iron{};       // Soft Iron W
    float    earth_field{45.0f};
    float    rms_residual{0.0f};
    float    coverage_pct{0.0f};
    float    condition_num{1.0f};
    bool     valid{false};

    [[nodiscard]] Vector3f apply(const Vector3f& raw) const noexcept {
        if (!valid) return raw;
        return soft_iron * (raw - offset);
    }
};

template <size_t LatBins = 6, size_t LonBins = 12, size_t SamplesPerBin = 4>
class SpatialMagCollector {
public:
    static constexpr size_t TotalBins = LatBins * LonBins;
    static constexpr size_t MaxSamples = TotalBins * SamplesPerBin;

    explicit SpatialMagCollector(float target_earth_field = 45.0f) noexcept
        : target_earth_field_{target_earth_field} {}

    void reset() noexcept {
        sample_counts_.fill(0);
        total_points_ = 0;
    }

    bool push(const Vector3f& raw, const Vector3f& gyro_rad_s) noexcept {
        if (gyro_rad_s.norm() > 1.745f) { // > 100 deg/s
            return false;
        }

        const auto bin_idx = calculate_bin(raw);
        if (!bin_idx) return false;

        auto& count = sample_counts_[*bin_idx];
        if (count < SamplesPerBin) {
            samples_[*bin_idx][count] = raw;
            ++count;
            ++total_points_;
            return true;
        }
        return false;
    }

    [[nodiscard]] float coverage_percentage() const noexcept {
        size_t filled = 0;
        for (auto count : sample_counts_) {
            if (count > 0) ++filled;
        }
        return (static_cast<float>(filled) / static_cast<float>(TotalBins)) * 100.0f;
    }

    [[nodiscard]] std::optional<CalibrationResult> solve() const noexcept {
        const float coverage = coverage_percentage();
        if (coverage < 60.0f || total_points_ < 40) {
            return std::nullopt;
        }

        std::array<float, 9> p{0, 0, 0, 1.0f, 0, 0, 1.0f, 0, 1.0f};
        
        // Початковий центр як вибіркове середнє
        Vector3f sum{};
        for (size_t b = 0; b < TotalBins; ++b) {
            for (size_t s = 0; s < sample_counts_[b]; ++s) {
                sum = sum + samples_[b][s];
            }
        }
        p[0] = sum.x / static_cast<float>(total_points_);
        p[1] = sum.y / static_cast<float>(total_points_);
        p[2] = sum.z / static_cast<float>(total_points_);

        float lambda = 1.0f;

        for (size_t iter = 0; iter < 20; ++iter) {
            std::array<std::array<float, 9>, 9> H{};
            std::array<float, 9> g{};

            Matrix3f W{{{
                { p[3], p[4], p[5] },
                { p[4], p[6], p[7] },
                { p[5], p[7], p[8] }
            }}};
            Vector3f V0{ p[0], p[1], p[2] };

            for (size_t b = 0; b < TotalBins; ++b) {
                for (size_t s = 0; s < sample_counts_[b]; ++s) {
                    const Vector3f raw = samples_[b][s];
                    const Vector3f d = raw - V0;
                    const Vector3f cal = W * d;
                    const float cal_norm = std::max(cal.norm(), 1e-4f);
                    const float r = cal_norm - target_earth_field_;

                    const Vector3f u{ cal.x / cal_norm, cal.y / cal_norm, cal.z / cal_norm };

                    std::array<float, 9> J{
                        -(u.x * W.m[0][0] + u.y * W.m[1][0] + u.z * W.m[2][0]),
                        -(u.x * W.m[0][1] + u.y * W.m[1][1] + u.z * W.m[2][1]),
                        -(u.x * W.m[0][2] + u.y * W.m[1][2] + u.z * W.m[2][2]),
                        u.x * d.x,
                        u.x * d.y + u.y * d.x,
                        u.x * d.z + u.z * d.x,
                        u.y * d.y,
                        u.y * d.z + u.z * d.y,
                        u.z * d.z
                    };

                    for (size_t j = 0; j < 9; ++j) {
                        g[j] += J[j] * r;
                        for (size_t k = 0; k < 9; ++k) {
                            H[j][k] += J[j] * J[k];
                        }
                    }
                }
            }

            for (size_t i = 0; i < 9; ++i) {
                H[i][i] += lambda * (H[i][i] + 1e-3f);
            }

            // Гаусове розв'язання H * dp = -g
            std::array<float, 9> dp{};
            for (size_t i = 0; i < 9; ++i) dp[i] = -g[i];

            bool singular = false;
            for (size_t i = 0; i < 9; ++i) {
                size_t max_r = i;
                float max_val = std::abs(H[i][i]);
                for (size_t k = i + 1; k < 9; ++k) {
                    if (std::abs(H[k][i]) > max_val) {
                        max_val = std::abs(H[k][i]);
                        max_r = k;
                    }
                }
                if (max_val < 1e-8f) { singular = true; break; }

                if (max_r != i) {
                    std::swap(H[i], H[max_r]);
                    std::swap(dp[i], dp[max_r]);
                }

                for (size_t k = i + 1; k < 9; ++k) {
                    float factor = H[k][i] / H[i][i];
                    for (size_t j = i; j < 9; j++) {
                        H[k][j] -= factor * H[i][j];
                    }
                    dp[k] -= factor * dp[i];
                }
            }

            if (singular) {
                lambda *= 10.0f;
                continue;
            }

            for (int i = 8; i >= 0; --i) {
                for (size_t j = i + 1; j < 9; ++j) {
                    dp[i] -= H[i][j] * dp[j];
                }
                dp[i] /= H[i][i];
            }

            float step_norm_sq = 0.0f;
            for (size_t i = 0; i < 9; ++i) {
                p[i] += dp[i];
                step_norm_sq += dp[i] * dp[i];
            }

            if (std::sqrt(step_norm_sq) < 1e-4f) break;
            lambda = std::max(lambda * 0.2f, 1e-6f);
        }

        CalibrationResult res{};
        res.offset = { p[0], p[1], p[2] };
        res.soft_iron = Matrix3f{{{
            { p[3], p[4], p[5] },
            { p[4], p[6], p[7] },
            { p[5], p[7], p[8] }
        }}};
        res.earth_field = target_earth_field_;
        res.coverage_pct = coverage;
        res.condition_num = res.soft_iron.condition_number();

        float sum_sq = 0.0f;
        for (size_t b = 0; b < TotalBins; ++b) {
            for (size_t s = 0; s < sample_counts_[b]; ++s) {
                const auto cal = res.apply(samples_[b][s]);
                const float err = cal.norm() - target_earth_field_;
                sum_sq += err * err;
            }
        }
        res.rms_residual = std::sqrt(sum_sq / static_cast<float>(total_points_));
        res.valid = (res.rms_residual < 3.0f) && (res.condition_num < 2.5f);

        return res;
    }

private:
    [[nodiscard]] std::optional<size_t> calculate_bin(const Vector3f& raw) const noexcept {
        const float norm = raw.norm();
        if (norm < 1e-3f) return std::nullopt;

        const float elev = std::asin(std::clamp(raw.z / norm, -1.0f, 1.0f));
        const float azim = std::atan2(raw.y, raw.x);

        int lat_idx = static_cast<int>((elev + 1.5707963f) / (3.1415926f / LatBins));
        lat_idx = std::clamp(lat_idx, 0, static_cast<int>(LatBins - 1));

        int lon_idx = static_cast<int>((azim + 3.1415926f) / (6.2831853f / LonBins));
        lon_idx = std::clamp(lon_idx, 0, static_cast<int>(LonBins - 1));

        return static_cast<size_t>(lat_idx * LonBins + lon_idx);
    }

    std::array<std::array<Vector3f, SamplesPerBin>, TotalBins> samples_{};
    std::array<uint8_t, TotalBins> sample_counts_{};
    size_t total_points_{0};
    float target_earth_field_{45.0f};
};

} // namespace drone::sensors
```
:::

---

## 3. Покроковий розбір чисельної оптимізації та захист від виродження

### Прямий хід Гаусса з частковим вибором головного елемента

На кожній ітерації алгоритму Левенберга — Марквардта формується система лінійних алгебраїчних рівнянь 9×9 `H · Δp = −g`. Оскільки матриця Гессе `H` будується як наближення другого порядку `H = Jᵀ · J + λ · diag(Jᵀ · J)`, її визначник залежить від геометричної повноти вихідного набору точок.

У разі неповної хмари вимірів (наприклад, оператор крутив апарат лише в горизонтальній площині) кілька стовпців матриці Якобі `J` стають майже лінійно залежними. Це спричиняє падіння діагональних елементів матриці `H` до значень менше `10⁻⁸`.

Для захисту від чисельного переповнення у функції реалізовано:
1. **Частковий вибір головного елемента (Partial Pivoting):** на кроці `i` шукається рядок `max_r` із максимальним за модулем елементом `|H[k][i]|`. Рядки переставляються місцями, що усуває ділення на малі числа та мінімізує похибку округлення чисел з рухомою комою `float`.
2. **Детектор сингулярності:** якщо навіть після перестановки головний елемент `max_val < 1e-8f`, виставляється прапорець `singular = true`. У цьому випадку крок `Δp` скасовується, а параметр демпфування `λ` збільшується в 10 разів (`lambda *= 10.0f`). Це миттєво підсилює діагональну регуляризацію, перетворюючи матрицю на діагонально домінантну і переводячи метод у надійний градієнтний спуск.

---

## 4. Інтеграція в драйверний рівень та енергонезалежне збереження

### Організація потоків у FreeRTOS / Zephyr

Калібрувальний конвеєр розділяється на два асинхронні завдання з різними пріоритетами:
1. **Високопріоритетний потік опитування сенсорів (Sensor Task, 50–100 Гц):** зчитує сирі регістри магнітометра через шину SPI або I2C (наприклад, регістри даних чипів RM3100 або IST8310), перевіряє показання гіроскопа та викликає швидку неблокувальну функцію `mag_cal_collector_push()`. Час обробки одного виміру не перевищує 4 мікросекунд.
2. **Низькопріоритетний фоновий потік калібрування (Calibration Task):** періодично перевіряє відсоток покриття сфери `coverage_pct`. Щойно заповнено понад 80% секторів, потік викликає функцію `mag_cal_run_solver()`. Оскільки розв'язання системи 9×9 та 10 ітерацій LM вимагають близько 2–4 мілісекунд суцільного процесорного часу, вони виконуються у фоні, не створюючи джиттеру для критичних контурів кутової стабілізації.

### Серіалізація та енергонезалежне збереження у Flash/EEPROM

Калібрувальні коефіцієнти упаковуються в бінарну структуру фіксованого розміру 60 байтів:

```
⎡ Байти 00..11: Вектор Hard Iron V₀ (3 × float = 12 байтів)       ⎤
⎢ Байти 12..47: Матриця Soft Iron W (9 × float = 36 байтів)       ⎥
⎢ Байти 48..51: Еталонний модуль поля B_earth (1 × float = 4 б)   ⎥
⎢ Байти 52..55: Залишкова RMS похибка (1 × float = 4 байти)       ⎥
⎣ Байти 56..59: Контрольна сума CRC32 (1 × uint32 = 4 байти)      ⎦
```

При старті системи завантажувач зчитує цю структуру, перераховує контрольну суму CRC32 і перевіряє прапорець `is_valid`. Якщо контрольна сума не збігається або `RMS > 3.0 мкТл`, польотний стек виставляє статус відмови `EKF_MAG_FAULT`, сигналізує про помилку світлодіодами та блокує команду запуску двигунів (Arming).

---

## 5. Протокол телеметрії MAVLink та візуалізація калібрування

Під час виконання процедури калібрування польотний контролер передає на наземну станцію керування (QGroundControl або Mission Planner) поточний статус процесу за допомогою стандартних повідомлень протоколу MAVLink:
1. `MAG_CAL_PROGRESS` (повідомлення #191): транслюється з частотою 5–10 Гц і містить ідентифікатор компаса `compass_id`, поточний відсоток заповнення секторів `completion_pct`, бітову маску заповнених орієнтацій `completion_mask` та радіус поточної сфери. Наземна станція використовує ці дані для відмальовування тривимірної сфери з кольоровими точками в реальному часі, підказуючи оператору, яку саме вісь необхідно докрутити.
2. `MAG_CAL_REPORT` (повідомлення #192): надсилається одноразово після завершення роботи розв'язувача. Повідомлення містить обчислені зміщення `V_0`, матрицю `W`, фінальну похибку `fitness` (RMS) та статус придатності `MAG_CAL_SUCCESS` або `MAG_CAL_FAILED`.

У разі перевищення тайм-ауту бездіяльності (наприклад, відсутність нових точок протягом 60 секунд) або якщо користувач натискає кнопку скасування, автомат скидає накопичені точки та відновлює попередні робочі коефіцієнти з Flash-пам'яті.
