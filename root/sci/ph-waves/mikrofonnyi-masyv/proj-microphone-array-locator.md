# ⚙️ Практичний проект мікрофонного пеленгатора на C та C++

У цьому проекті представлено повноцінний алгоритмічний конвеєр для локалізації джерела звуку та просторової фільтрації на базі мікрофонного масиву. Програмний комплекс реалізує повний цикл обробки: від генерації багатоканального звукового поля в умовах шуму до спектрального розрахунку взаємної кореляції GCC-PHAT з фазовим відбілюванням, параболічної субдискретної інтерполяції затримки приходу та просторового фазування за алгоритмом «затримка та додавання» (Delay-and-Sum Beamformer).

## 1. Архітектура та математична структура конвеєра

Програмний конвеєр складається з чотирьох послідовних функціональних модулів:

### Модуль 1: Акустичний симулятор звукового поля
Для автономного тестування алгоритму без підключення фізичного обладнання модуль синтезує багатоканальний аудіосигнал. Модель генерує суміш основного гармонічного тону з обертонами, що відповідає характерному спектру мови чи механічного джерела шуму:
- Для кожного `m`-го мікрофона лінійного масиву розраховується точна фізична часова затримка `τ_m = (m · d · sin(θ_target)) / c`.
- Сигнал зміщується у часі з високою субдискретною точністю.
- До кожного каналу додається некорельований псевдовипадковий білий шум із регульованою дисперсією для перевірки стійкості локалізатора при низьких відношеннях сигнал/шум (SNR).

### Модуль 2: Спектральний аналізатор БПФ (Fast Fourier Transform)
Усі обчислення кореляції виконуються у частотній області для досягнення обчислювальної складності `O(N log N)` замість прямої часової згортки `O(N²)`:
- Кадри аудіоданих розміром `N = 1024` відліки множаться на вікно Ганна `w[n] = 0.5 · (1 - cos(2π n / (N-1)))`, що мінімізує ефект спектрального просочування (spectral leakage).
- Застосовується класичний алгоритм швидкого перетворення Фур'є Кулі-Тьюкі (Cooley-Tukey Radix-2) з двійково-інверсною перестановкою відліків та ітеративними метеликовими операціями.
- Зворотне перетворення Фур'є (IFFT) виконується тим самим алгоритмом із комплексним спряженням повертаючих множників та масштабуванням результату на коефіцієнт `1 / N`.

### Модуль 3: Оцінювач TDoA на базі алгоритму GCC-PHAT
Для пари мікрофонів з максимальною базою (крайні елементи масиву `M₀` та `M_{M-1}`) обчислюється взаємна спектральна густина потужності:
- Комплексне перемноження спектрів: `G₁₂[k] = X₁[k] · X₂*[k]`.
- Фазове відбілювання (PHAT): кожна спектральна гармоніка ділиться на власний модуль `|G₁₂[k]| + ε`, де `ε = 10⁻⁷` запобігає діленню на нуль у смугах загородження.
- Зворотне перетворення Фур'є переводить нормований спектр у часову функцію взаємної кореляції `R₁₂^PHAT[m]`.
- Від'ємні та додатні затримки декодуються з циклічного буфера БПФ: відліки `0 ... N/2` відповідають додатним затримкам `τ \ge 0`, а відліки `N/2 ... N-1` — від'ємним затримкам `τ < 0`.
- Пошук піку обмежується фізично можливим часовим вікном `|τ| \le d_total / c`.

### Модуль 4: Параболічна субдискретна інтерполяція та просторове фазування
Дискретний крок вибірки на частоті `f_s = 16 000 Гц` становить `T_s = 62.5 мкс`. За цей час звук долає у повітрі відстань `Δr = c · T_s ≈ 21.4 мм`. Якщо крок між мікрофонами становить 42 мм, уся кутова півсфера `[-90°, +90°]` покривається лише кількома дискретними відліками затримки, що дає неприпустимо грубу дискретність кута (похибка 10–25°):
- Алгоритм виконує аналітичну параболічну апроксимацію верхівки кореляційного піка за трьома сусідніми точками: `y_{-1} = R[m-1]`, `y_0 = R[m]`, `y_{+1} = R[m+1]`.
- Зсув піку `δ = (y_{-1} - y_{+1}) / (2 · (y_{-1} - 2 y_0 + y_{+1}))` уточнює затримку з точністю до десятих часток мікросекунди.
- Знайдений кут пеленга `θ_est = arcsin(c · τ_est / d_total)` передається в модуль Delay-and-Sum.
- Модуль фазування компенсує затримки каналів за допомогою лінійної дробової інтерполяції та формує очищений монофонічний аудіопотік.

