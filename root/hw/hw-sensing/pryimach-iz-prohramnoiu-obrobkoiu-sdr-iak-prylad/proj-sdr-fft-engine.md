# ⚙️ Потоковий спектральний аналізатор на основі віконного FFT

Потоковий конвеєр спектральної обробки приймає безперервний потік комплексних квадратурних відліків `I(n) + j·Q(n)`, зважує їх віконною функцією з глибоким придушенням бічних пелюсток, виконує швидке перетворення Фур'є (FFT), центрує нульову частоту (`fftshift`), калібрує потужність у шкалу `dBm`, знаходить спектральні піки з суббіновою точністю та усереднює результати для стабілізації шумової доріжки.

## Архітектура та організація потокового конвеєра

Вимірювальний спектральний аналізатор на базі SDR повинен обробляти потік відліків у реальному часі без втрати кадрів (англ. *zero-drop streaming*) із фіксованим детермінованим часом затримки. Якщо обчислювальний потік хоста запізнюється і не встигає спорожняти буфери прямого доступу до пам'яті (DMA), виникає апаратне переповнення черги (англ. *buffer overrun / overflow*), що призводить до непоправного розриву фазової когерентності та спотворення вимірюваного спектра.

```
[ Потік IQ з USB/DMA ]
        │
        ▼
[ Кільцевий буфер (Ring Buffer) ]  ───► Перекриття блоків (Overlap 50%)
        │
        ▼
[ Віконне зважування w[n] ]        ───► Blackman-Harris / Flat-top
        │
        ▼
[ Комплексне FFT (Radix-2) ]       ───► Табличні коефіцієнти повороту (Twiddle)
        │
        ▼
[ Центрування спектра (fftshift) ] ───► Циклічний зсув: DC у центр
        │
        ▼
[ Перерахунок у dBm ]              ───► Калібрувальна константа, поріг відсікання
        │
        ▼
[ Відеоусереднення (IIR / Boxcar) ]───► Згладжування флуктуацій шуму
        │
        ▼
[ Суббіновий пошук піків ]        ───► Параболічна інтерполяція частоти
```

Конвеєр складається із семи послідовних стадій:

1. **Кільцева буферизація та перекриття (Overlap):** Вхідний DMA-потік записується у кільцевий буфер без блокувань (lock-free single-producer single-consumer ring buffer). Для запобігання втраті коротких радіоімпульсів (англ. *Probability of Intercept*, POI), які можуть припасти на край вікна, блоки вибираються з перекриттям 50% або 75%. Кожен новий блок зсувається лише на `N / 2` або `N / 4` відліків;
2. **Віконне зважування:** Множення комплексного вхідного вектора на попередньо розраховану таблицю коефіцієнтів Blackman-Harris для усунення розривів на межах блоку;
3. **Обчислення FFT:** Комплексне перетворення `N` точок (де `N = 2^M`) із використанням кешованих поворотних множників (англ. *twiddle factors*);
4. **Центрування спектра (`fftshift`):** Перестановка половин масиву так, щоб постійна складова (DC, 0 Гц) опинилася в центрі екрана, від'ємні частоти — ліворуч, а додатні — праворуч;
5. **Логарифмічне перетворення у dBm:** Обчислення квадрата модуля кожного комплексного біна `|X[k]|² = Re² + Im²` та переведення у децибел-мілівати з урахуванням когерентної суми вікна `S₁` та опору `50 Ом`;
6. **Відеоусереднення (Video Averaging):** Експоненційне фільтрування шуму за допомогою рекурсивного фільтра першого порядку (IIR), що стабілізує шумову доріжку;
7. **Суббінова параболічна інтерполяція:** Точне визначення частоти та амплітуди піка між дискретними відліками сітки ДПФ.

## Багатопотокова синхронізація та кільцевий буфер

Для забезпечення безперервного прийому прийомний потік (I/O thread) та обчислювальний потік DSP розносяться по різних ядрах процесора. Зв'язок між ними організується через кільцевий буфер із розділеними покажчиками запису (`write_ptr`) та читання (`read_ptr`). 

