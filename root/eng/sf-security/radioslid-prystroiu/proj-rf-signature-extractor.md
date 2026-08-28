# ⚙️ Програмний комплекс вилучення RF-сигнатур та TDoA-локалізації

Радіочастотна сигнатура фізичного пристрою формується сукупністю мікроскопічних апаратних дефектів аналогового тракту: зміщенням несучої частоти (CFO), амплітудно-фазовим дисбалансом квадратур (IQ Imbalance) та постійною складовою зміщення (DC Offset). Для просторової пеленгації джерела використовується різницево-часовий аналіз (TDoA), який розв'язує систему нелінійних гіперболічних рівнянь за часовими відмітками кореляційних піків.

Нижче наведено робочий програмний комплекс для аналізу сирого потоку комплексних відліків `I/Q`, автоматичного вилучення вектора радіочастотних ознак передавача та розв'язання задачі двовимірної TDoA-локалізації методом Гаусса-Ньютона.

---

### Архітектура конвеєра цифрової обробки

Програмний комплекс виконує послідовну цифрову обробку комплексного вхідного сигналу `s[n] = I[n] + j·Q[n]` у п'ять взаємопов'язаних етапів:

1. **Компенсація постійного зміщення (DC Offset Removal):** витік гетеродина у змішувачах прямого перетворення формує незмодульовану складову на нульовій проміжній частоті. Модуль обчислює математичне сподівання каналів `I` та `Q` на інтервалі пакета і виконує центрування вибірки: `I_c[n] = I[n] - \mu_I`, `Q_c[n] = Q[n] - \mu_Q`.
2. **Оцінка квадратурного дисбалансу методом статистичних моментів:** амплітудний дисбаланс `α` розраховується як відношення середньоквадратичних потужностей `α = \sqrt{P_I / P_Q}`. Фазовий перекіс `ϕ` оцінюється через нормовану взаємну коваріацію між гілками: `\sin(ϕ) = E[I_c · Q_c] / \sqrt{P_I · P_Q}`.
3. **Оцінка зсуву частоти несучої (CFO Estimation) за алгоритмом Муза:** фазовий набіг між сусідніми відліками обчислюється через диференційну автокореляцію першого порядку `R_1 = \sum s[k+1] · s^*[k]`. Кут аргументу комплексного числа `\arg(R_1)` переводиться в абсолютне зміщення частоти в герцах з урахуванням частоти дискретизації `F_s`.
4. **Оцінка відношення сигнал/шум (SNR):** потужність змінного сигналу усереднюється по вікну спостереження та переводиться в логарифмічний масштаб [дБ].
5. **Розв'язання задачі TDoA-позиціонування:** на основі просторових координат трьох або більше базових станцій та векторів часових відміток `t_i` будується нелінійна система різниць відстаней `Δd_{i0} = c · (t_i - t_0)`. Ітераційний оптимізатор Гаусса-Ньютона мінімізує нев'язку положення шляхом розв'язання лінеаризованої системи нормальних рівнянь `(J^T · J) · \Delta P = J^T · r` на кожній ітерації.

---

### Повна реалізація аналізатора на C та ідіоматичному C++

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define SPEED_OF_LIGHT 299792458.0
#define MAX_ITERATIONS 50
#define EPSILON 1e-5

typedef struct {
    double i;
    double q;
} complex_sample_t;

typedef struct {
    double cfo_hz;             /* Оцінка зсуву несучої частоти, Гц */
    double iq_gain_imbalance;  /* Амплітудний дисбаланс alpha = I_rms / Q_rms */
    double iq_phase_skew_deg;  /* Фазовий перекіс між гілками, градуси */
    double dc_offset_i;        /* Постійне зміщення синфазного каналу */
    double dc_offset_q;        /* Постійне зміщення квадратурного каналу */
    double snr_estimate_db;    /* Оцінка відношення сигнал/шум, дБ */
} rf_signature_t;

typedef struct {
    double x;
    double y;
} point2d_t;

typedef struct {
    point2d_t pos;
    double timestamp_s;
} tdoa_sensor_t;