## 2. Реалізація алгоритму на C та C++

Нижче наведено повні самодостатні програми мовами C та C++, які виконують синтез багатоканального аудіо, локалізацію джерела через GCC-PHAT та формування променя Delay-and-Sum.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#define M_PI_F 3.14159265358979323846f
#define NUM_MICS 4
#define FRAME_SIZE 1024
#define SAMPLING_RATE 16000.0f
#define SPEED_OF_SOUND 343.0f
#define MIC_SPACING 0.042f // 4.2 см (d <= lambda/2 для f <= 4083 Гц)

typedef struct {
    float re;
    float im;
} Complex;

static Complex c_add(Complex a, Complex b) {
    Complex r = { a.re + b.re, a.im + b.im };
    return r;
}

static Complex c_sub(Complex a, Complex b) {
    Complex r = { a.re - b.re, a.im - b.im };
    return r;
}

static Complex c_mul(Complex a, Complex b) {
    Complex r = { a.re * b.re - a.im * b.im, a.re * b.im + a.im * b.re };
    return r;
}

static Complex c_conj(Complex a) {
    Complex r = { a.re, -a.im };
    return r;
}

static float c_abs(Complex a) {
    return sqrtf(a.re * a.re + a.im * a.im);
}

// Пряме та зворотне швидке перетворення Фур'є (Cooley-Tukey Radix-2)
static void fft(Complex* x, int n, int invert) {
    int i, j, k;
    for (i = 1, j = 0; i < n; i++) {
        int bit = n >> 1;
        for (; j & bit; bit >>= 1) {
            j ^= bit;
        }
        j ^= bit;
        if (i < j) {
            Complex tmp = x[i];
            x[i] = x[j];
            x[j] = tmp;
        }
    }

    for (int len = 2; len <= n; len <<= 1) {
        float ang = 2.0f * M_PI_F / (float)len * (invert ? -1.0f : 1.0f);
        Complex wlen = { cosf(ang), sinf(ang) };
        for (i = 0; i < n; i += len) {
            Complex w = { 1.0f, 0.0f };
            for (k = 0; k < len / 2; k++) {
                Complex u = x[i + k];
                Complex v = c_mul(x[i + k + len / 2], w);
                x[i + k] = c_add(u, v);
                x[i + k + len / 2] = c_sub(u, v);
                w = c_mul(w, wlen);
            }
        }
    }

    if (invert) {
        for (i = 0; i < n; i++) {
            x[i].re /= (float)n;
            x[i].im /= (float)n;
        }
    }
}

// Розрахунок GCC-PHAT та визначення затримки між двома каналами
static float gcc_phat_tdoa(const float* sig1, const float* sig2, int n, float fs, float d_max_sec) {
    Complex* x1 = (Complex*)malloc(sizeof(Complex) * n);
    Complex* x2 = (Complex*)malloc(sizeof(Complex) * n);
    Complex* g12 = (Complex*)malloc(sizeof(Complex) * n);

    for (int i = 0; i < n; i++) {
        float win = 0.5f * (1.0f - cosf(2.0f * M_PI_F * (float)i / (float)(n - 1)));
        x1[i].re = sig1[i] * win;
        x1[i].im = 0.0f;
        x2[i].re = sig2[i] * win;
        x2[i].im = 0.0f;
    }

    fft(x1, n, 0);
    fft(x2, n, 0);

    const float eps = 1e-7f;
    for (int k = 0; k < n; k++) {
        Complex prod = c_mul(x1[k], c_conj(x2[k]));
        float mag = c_abs(prod);
        g12[k].re = prod.re / (mag + eps);
        g12[k].im = prod.im / (mag + eps);
    }

    fft(g12, n, 1);

    // Максимальна кількість відліків затримки за відстанню між мікрофонами
    int max_lags = (int)ceilf(d_max_sec * fs) + 2;
    if (max_lags > n / 2) max_lags = n / 2;

    float max_val = -1.0f;
    int best_lag = 0;

    for (int lag = -max_lags; lag <= max_lags; lag++) {
        int idx = (lag < 0) ? (n + lag) : lag;
        float val = g12[idx].re;
        if (val > max_val) {
            max_val = val;
            best_lag = lag;
        }
    }

    // Параболічна субдискретна інтерполяція верхівки кореляційного піка
    int idx_m = (best_lag - 1 < 0) ? (n + best_lag - 1) : (best_lag - 1);
    int idx_0 = (best_lag < 0) ? (n + best_lag) : best_lag;
    int idx_p = (best_lag + 1 < 0) ? (n + best_lag + 1) : (best_lag + 1);

    float ym = g12[idx_m].re;
    float y0 = g12[idx_0].re;
    float yp = g12[idx_p].re;

    float delta = 0.0f;
    float denom = 2.0f * (ym - 2.0f * y0 + yp);
    if (fabsf(denom) > 1e-9f) {
        delta = (ym - yp) / denom;
        if (delta > 0.5f) delta = 0.5f;
        if (delta < -0.5f) delta = -0.5f;
    }

    free(x1);
    free(x2);
    free(g12);

    return ((float)best_lag + delta) / fs;
}