Покажчики вирівнюються за межею рядка процесорного кешу (`alignas(64)`), щоб запобігти ефекту помилкового спільного використання пам'яті (англ. *false sharing*), коли запис у сусідній байт скидає L1-кеш іншого ядра:

```
[Потік I/O: запис DMA] ───► write_ptr (атомарний реліз)
                                  │
      ┌───┬───┬───┬───┬───┬───┬───▼───┬───┬───┐
      │ 0 │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ 9 │  [Кільцевий масив у RAM]
      └───┴───┴───┴───┴───┴───┴───▲───┴───┴───┘
                                  │
[Потік DSP: читання FFT] ───► read_ptr (атомарне захоплення)
```

При 50% перекритті обчислювальний потік читає `N` відліків, виконує FFT і просуває `read_ptr` вперед лише на `N / 2`. Таким чином, кожен відлік опрацьовується двічі у складі сусідніх вікон, що гарантує 100% ймовірність перехоплення імпульсів тривалістю більше `N / Fs`.

## Реалізація конвеєра на C та C++

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    float i;
    float q;
} complex_sample_t;

typedef struct {
    size_t size;
    float *window;
    complex_sample_t *twiddles;
    complex_sample_t *fft_buffer;
    float *power_spectrum_dbm;
    float *averaged_spectrum;
    float cal_offset_db;
    float alpha;
} sdr_spectrum_analyzer_t;

/* Генерація коефіцієнтів 4-точкового вікна Blackman-Harris */
static void init_blackman_harris(float *w, size_t n) {
    const float a0 = 0.35875f;
    const float a1 = 0.48829f;
    const float a2 = 0.14128f;
    const float a3 = 0.01168f;
    for (size_t i = 0; i < n; ++i) {
        float theta = (2.0f * (float)M_PI * (float)i) / (float)(n - 1);
        w[i] = a0 - a1 * cosf(theta) + a2 * cosf(2.0f * theta) - a3 * cosf(3.0f * theta);
    }
}

/* Попередня генерація поворотних множників для прискорення FFT */
static void init_twiddles(complex_sample_t *tw, size_t n) {
    for (size_t i = 0; i < n / 2; ++i) {
        float angle = -2.0f * (float)M_PI * (float)i / (float)n;
        tw[i].i = cosf(angle);
        tw[i].q = sinf(angle);
    }
}

/* Створення та виділення пам'яті аналізатора */
sdr_spectrum_analyzer_t* sdr_analyzer_create(size_t size, float cal_offset_db, float alpha) {
    if ((size & (size - 1)) != 0 || size == 0) {
        return NULL; /* Розмір має бути строго степенем двійки */
    }
    sdr_spectrum_analyzer_t *sa = (sdr_spectrum_analyzer_t*)calloc(1, sizeof(sdr_spectrum_analyzer_t));
    if (!sa) return NULL;

    sa->size = size;
    sa->cal_offset_db = cal_offset_db;
    sa->alpha = alpha;

    sa->window = (float*)malloc(size * sizeof(float));
    sa->twiddles = (complex_sample_t*)malloc((size / 2) * sizeof(complex_sample_t));
    sa->fft_buffer = (complex_sample_t*)malloc(size * sizeof(complex_sample_t));
    sa->power_spectrum_dbm = (float*)malloc(size * sizeof(float));
    sa->averaged_spectrum = (float*)malloc(size * sizeof(float));

    if (!sa->window || !sa->twiddles || !sa->fft_buffer || 
        !sa->power_spectrum_dbm || !sa->averaged_spectrum) {
        free(sa->window);
        free(sa->twiddles);
        free(sa->fft_buffer);
        free(sa->power_spectrum_dbm);
        free(sa->averaged_spectrum);
        free(sa);
        return NULL;
    }

    init_blackman_harris(sa->window, size);
    init_twiddles(sa->twiddles, size);

    for (size_t i = 0; i < size; ++i) {
        sa->averaged_spectrum[i] = -140.0f; /* Ініціалізація рівнем шуму */
    }
    return sa;
}