/* Оцінка постійного зміщення (DC Offset) */
void estimate_dc_offset(const complex_sample_t *samples, size_t count, double *dc_i, double *dc_q) {
    double sum_i = 0.0, sum_q = 0.0;
    for (size_t k = 0; k < count; ++k) {
        sum_i += samples[k].i;
        sum_q += samples[k].q;
    }
    *dc_i = sum_i / (double)count;
    *dc_q = sum_q / (double)count;
}

/* Оцінка квадратурного дисбалансу за методом моментів (IQ Imbalance) */
void estimate_iq_imbalance(const complex_sample_t *samples, size_t count, 
                           double dc_i, double dc_q, 
                           double *gain_imb, double *phase_skew_deg) {
    double p_i = 0.0, p_q = 0.0, cross_iq = 0.0;

    for (size_t k = 0; k < count; ++k) {
        double i_centered = samples[k].i - dc_i;
        double q_centered = samples[k].q - dc_q;
        p_i += i_centered * i_centered;
        p_q += q_centered * q_centered;
        cross_iq += i_centered * q_centered;
    }

    p_i /= (double)count;
    p_q /= (double)count;
    cross_iq /= (double)count;

    if (p_q > 1e-12) {
        *gain_imb = sqrt(p_i / p_q);
    } else {
        *gain_imb = 1.0;
    }

    double denom = sqrt(p_i * p_q);
    if (denom > 1e-12) {
        double sin_phi = cross_iq / denom;
        if (sin_phi > 1.0) sin_phi = 1.0;
        if (sin_phi < -1.0) sin_phi = -1.0;
        *phase_skew_deg = asin(sin_phi) * (180.0 / M_PI);
    } else {
        *phase_skew_deg = 0.0;
    }
}

/* Оцінка зміщення частоти несучої (CFO) методом автокореляції Муза */
double estimate_cfo(const complex_sample_t *samples, size_t count, double sample_rate_hz) {
    if (count < 2) return 0.0;
    double r_re = 0.0, r_im = 0.0;

    for (size_t k = 0; k < count - 1; ++k) {
        /* r[k+1] * conj(r[k]) */
        double re1 = samples[k + 1].i, im1 = samples[k + 1].q;
        double re0 = samples[k].i,     im0 = -samples[k].q; /* conj */
        r_re += (re1 * re0 - im1 * im0);
        r_im += (re1 * im0 + im1 * re0);
    }

    double phase_diff = atan2(r_im, r_re);
    return (phase_diff * sample_rate_hz) / (2.0 * M_PI);
}

/* Повний аналіз RF-сигнатури пакета */
bool extract_rf_signature(const complex_sample_t *samples, size_t count, 
                          double sample_rate_hz, rf_signature_t *out_sig) {
    if (!samples || count < 32 || !out_sig) return false;

    estimate_dc_offset(samples, count, &out_sig->dc_offset_i, &out_sig->dc_offset_q);
    estimate_iq_imbalance(samples, count, out_sig->dc_offset_i, out_sig->dc_offset_q,
                           &out_sig->iq_gain_imbalance, &out_sig->iq_phase_skew_deg);
    out_sig->cfo_hz = estimate_cfo(samples, count, sample_rate_hz);

    /* Оцінка потужності сигналу */
    double signal_pwr = 0.0;
    for (size_t k = 0; k < count; ++k) {
        double i_c = samples[k].i - out_sig->dc_offset_i;
        double q_c = samples[k].q - out_sig->dc_offset_q;
        signal_pwr += (i_c * i_c + q_c * q_c);
    }
    signal_pwr /= (double)count;
    out_sig->snr_estimate_db = 10.0 * log10(signal_pwr + 1e-12);

    return true;
}