// Формування променя Delay-and-Sum для заданого кута theta_deg
static void delay_and_sum(const float input[NUM_MICS][FRAME_SIZE], float* output,
                          int n, float fs, float theta_deg, float spacing, float c) {
    float theta_rad = theta_deg * M_PI_F / 180.0f;

    for (int i = 0; i < n; i++) {
        output[i] = 0.0f;
    }

    for (int m = 0; m < NUM_MICS; m++) {
        float tau_sec = (float)m * spacing * sinf(theta_rad) / c;
        float shift_samples = tau_sec * fs;
        int int_shift = (int)floorf(shift_samples);
        float frac_shift = shift_samples - (float)int_shift;

        for (int i = 0; i < n; i++) {
            int src_idx = i + int_shift;
            float val = 0.0f;
            if (src_idx >= 0 && src_idx + 1 < n) {
                val = (1.0f - frac_shift) * input[m][src_idx] + frac_shift * input[m][src_idx + 1];
            } else if (src_idx >= 0 && src_idx < n) {
                val = input[m][src_idx];
            }
            output[i] += val / (float)NUM_MICS;
        }
    }
}

int main(void) {
    float audio[NUM_MICS][FRAME_SIZE];
    float target_angle_deg = 32.0f;
    float target_freq = 1200.0f;

    printf("=== Мікрофонний масив: TDoA локалізація та Delay-and-Sum ===\n");
    printf("Конфігурація: M = %d мікрофонів, d = %.3f м, fs = %.0f Гц\n",
           NUM_MICS, MIC_SPACING, SAMPLING_RATE);
    printf("Істинний кут джерела: %.1f градусів\n\n", target_angle_deg);

    float target_rad = target_angle_deg * M_PI_F / 180.0f;

    // Синтез тестових сигналів з різницею ходу та шумом
    for (int m = 0; m < NUM_MICS; m++) {
        float delay_sec = (float)m * MIC_SPACING * sinf(target_rad) / SPEED_OF_SOUND;
        for (int i = 0; i < FRAME_SIZE; i++) {
            float t = (float)i / SAMPLING_RATE - delay_sec;
            // Тональний сигнал з гармонікою
            float sig = sinf(2.0f * M_PI_F * target_freq * t) + 0.5f * sinf(2.0f * M_PI_F * 2.0f * target_freq * t);
            // Адитивний білий шум
            float noise = (((float)rand() / (float)RAND_MAX) - 0.5f) * 0.4f;
            audio[m][i] = sig + noise;
        }
    }

    // Локалізація джерела через GCC-PHAT між M0 та M3 (максимальна база)
    float d_total = (float)(NUM_MICS - 1) * MIC_SPACING;
    float tdoa_est = gcc_phat_tdoa(audio[0], audio[NUM_MICS - 1], FRAME_SIZE, SAMPLING_RATE, d_total / SPEED_OF_SOUND);

    float sin_arg = tdoa_est * SPEED_OF_SOUND / d_total;
    if (sin_arg > 1.0f) sin_arg = 1.0f;
    if (sin_arg < -1.0f) sin_arg = -1.0f;
    float estimated_angle_deg = asinf(sin_arg) * 180.0f / M_PI_F;

    printf("Оцінена затримка TDoA (M0 -> M%d): %.4f мс\n", NUM_MICS - 1, tdoa_est * 1000.0f);
    printf("Оцінений кут приходу: %.2f градусів (похибка: %.2f°)\n\n",
           estimated_angle_deg, fabsf(estimated_angle_deg - target_angle_deg));

    // Застосування Delay-and-Sum beamforming
    float beamformed[FRAME_SIZE];
    delay_and_sum(audio, beamformed, FRAME_SIZE, SAMPLING_RATE, estimated_angle_deg, MIC_SPACING, SPEED_OF_SOUND);

    // Оцінка потужності одного каналу проти сформованого променя
    float p_single = 0.0f, p_beam = 0.0f;
    for (int i = 0; i < FRAME_SIZE; i++) {
        p_single += audio[0][i] * audio[0][i];
        p_beam += beamformed[i] * beamformed[i];
    }
    p_single /= (float)FRAME_SIZE;
    p_beam /= (float)FRAME_SIZE;

    printf("Середня потужність одиночного мікрофона M0: %.4f\n", p_single);
    printf("Середня потужність сформованого променя:      %.4f\n", p_beam);
    printf("Алгоритм успішно виділив синфазний сигнал та придушив шум.\n");

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
#include <random>
#include <algorithm>
#include <optional>

class MicrophoneArrayProcessor {
public:
    using Complex = std::complex<float>;

    MicrophoneArrayProcessor(std::size_t numMics, float spacingMeters, float samplingRate, float soundSpeed = 343.0f)
        : m_numMics(numMics), m_spacing(spacingMeters), m_fs(samplingRate), m_c(soundSpeed) {}

    // Швидке перетворення Фур'є (In-place Radix-2 FFT/IFFT)
    static void fft(std::span<Complex> data, bool invert) {
        const std::size_t n = data.size();
        for (std::size_t i = 1, j = 0; i < n; ++i) {
            std::size_t bit = n >> 1;
            for (; j & bit; bit >>= 1) {
                j ^= bit;
            }
            j ^= bit;
            if (i < j) {
                std::swap(data[i], data[j]);
            }
        }

        for (std::size_t len = 2; len <= n; len <<= 1) {
            const float angle = 2.0f * std::numbers::pi_v<float> / static_cast<float>(len) * (invert ? -1.0f : 1.0f);
            const Complex wlen(std::cos(angle), std::sin(angle));
            for (std::size_t i = 0; i < n; i += len) {
                Complex w(1.0f, 0.0f);
                for (std::size_t k = 0; k < len / 2; ++k) {
                    const Complex u = data[i + k];
                    const Complex v = data[i + k + len / 2] * w;
                    data[i + k] = u + v;
                    data[i + k + len / 2] = u - v;
                    w *= wlen;
                }
            }
        }

        if (invert) {
            const float invN = 1.0f / static_cast<float>(n);
            for (auto& val : data) {
                val *= invN;
            }
        }
    }

    // Оцінка різниці затримки сигналу (TDoA) через GCC-PHAT
    [[nodiscard]] float estimateTdoaGccPhat(std::span<const float> sig1, std::span<const float> sig2, float maxDistanceMeters) const {
        const std::size_t n = sig1.size();
        std::vector<Complex> x1(n), x2(n), g12(n);

        for (std::size_t i = 0; i < n; ++i) {
            const float win = 0.5f * (1.0f - std::cos(2.0f * std::numbers::pi_v<float> * static_cast<float>(i) / static_cast<float>(n - 1)));
            x1[i] = Complex(sig1[i] * win, 0.0f);
            x2[i] = Complex(sig2[i] * win, 0.0f);
        }

        fft(x1, false);
        fft(x2, false);

        constexpr float eps = 1e-7f;
        for (std::size_t k = 0; k < n; ++k) {
            const Complex prod = x1[k] * std::conj(x2[k]);
            const float mag = std::abs(prod);
            g12[k] = prod / (mag + eps);
        }

        fft(g12, true);

        const int maxLags = std::min<int>(static_cast<int>(std::ceil((maxDistanceMeters / m_c) * m_fs)) + 2, static_cast<int>(n / 2));
        float maxVal = -1.0f;
        int bestLag = 0;

        for (int lag = -maxLags; lag <= maxLags; ++lag) {
            const std::size_t idx = (lag < 0) ? (n + lag) : static_cast<std::size_t>(lag);
            const float val = g12[idx].real();
            if (val > maxVal) {
                maxVal = val;
                bestLag = lag;
            }
        }

        // Параболічна субдискретна інтерполяція
        const std::size_t idxM = (bestLag - 1 < 0) ? (n + bestLag - 1) : static_cast<std::size_t>(bestLag - 1);
        const std::size_t idx0 = (bestLag < 0) ? (n + bestLag) : static_cast<std::size_t>(bestLag);
        const std::size_t idxP = (bestLag + 1 < 0) ? (n + bestLag + 1) : static_cast<std::size_t>(bestLag + 1);

        const float ym = g12[idxM].real();
        const float y0 = g12[idx0].real();
        const float yp = g12[idxP].real();

        float delta = 0.0f;
        const float denom = 2.0f * (ym - 2.0f * y0 + yp);
        if (std::abs(denom) > 1e-9f) {
            delta = std::clamp((ym - yp) / denom, -0.5f, 0.5f);
        }

        return (static_cast<float>(bestLag) + delta) / m_fs;
    }

    // Оцінка кута напрямку на джерело за масивом
    [[nodiscard]] float estimateDoaDegrees(std::span<const float> mic0, std::span<const float> micLast) const {
        const float totalDistance = static_cast<float>(m_numMics - 1) * m_spacing;
        const float tdoa = estimateTdoaGccPhat(mic0, micLast, totalDistance);
        const float sinVal = std::clamp(tdoa * m_c / totalDistance, -1.0f, 1.0f);
        return std::asin(sinVal) * 180.0f / std::numbers::pi_v<float>;
    }

    // Формування променя Delay-and-Sum
    [[nodiscard]] std::vector<float> delayAndSumBeamform(const std::vector<std::vector<float>>& multiChannelAudio, float steerAngleDeg) const {
        const std::size_t frameSize = multiChannelAudio[0].size();
        std::vector<float> output(frameSize, 0.0f);
        const float steerRad = steerAngleDeg * std::numbers::pi_v<float> / 180.0f;

        for (std::size_t m = 0; m < m_numMics; ++m) {
            const float tau = static_cast<float>(m) * m_spacing * std::sin(steerRad) / m_c;
            const float shiftSamples = tau * m_fs;
            const int intShift = static_cast<int>(std::floor(shiftSamples));
            const float fracShift = shiftSamples - static_cast<float>(intShift);

            for (std::size_t i = 0; i < frameSize; ++i) {
                const int srcIdx = static_cast<int>(i) + intShift;
                float val = 0.0f;
                if (srcIdx >= 0 && static_cast<std::size_t>(srcIdx + 1) < frameSize) {
                    val = (1.0f - fracShift) * multiChannelAudio[m][srcIdx] + fracShift * multiChannelAudio[m][srcIdx + 1];
                } else if (srcIdx >= 0 && static_cast<std::size_t>(srcIdx) < frameSize) {
                    val = multiChannelAudio[m][srcIdx];
                }
                output[i] += val / static_cast<float>(m_numMics);
            }
        }
        return output;
    }

private:
    std::size_t m_numMics;
    float m_spacing;
    float m_fs;
    float m_c;
};

int main() {
    constexpr std::size_t numMics = 4;
    constexpr std::size_t frameSize = 1024;
    constexpr float samplingRate = 16000.0f;
    constexpr float micSpacing = 0.042f;
    constexpr float speedOfSound = 343.0f;
    constexpr float targetAngleDeg = 32.0f;
    constexpr float targetFreq = 1200.0f;

    std::cout << "=== [C++] Мікрофонний масив: TDoA локалізація та Delay-and-Sum ===\n";
    std::cout << "Конфігурація: M = " << numMics << ", d = " << micSpacing << " м, fs = " << samplingRate << " Гц\n";
    std::cout << "Цільовий кут: " << targetAngleDeg << "°\n\n";

    MicrophoneArrayProcessor processor(numMics, micSpacing, samplingRate, speedOfSound);

    std::vector<std::vector<float>> multiChannelAudio(numMics, std::vector<float>(frameSize));
    const float targetRad = targetAngleDeg * std::numbers::pi_v<float> / 180.0f;

    std::mt19937 rng(42);
    std::uniform_real_distribution<float> noiseDist(-0.2f, 0.2f);

    for (std::size_t m = 0; m < numMics; ++m) {
        const float delay = static_cast<float>(m) * micSpacing * std::sin(targetRad) / speedOfSound;
        for (std::size_t i = 0; i < frameSize; ++i) {
            const float t = static_cast<float>(i) / samplingRate - delay;
            const float sig = std::sin(2.0f * std::numbers::pi_v<float> * targetFreq * t)
                            + 0.5f * std::sin(2.0f * std::numbers::pi_v<float> * 2.0f * targetFreq * t);
            multiChannelAudio[m][i] = sig + noiseDist(rng);
        }
    }

    const float estimatedAngle = processor.estimateDoaDegrees(multiChannelAudio.front(), multiChannelAudio.back());
    std::cout << "Оцінений кут джерела (GCC-PHAT): " << estimatedAngle << "° (похибка: "
              << std::abs(estimatedAngle - targetAngleDeg) << "°)\n";

    const auto beamformed = processor.delayAndSumBeamform(multiChannelAudio, estimatedAngle);

    float pSingle = 0.0f, pBeam = 0.0f;
    for (std::size_t i = 0; i < frameSize; ++i) {
        pSingle += multiChannelAudio[0][i] * multiChannelAudio[0][i];
        pBeam += beamformed[i] * beamformed[i];
    }
    pSingle /= static_cast<float>(frameSize);
    pBeam /= static_cast<float>(frameSize);

    std::cout << "Потужність входу M0:      " << pSingle << "\n";
    std::cout << "Потужність після променя: " << pBeam << "\n";
    std::cout << "Просторовий фільтр успішно підсилив цільовий напрямок.\n";

    return 0;
}
```
:::

## 3. Аналіз роботи та інженерні пастки реалізації

Під час практичного розгортання алгоритму на вбудованих платформах (ARM Cortex, DSP, FPGA) інженер стикається з низкою критичних крайових випадків:

### Дробова інтерполяція та затримки між відліками
Лінійна дробова інтерполяція є обчислювально найлегшою, проте вона діє як низькочастотний фільтр першого порядку, послаблюючи високі частоти сигналу пропорційно дробовій частині затримки `s_frac · (1 - s_frac)`. У високоякісних аудіосистемах замість лінійної інтерполяції застосовують поліфазні КІХ-фільтри (Polyphase FIR Filters) на основі зрізаної функції `sinc`, що зберігають амплітудно-частотну характеристику в усій робочій смузі без завалу високих частот.

### Обробка країв кадрового буфера
При зсуві сигналу на затримку `+int_shift` індекси на межах кадру можуть виходити за межі масиву `[0, N-1]`. Обнулення країв породжує клацання (кліки) на стиках блоків при відтворенні. Для запобігання цьому використовують техніку Overlap-Add або Overlap-Save з кільцевими буферами передісторії (history buffers) розміром не менше максимальної фізичної затримки масиву `max_shift = (M-1) · d / c · f_s`.

### Стабілізація ділення у PHAT (Регуляризація)
Якщо сигнал у певному частотному біні повністю відсутній (наприклад, у смузі загородження аналогового фільтра антиаліасингу АЦП), вираз `|G₁₂[k]|` наближається до машинного нуля. Пряме ділення на нуль без захисного коефіцієнта `eps` призводить до генерації значень `NaN` та різкого підсилення високочастотного шуму квантування, що руйнує кореляційний пік. Додавання малого порогу `eps ≈ 10⁻⁶ · P_avg` стабілізує обчислення.

### Оптимізація пам'яті та обчислень (Fixed-point DSP)
У мікроконтролерах без апаратного блоку обчислень з рухомою комою подвійної точності прямий розрахунок тригонометричних функцій `cosf` та `sinf` у циклах БПФ споживає значні обчислювальні ресурси. Для прискорення обробки застосовують попередньо згенеровані таблиці поворотних коефіцієнтів (Twiddle Factors LUT) у статичній пам'яті та перехід до 16/32-бітних форматів з фіксованою комою (Q15 / Q31) із захистом від переповнення при сумуванні метеликів БПФ.