void sdr_analyzer_destroy(sdr_spectrum_analyzer_t *sa) {
    if (!sa) return;
    free(sa->window);
    free(sa->twiddles);
    free(sa->fft_buffer);
    free(sa->power_spectrum_dbm);
    free(sa->averaged_spectrum);
    free(sa);
}

/* Швидке перетворення Фур'є Radix-2 за часом (in-place) */
static void radix2_fft(complex_sample_t *x, const complex_sample_t *twiddles, size_t n) {
    /* Біт-реверсна перестановка індексів */
    size_t j = 0;
    for (size_t i = 0; i < n - 1; ++i) {
        if (i < j) {
            complex_sample_t temp = x[i];
            x[i] = x[j];
            x[j] = temp;
        }
        size_t k = n >> 1;
        while (k <= j) {
            j -= k;
            k >>= 1;
        }
        j += k;
    }

    /* Каскади метеликів */
    for (size_t len = 2; len <= n; len <<= 1) {
        size_t half_len = len >> 1;
        size_t step = n / len;
        for (size_t i = 0; i < n; i += len) {
            for (size_t m = 0; m < half_len; ++m) {
                complex_sample_t w = twiddles[m * step];
                complex_sample_t u = x[i + m];
                complex_sample_t v = {
                    x[i + m + half_len].i * w.i - x[i + m + half_len].q * w.q,
                    x[i + m + half_len].i * w.q + x[i + m + half_len].q * w.i
                };
                x[i + m].i = u.i + v.i;
                x[i + m].q = u.q + v.q;
                x[i + m + half_len].i = u.i - v.i;
                x[i + m + half_len].q = u.q - v.q;
            }
        }
    }
}

/* Обробка одного блоку комплексних IQ відліків */
void sdr_analyzer_process(sdr_spectrum_analyzer_t *sa, const complex_sample_t *input) {
    const size_t n = sa->size;
    const size_t half = n / 2;

    /* 1. Віконне зважування вхідного блоку */
    for (size_t i = 0; i < n; ++i) {
        sa->fft_buffer[i].i = input[i].i * sa->window[i];
        sa->fft_buffer[i].q = input[i].q * sa->window[i];
    }

    /* 2. Обчислення FFT */
    radix2_fft(sa->fft_buffer, sa->twiddles, n);

    /* 3. fftshift, розрахунок потужності в dBm та відеоусереднення */
    for (size_t i = 0; i < n; ++i) {
        size_t shifted_idx = (i < half) ? (i + half) : (i - half);

        float re = sa->fft_buffer[i].i;
        float im = sa->fft_buffer[i].q;
        float power_lin = re * re + im * im;

        /* Захист від взяття логарифма нуля */
        if (power_lin < 1e-18f) {
            power_lin = 1e-18f;
        }

        float power_dbm = 10.0f * log10f(power_lin) + sa->cal_offset_db;
        sa->power_spectrum_dbm[shifted_idx] = power_dbm;

        /* Експоненційне відеоусереднення */
        sa->averaged_spectrum[shifted_idx] =
            sa->alpha * power_dbm + (1.0f - sa->alpha) * sa->averaged_spectrum[shifted_idx];
    }
}

/* Суббіновий пошук піка за допомогою параболічної інтерполяції */
void sdr_analyzer_find_peak_interp(const sdr_spectrum_analyzer_t *sa, 
                                   float *peak_bin_out, float *peak_power_out) {
    const size_t n = sa->size;
    size_t max_idx = 1;
    float max_val = sa->averaged_spectrum[1];

    for (size_t i = 2; i < n - 1; ++i) {
        if (sa->averaged_spectrum[i] > max_val) {
            max_val = sa->averaged_spectrum[i];
            max_idx = i;
        }
    }

    /* Параболічна інтерполяція по трьох точках */
    float y_left = sa->averaged_spectrum[max_idx - 1];
    float y_mid = sa->averaged_spectrum[max_idx];
    float y_right = sa->averaged_spectrum[max_idx + 1];

    float denom = (y_left - 2.0f * y_mid + y_right);
    float delta = 0.0f;
    if (fabsf(denom) > 1e-6f) {
        delta = 0.5f * (y_left - y_right) / denom;
    }

    *peak_bin_out = (float)max_idx + delta;
    *peak_power_out = y_mid - 0.25f * (y_left - y_right) * delta;
}
```
```cpp
#include <vector>
#include <span>
#include <complex>
#include <cmath>
#include <numbers>
#include <algorithm>
#include <stdexcept>