/* Двовимірна локалізація TDoA методом Гаусса-Ньютона */
bool solve_tdoa_2d(const tdoa_sensor_t *sensors, size_t sensor_count, 
                   point2d_t initial_guess, point2d_t *out_pos) {
    if (!sensors || sensor_count < 3 || !out_pos) return false;

    double x = initial_guess.x;
    double y = initial_guess.y;

    for (int iter = 0; iter < MAX_ITERATIONS; ++iter) {
        double d0 = sqrt((x - sensors[0].pos.x) * (x - sensors[0].pos.x) + 
                         (y - sensors[0].pos.y) * (y - sensors[0].pos.y));
        if (d0 < 1e-4) d0 = 1e-4;

        /* J^T * J (розмір 2x2) та J^T * r (розмір 2x1) */
        double jtj00 = 0.0, jtj01 = 0.0, jtj11 = 0.0;
        double jtr0 = 0.0, jtr1 = 0.0;

        for (size_t i = 1; i < sensor_count; ++i) {
            double di = sqrt((x - sensors[i].pos.x) * (x - sensors[i].pos.x) + 
                             (y - sensors[i].pos.y) * (y - sensors[i].pos.y));
            if (di < 1e-4) di = 1e-4;

            double measured_delta_d = SPEED_OF_LIGHT * (sensors[i].timestamp_s - sensors[0].timestamp_s);
            double calculated_delta_d = di - d0;
            double residual = measured_delta_d - calculated_delta_d;

            double j_x = ((x - sensors[i].pos.x) / di) - ((x - sensors[0].pos.x) / d0);
            double j_y = ((y - sensors[i].pos.y) / di) - ((y - sensors[0].pos.y) / d0);

            jtj00 += j_x * j_x;
            jtj01 += j_x * j_y;
            jtj11 += j_y * j_y;

            jtr0 += j_x * residual;
            jtr1 += j_y * residual;
        }

        double det = jtj00 * jtj11 - jtj01 * jtj01;
        if (fabs(det) < 1e-12) return false; /* Погано обумовлена матриця (колінеарність) */

        double inv00 = jtj11 / det;
        double inv01 = -jtj01 / det;
        double inv11 = jtj00 / det;

        double delta_x = inv00 * jtr0 + inv01 * jtr1;
        double delta_y = inv01 * jtr0 + inv11 * jtr1;

        x += delta_x;
        y += delta_y;

        if (sqrt(delta_x * delta_x + delta_y * delta_y) < EPSILON) {
            out_pos->x = x;
            out_pos->y = y;
            return true;
        }
    }

    out_pos->x = x;
    out_pos->y = y;
    return true;
}