struct PeakResult {
    float bin_index;
    float power_dbm;
};

class SdrSpectrumAnalyzer {
public:
    explicit SdrSpectrumAnalyzer(size_t size, float cal_offset_db = 0.0f, float alpha = 0.2f)
        : size_(size), cal_offset_db_(cal_offset_db), alpha_(alpha),
          window_(size), twiddles_(size / 2), fft_buffer_(size), 
          power_spectrum_dbm_(size), averaged_spectrum_(size, -140.0f) {
        if ((size & (size - 1)) != 0 || size == 0) {
            throw std::invalid_argument("FFT size must be a power of two");
        }
        init_blackman_harris();
        init_twiddles();
    }

    void process(std::span<const std::complex<float>> input) {
        if (input.size() != size_) {
            throw std::invalid_argument("Input size mismatch");
        }

        // 1. Віконне зважування
        for (size_t i = 0; i < size_; ++i) {
            fft_buffer_[i] = input[i] * window_[i];
        }

        // 2. Комплексне FFT
        radix2_fft(fft_buffer_, twiddles_);

        // 3. fftshift, розрахунок потужності в dBm та відеоусереднення
        const size_t half = size_ / 2;
        for (size_t i = 0; i < size_; ++i) {
            size_t shifted_idx = (i < half) ? (i + half) : (i - half);
            float power_lin = std::norm(fft_buffer_[i]);
            power_lin = std::max(power_lin, 1e-18f);

            float power_dbm = 10.0f * std::log10(power_lin) + cal_offset_db_;
            power_spectrum_dbm_[shifted_idx] = power_dbm;

            averaged_spectrum_[shifted_idx] =
                alpha_ * power_dbm + (1.0f - alpha_) * averaged_spectrum_[shifted_idx];
        }
    }

    [[nodiscard]] std::span<const float> power_spectrum() const noexcept {
        return power_spectrum_dbm_;
    }

    [[nodiscard]] std::span<const float> averaged_spectrum() const noexcept {
        return averaged_spectrum_;
    }

    [[nodiscard]] PeakResult find_peak_interpolated() const noexcept {
        auto it = std::max_element(averaged_spectrum_.begin() + 1, averaged_spectrum_.end() - 1);
        size_t max_idx = std::distance(averaged_spectrum_.begin(), it);

        float y_left = averaged_spectrum_[max_idx - 1];
        float y_mid = averaged_spectrum_[max_idx];
        float y_right = averaged_spectrum_[max_idx + 1];

        float denom = y_left - 2.0f * y_mid + y_right;
        float delta = 0.0f;
        if (std::abs(denom) > 1e-6f) {
            delta = 0.5f * (y_left - y_right) / denom;
        }

        return {
            .bin_index = static_cast<float>(max_idx) + delta,
            .power_dbm = y_mid - 0.25f * (y_left - y_right) * delta
        };
    }

private:
    void init_blackman_harris() {
        constexpr float a0 = 0.35875f;
        constexpr float a1 = 0.48829f;
        constexpr float a2 = 0.14128f;
        constexpr float a3 = 0.01168f;
        const float pi = std::numbers::pi_v<float>;

        for (size_t i = 0; i < size_; ++i) {
            float theta = (2.0f * pi * static_cast<float>(i)) / static_cast<float>(size_ - 1);
            window_[i] = a0 - a1 * std::cos(theta) + a2 * std::cos(2.0f * theta) - a3 * std::cos(3.0f * theta);
        }
    }

    void init_twiddles() {
        const float pi = std::numbers::pi_v<float>;
        for (size_t i = 0; i < size_ / 2; ++i) {
            float angle = -2.0f * pi * static_cast<float>(i) / static_cast<float>(size_);
            twiddles_[i] = std::complex<float>(std::cos(angle), std::sin(angle));
        }
    }

    static void radix2_fft(std::vector<std::complex<float>>& x, 
                           const std::vector<std::complex<float>>& twiddles) {
        const size_t n = x.size();
        size_t j = 0;
        for (size_t i = 0; i < n - 1; ++i) {
            if (i < j) {
                std::swap(x[i], x[j]);
            }
            size_t k = n >> 1;
            while (k <= j) {
                j -= k;
                k >>= 1;
            }
            j += k;
        }

        for (size_t len = 2; len <= n; len <<= 1) {
            size_t half_len = len >> 1;
            size_t step = n / len;
            for (size_t i = 0; i < n; i += len) {
                for (size_t m = 0; m < half_len; ++m) {
                    std::complex<float> w = twiddles[m * step];
                    std::complex<float> u = x[i + m];
                    std::complex<float> v = x[i + m + half_len] * w;
                    x[i + m] = u + v;
                    x[i + m + half_len] = u - v;
                }
            }
        }
    }

    size_t size_;
    float cal_offset_db_;
    float alpha_;
    std::vector<float> window_;
    std::vector<std::complex<float>> twiddles_;
    std::vector<std::complex<float>> fft_buffer_;
    std::vector<float> power_spectrum_dbm_;
    std::vector<float> averaged_spectrum_;
};
```
:::

## Інженерні пастки та граничні випадки потокового аналізу

1. **Центрування нульової частоти (`fftshift`):** У стандартному масиві дискретного перетворення Фур'є індекс `k = 0` відповідає постійній складовій (0 Гц), індекси `1 .. N/2 - 1` — додатним частотам від `+Δf` до `+Fs/2 - Δf`, а індекси `N/2 .. N - 1` — від'ємним частотам від `-Fs/2` до `-Δf`. Без циклічної перестановки половин масиву спектр на екрані буде розірваним: нульова частота гетеродина опиниться зліва, а не в центрі смуги огляду;
2. **Артефакт постійної складової (DC Spike):** Через пряме просочування гетеродина (LO leakage) та зміщення нуля вхідних АЦП у нульовому біні завжди формується паразитний сплеск. Для його усунення перед FFT застосовують цифровий режекторний фільтр (DC notch filter) або програмне віднімання середнього значення: `I[n] -= mean(I)`, `Q[n] -= mean(Q)`;
3. **Втрата коротких імпульсів без накладання блоків:** Якщо блоки FFT обробляються стик у стик (без перекриття), короткі сигнали, що потрапляють на краї блоку, пригнічуються віконною функцією на 30–90 dB і можуть залишитися непоміченими. Вимірювальні приймачі реалізують ковзне перекриття 50% або 75%, виконуючи обчислення FFT у 2–4 рази частіше за тривалість вікна;
4. **Захист від субнормальних чисел і ділення на нуль:** При розрахунку `10 · log10(power)` за відсутності сигналу потужність шуму на окремих бінах може наближатися до абсолютного нуля машинного представлення `float` (subnormal float), що викликає переповнення або деградацію продуктивності FPU. Обов'язковим є попереднє затискання аргументу логарифма знизу на рівні `10⁻¹⁸` (-180 dB);
5. **Суббінова точність частоти:** Крок сітки FFT становить `Δf_bin = Fs / N`. Якщо гармонічний сигнал знаходиться між бінами, просте взяття дискретного індексу дає похибку до `±0.5 · Δf_bin`. Параболічна інтерполяція по трьох найближчих спектральних відліках уточнює дійсну частоту коливань у 10–20 разів точніше за крок біна;
6. **Обмеження пропускної здатності L1/L2 кешу процесора:** При великих розмірах перетворення (`N ≥ 16384` відліки) робочий буфер комплексних чисел займає понад 128 КБ, виходячи за межі швидкого кешу першого рівня (L1 Data Cache). Для збереження частоти оновлення понад 60 кадрів на секунду застосовують розбиття алгоритму Кулі-Тюкі на кашево-оптимізовані блоки (cache-oblivious / Radix-4) та вирівняні інструкції AVX2/AVX-512.