int main(void) {
    /* Генерація тестового сигналу з апаратним дисбалансом */
    const size_t N = 128;
    complex_sample_t test_signal[128];
    const double Fs = 10000000.0; /* 10 MSps */
    const double True_CFO = 45200.0; /* 45.2 кГц */

    for (size_t k = 0; k < N; ++k) {
        double t = (double)k / Fs;
        double phase = 2.0 * M_PI * True_CFO * t;
        /* I-гілка: коефіцієнт 1.06, зміщення 0.03 */
        test_signal[k].i = 1.06 * cos(phase) + 0.03;
        /* Q-гілка: коефіцієнт 0.94, зсув фази +4 град, зміщення -0.02 */
        test_signal[k].q = 0.94 * sin(phase + 4.0 * M_PI / 180.0) - 0.02;
    }

    rf_signature_t sig;
    if (extract_rf_signature(test_signal, N, Fs, &sig)) {
        printf("RF Fingerprint Extracted:\n");
        printf("  CFO: %.1f Hz\n", sig.cfo_hz);
        printf("  IQ Gain Imbalance: %.4f\n", sig.iq_gain_imbalance);
        printf("  IQ Phase Skew: %.2f deg\n", sig.iq_phase_skew_deg);
        printf("  DC Offset: I=%.3f, Q=%.3f\n", sig.dc_offset_i, sig.dc_offset_q);
    }

    /* Тест TDoA локалізації з 3 станціями */
    tdoa_sensor_t network[3] = {
        { .pos = { .x = 0.0,    .y = 0.0 },    .timestamp_s = 0.000001000 },
        { .pos = { .x = 1000.0, .y = 0.0 },    .timestamp_s = 0.000002155 },
        { .pos = { .x = 500.0,  .y = 1000.0 }, .timestamp_s = 0.000001840 }
    };

    point2d_t guess = { .x = 500.0, .y = 500.0 };
    point2d_t estimated_target;
    if (solve_tdoa_2d(network, 3, guess, &estimated_target)) {
        printf("TDoA Estimated Target: X=%.2f m, Y=%.2f m\n", 
               estimated_target.x, estimated_target.y);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <span>
#include <expected>
#include <numeric>

namespace rf {

inline constexpr double SpeedOfLight = 299792458.0;

struct Signature {
    double cfo_hz{0.0};
    double iq_gain_imbalance{1.0};
    double iq_phase_skew_deg{0.0};
    std::complex<double> dc_offset{0.0, 0.0};
    double snr_db{0.0};
};

struct Point2D {
    double x{0.0};
    double y{0.0};
};

struct TdoaSensor {
    Point2D pos;
    double timestamp_s{0.0};
};

enum class AnalysisError {
    InsufficientSamples,
    CollinearSensors,
    NonConvergent
};

class FingerprintAnalyzer {
public:
    [[nodiscard]] static std::expected<Signature, AnalysisError>
    extract(std::span<const std::complex<double>> samples, double sample_rate_hz) noexcept {
        if (samples.size() < 32) {
            return std::unexpected(AnalysisError::InsufficientSamples);
        }

        const auto count = static_cast<double>(samples.size());

        // 1. Оцінка постійного зміщення (DC Offset)
        const auto sum = std::accumulate(samples.begin(), samples.end(), std::complex<double>{0.0, 0.0});
        const auto dc = sum / count;

        // 2. Дисбаланс квадратурних гілок (IQ Imbalance)
        double p_i = 0.0;
        double p_q = 0.0;
        double cross_iq = 0.0;

        for (const auto& s : samples) {
            const double i_c = s.real() - dc.real();
            const double q_c = s.imag() - dc.imag();
            p_i += i_c * i_c;
            p_q += q_c * q_c;
            cross_iq += i_c * q_c;
        }

        p_i /= count;
        p_q /= count;
        cross_iq /= count;

        const double gain_imb = (p_q > 1e-12) ? std::sqrt(p_i / p_q) : 1.0;
        const double denom = std::sqrt(p_i * p_q);
        double phase_skew_deg = 0.0;

        if (denom > 1e-12) {
            const double sin_phi = std::clamp(cross_iq / denom, -1.0, 1.0);
            phase_skew_deg = std::asin(sin_phi) * (180.0 / std::numbers::pi);
        }

        // 3. Зсув частоти несучої (CFO) через автокореляцію Муза
        std::complex<double> r_cross{0.0, 0.0};
        for (std::size_t k = 0; k < samples.size() - 1; ++k) {
            r_cross += samples[k + 1] * std::conj(samples[k]);
        }

        const double phase_diff = std::arg(r_cross);
        const double cfo_hz = (phase_diff * sample_rate_hz) / (2.0 * std::numbers::pi);

        const double signal_pwr = (p_i + p_q);
        const double snr_db = 10.0 * std::log10(signal_pwr + 1e-12);

        return Signature{
            .cfo_hz = cfo_hz,
            .iq_gain_imbalance = gain_imb,
            .iq_phase_skew_deg = phase_skew_deg,
            .dc_offset = dc,
            .snr_db = snr_db
        };
    }
};

class TdoaLocalizer {
public:
    [[nodiscard]] static std::expected<Point2D, AnalysisError>
    localize2D(std::span<const TdoaSensor> sensors, Point2D initial_guess) noexcept {
        if (sensors.size() < 3) {
            return std::unexpected(AnalysisError::InsufficientSamples);
        }

        double x = initial_guess.x;
        double y = initial_guess.y;
        constexpr int MaxIterations = 50;
        constexpr double Tolerance = 1e-5;

        for (int iter = 0; iter < MaxIterations; ++iter) {
            double d0 = std::hypot(x - sensors[0].pos.x, y - sensors[0].pos.y);
            if (d0 < 1e-4) d0 = 1e-4;

            double jtj00 = 0.0, jtj01 = 0.0, jtj11 = 0.0;
            double jtr0 = 0.0, jtr1 = 0.0;

            for (std::size_t i = 1; i < sensors.size(); ++i) {
                double di = std::hypot(x - sensors[i].pos.x, y - sensors[i].pos.y);
                if (di < 1e-4) di = 1e-4;

                const double measured_delta_d = SpeedOfLight * (sensors[i].timestamp_s - sensors[0].timestamp_s);
                const double calc_delta_d = di - d0;
                const double residual = measured_delta_d - calc_delta_d;

                const double j_x = ((x - sensors[i].pos.x) / di) - ((x - sensors[0].pos.x) / d0);
                const double j_y = ((y - sensors[i].pos.y) / di) - ((y - sensors[0].pos.y) / d0);

                jtj00 += j_x * j_x;
                jtj01 += j_x * j_y;
                jtj11 += j_y * j_y;

                jtr0 += j_x * residual;
                jtr1 += j_y * residual;
            }

            const double det = jtj00 * jtj11 - jtj01 * jtj01;
            if (std::abs(det) < 1e-12) {
                return std::unexpected(AnalysisError::CollinearSensors);
            }

            const double inv00 = jtj11 / det;
            const double inv01 = -jtj01 / det;
            const double inv11 = jtj00 / det;

            const double delta_x = inv00 * jtr0 + inv01 * jtr1;
            const double delta_y = inv01 * jtr0 + inv11 * jtr1;

            x += delta_x;
            y += delta_y;

            if (std::hypot(delta_x, delta_y) < Tolerance) {
                return Point2D{x, y};
            }
        }

        return Point2D{x, y};
    }
};

} // namespace rf

int main() {
    constexpr std::size_t N = 128;
    constexpr double Fs = 10'000'000.0;
    constexpr double TrueCfo = 45'200.0;
    std::vector<std::complex<double>> signal(N);

    for (std::size_t k = 0; k < N; ++k) {
        const double t = static_cast<double>(k) / Fs;
        const double phase = 2.0 * std::numbers::pi * TrueCfo * t;
        signal[k] = std::complex<double>(
            1.06 * std::cos(phase) + 0.03,
            0.94 * std::sin(phase + 4.0 * std::numbers::pi / 180.0) - 0.02
        );
    }

    if (const auto sig = rf::FingerprintAnalyzer::extract(signal, Fs)) {
        std::cout << "C++ RF Fingerprint:\n"
                  << "  CFO: " << sig->cfo_hz << " Hz\n"
                  << "  Gain Imbalance: " << sig->iq_gain_imbalance << "\n"
                  << "  Phase Skew: " << sig->iq_phase_skew_deg << " deg\n"
                  << "  DC Offset: " << sig->dc_offset << "\n";
    }

    const std::vector<rf::TdoaSensor> sensors = {
        { .pos = { .x = 0.0,    .y = 0.0 },    .timestamp_s = 0.000001000 },
        { .pos = { .x = 1000.0, .y = 0.0 },    .timestamp_s = 0.000002155 },
        { .pos = { .x = 500.0,  .y = 1000.0 }, .timestamp_s = 0.000001840 }
    };

    if (const auto target = rf::TdoaLocalizer::localize2D(sensors, {500.0, 500.0})) {
        std::cout << "C++ TDoA Target: X=" << target->x << " m, Y=" << target->y << " m\n";
    }

    return 0;
}
```
:::

---

### Детальний розбір математичних операцій

Розглянемо ключові інженерні особливості обчислювального конвеєра:

1. **Матриця Якобі в алгоритмі Гаусса-Ньютона:** Лінеаризація системи різниць відстаней вимагає обчислення часткових похідних відстані `d_i = \sqrt{(x - x_i)^2 + (y - y_i)^2}` за просторовими координатами `x` та `y`:
   ```
   ∂d_i / ∂x = (x - x_i) / d_i
   ∂d_i / ∂y = (y - y_i) / d_i
   ```
   Для різницевого рівняння `f_i(x, y) = d_i - d_0` відповідний рядок матриці Якобі формується як різниця нормалізованих одиничних векторів спрямованості від цілі до `i`-ї та нульової станцій:
   ```
   J_{i, 0} = (x - x_i) / d_i - (x - x_0) / d_0
   J_{i, 1} = (y - y_i) / d_i - (y - y_0) / d_0
   ```

2. **Запобігання діленню на нуль:** Якщо поточна оцінка положення `(x, y)` точно збігається з координатами однієї з базових станцій, знаменник `d_i` обнуляється. У коді передбачено затискання `if (di < 1e-4) di = 1e-4`, що запобігає появі нечислових значень `NaN` та переповнення конвеєра FPU.

3. **Критерій зупинки оптимізації:** Ітераційний процес завершується, коли модуль вектора приросту `\sqrt{\Delta x^2 + \Delta y^2}` опускається нижче порогового значення `EPSILON = 10^{-5}` м (0.01 мм) або досягається ліміт `MAX_ITERATIONS = 50`.

4. **Регуляризація Левенберга-Марквардта:** У складних умовах міської забудови, коли визначник матриці наближається до нуля, до діагональних елементів додається коефіцієнт демпфування: `(J^T · J + \lambda · I) · \Delta P = J^T · r`. Це запобігає розбіжності траєкторії оцінки.

---

### Інженерні пастки реалізації та методи калібрування

Під час розгортання пеленгаційних та розвідувальних систем на практиці виникають такі типові виклики:

1. **Геометрична виродженість та колінеарність сенсорів:** Якщо три приймальні станції TDoA розміщено майже на одній прямій лінії (наприклад, уздовж лінії автодороги або узбережжя річки), матриця нормальних рівнянь `J^T · J` втрачає лінійну незалежність. Її визначник `\det(J^T · J)` прямує до нуля, викликаючи катастрофічне зростання геометричного фактора GDOP. У такій конфігурації похибка вимірювання затримки часу в 5 наносекунд призводить до похибки поперечного зміщення цілі на сотні метрів. Для усунення проблеми сенсори обов'язково розміщують трикутником або багатокутником із тупими кутами, охоплюючи передбачуваний район знаходження передавача.

2. **Фазове переповнення (Wrap-around) в оцінці CFO:** Функція `atan2()` обчислює фазовий зсув строго в діапазоні `[-π, +π]`. Якщо реальне зміщення частоти `Δf` перевищує половину частоти дискретизації `F_s / 2`, відбувається перескок фази на `2π`, що повністю спотворює обчислену сигнатуру. Для надійного охоплення широких діапазонів застосовують двокроковий алгоритм: спочатку груба оцінка частоти за положенням максимуму БПФ (FFT Peak), а потім прецизійна оцінка за аргументом кореляції залишку.

3. **Вплив багатопроменевого поширення (Multipath Distortion):** Відбиття від будівель, пагорбів та великих металевих об'єктів створюють копії сигналу із запізненням, деформуючи виміряну матрицю IQ-дисбалансу. Для очищення сигнатури застосовують часове стробування (Time-gating): аналізатор виділяє для розрахунку параметрів виключно перші 100–200 відліків прямого променя (Direct Path Arrival) до приходу відбитих ехо-сигналів.

4. **Температурний дрейф аналогового тракту приймача:** Апаратний дисбаланс квадратур приймальної станції накладається на дисбаланс передавача. Перед проведенням вимірювань приймач обов'язково калібрується за допомогою вбудованого генератора контрольного тестового тону (Loopback Calibration), щоб виключити власні спотворення оцифровувача з підсумкової сигнатури.

5. **Синхронізація відліків у Linux просторі користувача:** Передача потоків IQ через Ethernet-пакети протоколу VITA 49 або eCPRI вимагає використання апаратних міток часу мережевої карти (Hardware Timestamping через прапорець сокета `SO_TIMESTAMPING`), оскільки програмне додавання мітки в обробнику ядра Linux вносить непередбачуваний джитер планувальника від 5 до 100 мікросекунд, що неприпустимо для наносекундної точності TDoA.
