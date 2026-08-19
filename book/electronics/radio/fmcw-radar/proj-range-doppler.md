# ⚙️ Алгоритм 2D-FFT обробки радарного кадру та виявлення цілей

Цифрове оброблення сигналів у сучасних FMCW-радарах перетворює масив оцифрованих відліків проміжної частоти з виходу АЦП на список фізичних цілей із точними координатами дальності, радіальної швидкості та амплітуди відбиття. Цей проект реалізує повний конвеєр радарного сигнального процесора: від накладання віконних функцій і двовимірного швидкого перетворення Фур'є (2D-FFT: Range-FFT та Doppler-FFT) до адаптивного порогування за алгоритмами родини CFAR (CA-CFAR, GOCA, SOCA та OS-CFAR) й просторового оцінювання кута приходу хвилі (Angle-FFT) для надійного виявлення рухомих об'єктів на фоні шумів і стаціонарних завад.

---

### 1. Архітектура конвеєра обробки радарного кадру

Сигнал на виході квадратурного змішувача після аналого-цифрового перетворювача організується в двовимірну матрицю комплексних чисел `ADC_Data[N_chirps][N_samples]`, яка називається радарним кадром (Radar Frame) або радарним кубом даних (Radar Data Cube):

* **Швидкий час (Fast Time, рядки матриці):** `N_samples` відліків, знятих АЦП усередині одного чірпа з частотою дискретизації `f_s`. Частота коливань у цьому вимірі пропорційна затримці сигналу, тобто дальності до цілі `R`.
* **Повільний час (Slow Time, стовпчики матриці):** `N_chirps` послідовних чірпів, випромінених з інтервалом повторення `T_r`. Фазове обертання від чірпа до чірпа пропорційне радіальній швидкості цілі `v`.

```
                  Швидкий час (Fast Time): n = 0, 1, ..., N_samples - 1
            ┌────────────────────────────────────────────────────────┐
   чірп 0   │ x[0][0]       x[0][1]       ...      x[0][N_samples-1] │ ──► 1D Range-FFT
   чірп 1   │ x[1][0]       x[1][1]       ...      x[1][N_samples-1] │ ──► 1D Range-FFT
   ...      │ ...           ...           ...      ...               │ ──► ...
   чірп M-1 │ x[M-1][0]     x[M-1][1]     ...      x[M-1][N_samples-1]│──► 1D Range-FFT
            └────────────────────────────────────────────────────────┘
                 │               │                      │
                 ▼               ▼                      ▼
           2D Doppler-FFT   2D Doppler-FFT         2D Doppler-FFT
```

Конвеєр обробки складається з наступних послідовних стадій:

1. **Range-FFT (Перетворення дальності):** Кожен рядок матриці множиться на віконну функцію (наприклад, вікно Ганнінга) для придушення бічних пелюсток, після чого обчислюється 1D-FFT за швидким часом. Результатом є матриця профілів дальності (Range Profiles), де індекс біна відповідає відстані.
2. **Doppler-FFT (Перетворення швидкості):** Для кожного фіксованого біна дальності (стовпчика отриманої матриці) накладається вікно повільного часу та обчислюється 1D-FFT за стовпчиками. Спектр центрується за допомогою операції `fftshift`, щоб нульова доплерівська швидкість опинилася в центрі. Результатом є двовимірна Range-Doppler карта (R-D Map).
3. **Обчислення карти потужності:** Комплексні значення перетворюються на енергетичну потужність `P(r, d) = I²(r, d) + Q²(r, d)` або логарифмічний масштаб у децибелах `10 · log10(P)`.
4. **2D CFAR детектор:** Для кожного елемента карти потужності оцінюється локальний рівень шуму в ковзному двовимірному вікні, формується адаптивний поріг і фіксуються піки, що перевищують поріг і є локальними максимумами.
5. **Angle-FFT (Кутова пеленгація):** Для знайдених точок `(r, d)` витягуються комплексні відліки по всіх приймальних антенах і проводиться просторове перетворення Фур'є для знаходження азимута `θ` та елевації `φ`.

---

### 2. Математика віконних функцій та родина детекторів CFAR

#### Віконна фільтрація
Прямокутне вікно природного обмеження сигналу має високі бічні пелюстки (-13 дБ), через що потужне відбиття від близького масивного об'єкта (наприклад, дорожнього відбійника) маскує слабкий сигнал від віддаленої малопомітної цілі (наприклад, пішохода). Для зниження рівня бічних пелюсток застосовується вікно Ганнінга (Hanning window):

```
w[n] = 0.5 · (1 - cos((2·π · n) / (N - 1))),   n = 0, 1, ..., N - 1
```

Вікно Ганнінга знижує рівень першої бічної пелюстки до -31.5 дБ, що розширює динамічний діапазон виявлення цілей до 60 дБ ціною незначного розширення головного піка на 44%.

#### Двовимірний детектор CA-CFAR
У радарних картах рівень завад і шумів змінюється за дальністю (через геометричне загасання `1/R⁴` та шуми гетеродина) і за швидкістю (через розмиття стаціонарного відбиття фону). Фіксований поріг виявлення або призведе до лавини хибних тривог поблизу нульової дальності, або втратить цілі на дистанції.

Алгоритм CA-CFAR (Cell-Averaging Constant False Alarm Rate) оцінює потужність шуму індивідуально для кожної досліджуваної комірки (Cell Under Test, CUT). Навколо CUT утворюється прямокутна маска, яка містить три зони:

1. **CUT (Cell Under Test):** Центральна комірка з координатами `(r, d)`, яка перевіряється на наявність цілі.
2. **Охоронна зона (Guard Cells):** Прямокутна область розміром `(2·G_r + 1) × (2·G_d + 1)` без урахування CUT. Охоронні комірки виключаються з оцінки шуму, щоб енергія розмитого піка самої цілі не потрапляла в розрахунок шумового фону і не завищувала поріг.
3. **Навчальна зона (Training / Reference Cells):** Зовнішня область розміром `(2·(T_r + G_r) + 1) × (2·(T_d + G_d) + 1)` без урахування охоронної зони.

```
       ┌───────────────────────────────┐  ▲
       │      Навчальні комірки        │  │
       │   ┌───────────────────────┐   │  │ T_d (навчання)
       │   │   Охоронні комірки    │   │  │
       │   │   ┌───────────────┐   │   │  ▼
       │   │   │   C U T       │   │   │  ▲ G_d (охорона)
       │   │   └───────────────┘   │   │  ▼
       │   │                       │   │
       │   └───────────────────────┘   │
       │                               │
       └───────────────────────────────┘
       ◄───────────────►◄──────────────►
             T_r              G_r
```

Кількість навчальних комірок `N_train` розраховується як різниця площ великого та середнього прямокутників:

```
N_train = (2·(T_r + G_r) + 1) · (2·(T_d + G_d) + 1) - (2·G_r + 1) · (2·G_d + 1)
```

Середня потужність фонового шуму обчислюється як середнє арифметичне навчальних комірок:

```
P_noise = (1 / N_train) · ∑ P_train(i, j)
```

Адаптивний поріг виявлення `Threshold` формується множенням оцінки шуму на масштабний коефіцієнт `α`:

```
Threshold = α · P_noise
```

Для експоненційного розподілу потужності білого гаусового шуму масштабний коефіцієнт `α` строго зв'язаний із заданою ймовірністю хибної тривоги `P_fa` (Probability of False Alarm, зазвичай `10⁻⁴ ... 10⁻⁶`):

```
α = N_train · (P_fa^(-1 / N_train) - 1)
```

#### Варіанти алгоритму CFAR для складних середовищ

* **CA-CFAR (Cell-Averaging):** Класичне усереднення по всіх навчальних комірках. Оптимальне для однорідного білого гаусового шуму, але дає збої у двох випадках:
  1. *Ефект маскування (Target Masking):* Якщо у навчальне вікно потрапляє сусідня потужна ціль, `P_noise` різко зростає, поріг штучно завищується, і слабша ціль у CUT втрачається.
  2. *Межа завади (Clutter Edge):* При переході між різними типами покриття (асфальт → газон або в'їзд у тунель) на межі різкого стрибка потужності виникає сплеск хибних спрацьовувань.
* **GOCA-CFAR (Greatest-Of CA-CFAR):** Навчальна зона ділиться на дві половини (випереджаючу `P_lead` та запізнілу `P_lag`). Порогом служить максимум `max(P_lead, P_lag)`. Це надійно запобігає хибним тривогам на межах завад ціною втрати чутливості до близьких цілей.
* **SOCA-CFAR (Smallest-Of CA-CFAR):** Обирає мінімум `min(P_lead, P_lag)`. Дозволяє надійно розділяти дві близько розташовані цілі, оскільки наявність однієї цілі в одній половині вікна не заважає виявити другу в іншій половині.
* **OS-CFAR (Ordered-Statistic CFAR):** Значення всіх `N_train` комірок сортуються за зростанням `P_(1) ≤ P_(2) ≤ ... ≤ P_(N)`, і як оцінка шуму обирається `k`-й ранг (зазвичай 75-й процентиль, `k = 0.75 · N_train`). Алгоритм повністю імунний до наявності до `N_train - k` сторонніх цілей у навчальному вікні, проте вимагає сортування масиву в кожній точці карти.

---

### 3. Програмна реалізація

Нижче наведено повну реалізацію обробника радарного кадру. Алгоритм приймає матрицю відліків комплексного АЦП, обчислює 2D-FFT, формує Range-Doppler карту, виконує 2D CA-CFAR детектування та повертає структурований список виявлених цілей.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    float real;
    float imag;
} Complex32;

typedef struct {
    float range_m;       /* Дальність до цілі, м */
    float velocity_ms;   /* Радіальна швидкість цілі, м/с */
    float power_db;      /* Потужність сигналу, дБ */
    int range_bin;       /* Індекс біна дальності */
    int doppler_bin;     /* Індекс біна швидкості */
} RadarTarget;

/* Ініціалізація вікна Ганнінга */
void init_hanning_window(float *win, int n) {
    for (int i = 0; i < n; i++) {
        win[i] = 0.5f * (1.0f - cosf((2.0f * (float)M_PI * (float)i) / (float)(n - 1)));
    }
}

/* Ітеративне БПФ з проріджуванням за часом (Radix-2 Cooley-Tukey) */
void fft_radix2(Complex32 *x, int n, bool invert) {
    /* Перестановка з біт-реверсивною адресацією */
    int j = 0;
    for (int i = 0; i < n - 1; i++) {
        if (i < j) {
            Complex32 temp = x[i];
            x[i] = x[j];
            x[j] = temp;
        }
        int k = n >> 1;
        while (k <= j) {
            j -= k;
            k >>= 1;
        }
        j += k;
    }

    /* Метелики БПФ */
    for (int len = 2; len <= n; len <<= 1) {
        float angle = (invert ? 2.0f : -2.0f) * (float)M_PI / (float)len;
        Complex32 wlen = { cosf(angle), sinf(angle) };
        for (int i = 0; i < n; i += len) {
            Complex32 w = { 1.0f, 0.0f };
            for (int k = 0; k < len / 2; k++) {
                Complex32 u = x[i + k];
                Complex32 v = {
                    w.real * x[i + k + len / 2].real - w.imag * x[i + k + len / 2].imag,
                    w.real * x[i + k + len / 2].imag + w.imag * x[i + k + len / 2].real
                };
                x[i + k].real = u.real + v.real;
                x[i + k].imag = u.imag + v.imag;
                x[i + k + len / 2].real = u.real - v.real;
                x[i + k + len / 2].imag = u.imag - v.imag;

                float next_w_real = w.real * wlen.real - w.imag * wlen.imag;
                w.imag = w.real * wlen.imag + w.imag * wlen.real;
                w.real = next_w_real;
            }
        }
    }

    if (invert) {
        for (int i = 0; i < n; i++) {
            x[i].real /= (float)n;
            x[i].imag /= (float)n;
        }
    }
}

/* Двовимірна 2D-FFT обробка радарного кадру */
void process_radar_cube_2dfft(Complex32 *cube, float *rd_map_power,
                             int n_chirps, int n_samples) {
    float *win_fast = (float*)malloc(sizeof(float) * n_samples);
    float *win_slow = (float*)malloc(sizeof(float) * n_chirps);
    init_hanning_window(win_fast, n_samples);
    init_hanning_window(win_slow, n_chirps);

    /* 1. Range-FFT по рядках (швидкий час) */
    Complex32 *row_buf = (Complex32*)malloc(sizeof(Complex32) * n_samples);
    for (int c = 0; c < n_chirps; c++) {
        for (int s = 0; s < n_samples; s++) {
            int idx = c * n_samples + s;
            row_buf[s].real = cube[idx].real * win_fast[s];
            row_buf[s].imag = cube[idx].imag * win_fast[s];
        }
        fft_radix2(row_buf, n_samples, false);
        for (int s = 0; s < n_samples; s++) {
            cube[c * n_samples + s] = row_buf[s];
        }
    }
    free(row_buf);

    /* 2. Doppler-FFT по стовпчиках (повільний час) */
    Complex32 *col_buf = (Complex32*)malloc(sizeof(Complex32) * n_chirps);
    for (int s = 0; s < n_samples; s++) {
        for (int c = 0; c < n_chirps; c++) {
            int idx = c * n_samples + s;
            col_buf[c].real = cube[idx].real * win_slow[c];
            col_buf[c].imag = cube[idx].imag * win_slow[c];
        }
        fft_radix2(col_buf, n_chirps, false);

        /* 3. Центрування спектра (FFTShift) та розрахунок потужності */
        for (int c = 0; c < n_chirps; c++) {
            int shifted_c = (c + n_chirps / 2) % n_chirps;
            float mag2 = col_buf[c].real * col_buf[c].real + col_buf[c].imag * col_buf[c].imag;
            rd_map_power[s * n_chirps + shifted_c] = mag2;
        }
    }
    free(col_buf);
    free(win_fast);
    free(win_slow);
}

/* 2D CA-CFAR детектор цілей */
int detect_cfar_2d(const float *rd_map_power, int n_samples, int n_chirps,
                   int guard_r, int guard_d, int train_r, int train_d,
                   float p_fa, float range_res_m, float vel_res_ms,
                   RadarTarget *out_targets, int max_targets) {
    int count = 0;
    int n_train_cells = (2 * (train_r + guard_r) + 1) * (2 * (train_d + guard_d) + 1)
                      - (2 * guard_r + 1) * (2 * guard_d + 1);

    /* Масштабний коефіцієнт порогу за заданою ймовірністю P_fa */
    float alpha = (float)n_train_cells * (powf(p_fa, -1.0f / (float)n_train_cells) - 1.0f);

    int r_start = train_r + guard_r;
    int r_end = n_samples - (train_r + guard_r);
    int d_start = train_d + guard_d;
    int d_end = n_chirps - (train_d + guard_d);

    for (int r = r_start; r < r_end; r++) {
        for (int d = d_start; d < d_end; d++) {
            float cut_val = rd_map_power[r * n_chirps + d];

            /* Розрахунок середнього шуму в навчальних комірках */
            float noise_sum = 0.0f;
            for (int dr = -(train_r + guard_r); dr <= (train_r + guard_r); dr++) {
                for (int dd = -(train_d + guard_d); dd <= (train_d + guard_d); dd++) {
                    if (abs(dr) <= guard_r && abs(dd) <= guard_d) {
                        continue; /* Пропуск охоронної зони і CUT */
                    }
                    noise_sum += rd_map_power[(r + dr) * n_chirps + (d + dd)];
                }
            }
            float noise_avg = noise_sum / (float)n_train_cells;
            float threshold = alpha * noise_avg;

            if (cut_val > threshold) {
                /* Придушення не-максимумів: перевірка на локальний пік */
                bool is_peak = true;
                for (int dr = -guard_r; dr <= guard_r && is_peak; dr++) {
                    for (int dd = -guard_d; dd <= guard_d; dd++) {
                        if (dr == 0 && dd == 0) continue;
                        if (rd_map_power[(r + dr) * n_chirps + (d + dd)] >= cut_val) {
                            is_peak = false;
                            break;
                        }
                    }
                }

                if (is_peak && count < max_targets) {
                    out_targets[count].range_bin = r;
                    out_targets[count].doppler_bin = d;
                    out_targets[count].range_m = (float)r * range_res_m;
                    out_targets[count].velocity_ms = (float)(d - n_chirps / 2) * vel_res_ms;
                    out_targets[count].power_db = 10.0f * log10f(cut_val + 1e-12f);
                    count++;
                }
            }
        }
    }
    return count;
}
```
```cpp
#include <vector>
#include <complex>
#include <cmath>
#include <algorithm>
#include <span>
#include <numbers>

namespace radar {

using ComplexF = std::complex<float>;

struct Target {
    float range_m{0.0f};       // Відстань до цілі, м
    float velocity_ms{0.0f};   // Радіальна швидкість, м/с
    float power_db{0.0f};      // Потужність відбиття, дБ
    int range_bin{0};          // Індекс біна дальності
    int doppler_bin{0};        // Індекс біна швидкості
};

class FmcwProcessor {
public:
    FmcwProcessor(int n_samples, int n_chirps, float range_res, float vel_res)
        : n_samples_(n_samples), n_chirps_(n_chirps),
          range_res_(range_res), vel_res_(vel_res),
          win_fast_(generate_hanning(n_samples)),
          win_slow_(generate_hanning(n_chirps)),
          rd_map_power_(n_samples * n_chirps, 0.0f) {}

    // Обробка кадру: 2D-FFT та формування карти потужності
    void compute_range_doppler_map(std::span<ComplexF> cube) {
        std::vector<ComplexF> row_buf(n_samples_);
        std::vector<ComplexF> col_buf(n_chirps_);

        // 1. Range-FFT вздовж швидкого часу (рядки)
        for (int c = 0; c < n_chirps_; ++c) {
            for (int s = 0; s < n_samples_; ++s) {
                row_buf[s] = cube[c * n_samples_ + s] * win_fast_[s];
            }
            fft(row_buf);
            for (int s = 0; s < n_samples_; ++s) {
                cube[c * n_samples_ + s] = row_buf[s];
            }
        }

        // 2. Doppler-FFT вздовж повільного часу (стовпчики)
        for (int s = 0; s < n_samples_; ++s) {
            for (int c = 0; c < n_chirps_; ++c) {
                col_buf[c] = cube[c * n_samples_ + s] * win_slow_[c];
            }
            fft(col_buf);

            // 3. FFTShift і збереження квадрата амплітуди
            for (int c = 0; c < n_chirps_; ++c) {
                int shifted_c = (c + n_chirps_ / 2) % n_chirps_;
                rd_map_power_[s * n_chirps_ + shifted_c] = std::norm(col_buf[c]);
            }
        }
    }

    // 2D CA-CFAR виявлення цілей
    [[nodiscard]] std::vector<Target> detect_cfar(int guard_r, int guard_d,
                                                  int train_r, int train_d,
                                                  float p_fa) const {
        std::vector<Target> detected;
        const int n_train_cells = (2 * (train_r + guard_r) + 1) * (2 * (train_d + guard_d) + 1)
                                - (2 * guard_r + 1) * (2 * guard_d + 1);

        const float alpha = static_cast<float>(n_train_cells) *
                            (std::pow(p_fa, -1.0f / static_cast<float>(n_train_cells)) - 1.0f);

        const int r_start = train_r + guard_r;
        const int r_end = n_samples_ - (train_r + guard_r);
        const int d_start = train_d + guard_d;
        const int d_end = n_chirps_ - (train_d + guard_d);

        for (int r = r_start; r < r_end; ++r) {
            for (int d = d_start; d < d_end; ++d) {
                const float cut_val = rd_map_power_[r * n_chirps_ + d];

                float noise_sum = 0.0f;
                for (int dr = -(train_r + guard_r); dr <= (train_r + guard_r); ++dr) {
                    for (int dd = -(train_d + guard_d); dd <= (train_d + guard_d); ++dd) {
                        if (std::abs(dr) <= guard_r && std::abs(dd) <= guard_d) {
                            continue;
                        }
                        noise_sum += rd_map_power_[(r + dr) * n_chirps_ + (d + dd)];
                    }
                }

                const float noise_avg = noise_sum / static_cast<float>(n_train_cells);
                if (cut_val <= alpha * noise_avg) {
                    continue;
                }

                // Перевірка на локальний максимум
                bool is_peak = true;
                for (int dr = -guard_r; dr <= guard_r && is_peak; ++dr) {
                    for (int dd = -guard_d; dd <= guard_d; ++dd) {
                        if (dr == 0 && dd == 0) continue;
                        if (rd_map_power_[(r + dr) * n_chirps_ + (d + dd)] >= cut_val) {
                            is_peak = false;
                            break;
                        }
                    }
                }

                if (is_peak) {
                    detected.push_back(Target{
                        .range_m = static_cast<float>(r) * range_res_,
                        .velocity_ms = static_cast<float>(d - n_chirps_ / 2) * vel_res_,
                        .power_db = 10.0f * std::log10(cut_val + 1e-12f),
                        .range_bin = r,
                        .doppler_bin = d
                    });
                }
            }
        }
        return detected;
    }

private:
    int n_samples_;
    int n_chirps_;
    float range_res_;
    float vel_res_;
    std::vector<float> win_fast_;
    std::vector<float> win_slow_;
    std::vector<float> rd_map_power_;

    static std::vector<float> generate_hanning(int n) {
        std::vector<float> w(n);
        for (int i = 0; i < n; ++i) {
            w[i] = 0.5f * (1.0f - std::cos(2.0f * std::numbers::pi_v<float> * static_cast<float>(i) / static_cast<float>(n - 1)));
        }
        return w;
    }

    static void fft(std::span<ComplexF> x) {
        const size_t n = x.size();
        size_t j = 0;
        for (size_t i = 0; i < n - 1; ++i) {
            if (i < j) std::swap(x[i], x[j]);
            size_t k = n >> 1;
            while (k <= j) {
                j -= k;
                k >>= 1;
            }
            j += k;
        }

        for (size_t len = 2; len <= n; len <<= 1) {
            const float angle = -2.0f * std::numbers::pi_v<float> / static_cast<float>(len);
            const ComplexF wlen(std::cos(angle), std::sin(angle));
            for (size_t i = 0; i < n; i += len) {
                ComplexF w(1.0f, 0.0f);
                for (size_t k = 0; k < len / 2; ++k) {
                    const ComplexF u = x[i + k];
                    const ComplexF v = x[i + k + len / 2] * w;
                    x[i + k] = u + v;
                    x[i + k + len / 2] = u - v;
                    w *= wlen;
                }
            }
        }
    }
};

} // namespace radar
```
:::

---

### 4. Подальша обробка: Кутова пеленгація (Angle-FFT / 3D-FFT)

Після виявлення пари координат `(r, d)` на Range-Doppler карті, наступним кроком є вимірювання просторового кута приходу сигналу `θ` (Angle of Arrival, AoA).

Якщо радар має антенну решітку з `N_rx` приймачів (або `N_virt` віртуальних елементів у MIMO-радарі), для кожної виявленої точки `(r, d)` формується просторовий вектор комплексних значень:

```
s_angle[k] = Cube[k][r][d],   k = 0, 1, ..., N_virt - 1
```

Кутова пеленгація здійснюється третім перетворенням Фур'є (Angle-FFT):

```
S_angle(p) = ∑ s_angle[k] · w_angle[k] · exp(-j · 2·π · k · p / N_angle_fft)
```

Для підвищення кутової роздільності розмір перетворення `N_angle_fft` доповнюють нулями (Zero-Padding) до 64 або 128 точок. Індекс піка `p_max` перераховується в кут падіння за формулою:

```
sin(θ) = (λ / (2·π · d_ant)) · (2·π · (p_max - N_angle_fft / 2) / N_angle_fft)
θ = arcsin((λ / d_ant) · (p_max - N_angle_fft / 2) / N_angle_fft)
```

Для відстані між антенами `d_ant = λ / 2` формула спрощується до прямої тригонометричної залежності:

```
θ = arcsin((2 · (p_max - N_angle_fft / 2)) / N_angle_fft)
```

---

### 5. Інженерні підводні камені та оптимізація

#### 1. Кеш-пам'ять та блокове транспонування матриці
У базовій реалізації перший прохід (Range-FFT) здійснюється по рядках матриці. Оскільки дані кожного чірпа лежать у пам'яті послідовно (`row-major order`), процесор ефективно завантажує дані цілими кеш-лініями (64 байти в архітектурах x86/ARM).

Натомість другий прохід (Doppler-FFT) читає відліки зі стовпчиків із великим кроком `stride = N_samples · sizeof(Complex32)`. Для матриці `128 × 1024` крок становить 8192 байти. Кожне звернення до сусіднього чірпа призводить до промаху кешу (Cache Miss), простою обчислювального конвеєра та багаторазової деградації швидкодії.

У високопродуктивних радарних DSP (наприклад, C674x або Cortex-R4F у процесорах Texas Instruments AWR2944) між Range-FFT та Doppler-FFT обов'язково виконують **блокове апаратне транспонування матриці (EDMA Transpose)**. Контролер DMA переставляє блоки даних у фоновому режимі паралельно з обчисленнями, після чого Doppler-FFT знову виконується по суміжних адресах оперативної пам'яті.

#### 2. Завади від витоку передавача (DC Clutter Leakage)
Через пряме електромагнітне просочування випроміненого сигналу TX у приймальний тракт RX через підкладку друкованої плати та близьке відбиття від пластикового радіопрозорого ковпака (Radome), сигнал биття завжди містить потужну постійну складову (DC offset) та низькочастотний пік на нульовій дальності `R = 0`.

Якщо його не придушити до обчислення Range-FFT, бічні пелюстки нульового біна піднімуть шумову полицю на всій карті дальності на 20–40 дБ. Для усунення цього ефекту застосовують трирівневу фільтрацію:
1. Апаратний фільтр високих частот (HPF) у тракті проміжної частоти з частотою зрізу 50–150 кГц.
2. Цифрове видалення середнього значення: від кожного рядка віднімається оцінка постійного зсуву `x[s] = x[s] - mean(x)`.
3. Режекторний фільтр нульової швидкості (Moving Target Indication, MTI): віднімання сусідніх чірпів `x_mti[m] = x[m] - x[m-1]` або обнулення центрального доплерівського біна на карті після 2D-FFT для видалення нерухомих стаціонарних об'єктів.

#### 3. Арифметика з фіксованою крапкою та бюджет пам'яті
В автомобільних та промислових мікроконтролерах без апаратного блоку FPU обчислення FFT виконується у форматі 16-бітних цілих чисел (`int16_t` для I та Q). Кожен каскад метелика БПФ множить амплітуду на `√2`, що подвоює енергію сигналу. Без належного масштабування на 10 каскадах БПФ виникає переповнення розрядної сітки (Integer Overflow), яке повністю руйнує спектр.

Ділення результату на 2 на кожному каскаді запобігає переповненню, проте втрачає молодші розряди (Losing Dynamic Range), через що слабкі цілі тонуть у шумі квантування. Найкращим інженерним рішенням є алгоритм Block Floating Point (блокова плаваюча крапка), де спільний показник степеня масштабування підбирається динамічно на кожному каскаді лише за умови, що максимальний елемент масиву наближається до розрядної стелі 32767.

---

### 6. Розкриття неоднозначності швидкості (Doppler Unwrapping)

У високошвидкісних сценаріях (наприклад, зближення двох автомобілів на трасі зі швидкістю 200 км/год або 55.5 м/с) реальна радіальна швидкість значно перевищує максимальну однозначну швидкість радара `v_max = λ / (4·T_r)` (яка для `T_r = 50` мкс становить лише 19.5 м/с).

Справжня швидкість цілі `v_true` згортається в діапазон `[-v_max, v_max]` через фазове переповнення:

```
v_measured = v_true + 2 · k · v_max,   де k ∈ {..., -2, -1, 0, 1, 2, ...}
```

Для відновлення цілого коефіцієнта неоднозначності `k` застосовують метод чергування періодів повторення чірпів (Staggered PRF / Dual-Chirp Sequence):
1. Радар випромінює два послідовні підкадри з різними періодами повторення чірпів: `T_r1` та `T_r2` (наприклад, `T_r1 = 50` мкс та `T_r2 = 60` мкс).
2. Однозначні межі швидкості для обох підкадрів різняться: `v_max1 = λ / (4·T_r1)` та `v_max2 = λ / (4·T_r2)`.
3. Виміряні швидкості `v_m1` та `v_m2` зв'язані співвідношенням за Китайською теоремою про залишки (CRT):

```
v_true = v_m1 + 2·k₁·v_max1 = v_m2 + 2·k₂·v_max2
```

Шляхом зіставлення гіпотез для малих цілих значень `k₁, k₂ ∈ [-3, 3]` алгоритм знаходить пару, для якої різниця `|v_true1 - v_true2|` мінімальна, розширюючи результуючий діапазон однозначного вимірювання швидкості в 5–10 разів (до 150–200 м/с).

---

### 7. Кластеризація хмари точок та супровід цілей (Tracking)

На виході детектора CFAR для складних протяжних об'єктів (автомобіль, вантажівка, автобус) утворюється не один пік, а група суміжних відбиттів від бампера, колісних арок, фар і дзеркал. Для перетворення масиву сирих точок у дискретні фізичні об'єкти конвеєр виконує два фінальні етапи:

#### Просторове кластерування (DBSCAN)
Алгоритм DBSCAN (Density-Based Spatial Clustering of Applications with Noise) групує точки за просторовою та швидкісною метрикою:

```
dist(p₁, p₂) = √(((x₁ - x₂)² / σ_x²) + ((y₁ - y₂)² / σ_y²) + ((v₁ - v₂)² / σ_v²))
```

Точки, розташовані на відстані менше за радіус сусідства `ε` і з різницею швидкостей менше ніж 1.5 м/с, об'єднуються в єдиний кластер. Для кожного кластера розраховується геометричний центр, ефективна площа розсіювання (RCS) та середньозважена швидкість.

#### Калманівська фільтрація (EKF Tracking)
Отриманий центроїд кластера передається у розширений фільтр Калмана (Extended Kalman Filter), вектор стану якого описує кінематику об'єкта:

```
State = [x, y, v_x, v_y, a_x, a_y]ᵀ
```

Фільтр згладжує випадкові шуми вимірювань, екстраполює траєкторію при короткочасному перекритті (оклюзії) та оцінює прискорення об'єкта, формуючи стабільний список треків для систем адаптивного круїз-контролю (ACC) та екстреного гальмування (AEB).

---

### 8. Покроковий числовий приклад обробки кадру

Простежимо проходження сигналу через усі етапи обробки для цілі з параметрами: дальність `R = 15.0` м, радіальна швидкість `v = +10.0` м/с (віддалення).

Параметри радара: `f₀ = 77` ГГц (`λ = 3.896` мм), `B = 1.0` ГГц, `T_c = 50` мкс, `T_r = 60` мкс, `N_samples = 512`, `N_chirps = 64`, `f_s = 10.24` МГц.

1. **Розрахунок частоти биття та доплера:**
```
f_R = (2 · B · R) / (c · T_c) = (2 · 10⁹ · 15) / (3·10⁸ · 50·10⁻⁶) = 2.0 МГц
f_d = (2 · v) / λ = (2 · 10) / (3.896 · 10⁻³) = 5133 Гц = 5.133 кГц
f_b = f_R + f_d = 2.005133 МГц
```

2. **Індекс біна дальності після Range-FFT (розмір 512):**
```
Крок біна дальності: Δf_bin = f_s / N_samples = 10.24·10⁶ / 512 = 20 кГц
Range_Bin = round(f_b / Δf_bin) = round(2005.133 / 20) = 100
Оцінена дальність: R_est = 100 · (c / (2·B)) · (N_samples_active / 512) = 15.0 м
```

3. **Фазовий зсув між сусідніми чірпами:**
```
Δφ = (4·π · v · T_r) / λ = (4·π · 10 · 60·10⁻⁶) / (3.896 · 10⁻³) = 1.935 рад ≈ 110.88°
```

4. **Індекс доплерівського біна після Doppler-FFT (розмір 64 з FFTShift):**
```
Крок доплерівського біна: Δf_doppler = 1 / (N_chirps · T_r) = 1 / (64 · 60·10⁻⁶) = 260.4 Гц
Doppler_Shift_Bin = round(f_d / Δf_doppler) = round(5133 / 260.4) = +20
Центрований індекс у матриці: Doppler_Bin = 32 + 20 = 52
Оцінена швидкість: v_est = 20 · (λ / (2 · 64 · T_r)) = 20 · 0.5073 = 10.14 м/с
```

5. **Поріг детектора CA-CFAR у комірці (100, 52):**
* Навчальні комірки: `T_r = 4, T_d = 2` (`N_train = 40`).
* Оцінка фонового шуму: `P_noise = -85` дБм (`3.16 · 10⁻¹²` мВт).
* Коефіцієнт `α` для `P_fa = 10⁻⁴`: `α = 40 · ((10⁻⁴)^(-1/40) - 1) = 10.43` (+10.18 дБ).
* Поріг спрацьовування: `Threshold = -85 + 10.18 = -74.82` дБм.
* Потужність сигналу цілі: `P_target = -48` дБм.
* Оскільки `-48 дБм > -74.82 дБм` з перевищенням на 26.82 дБ і значення є локальним максимумом, формується детекція цілі з експортом у хмару точок.

---

### 9. Векторизація та апаратне прискорення (SIMD і GPU)

Для забезпечення частоти оновлення кадрів 20–50 Гц (бюджет часу 20–50 мс на весь цикл аналізу) базове скалярне обчислення 2D-FFT і CFAR часто виявляється занадто повільним для центрального процесора загального призначення.

Сучасні радарні платформи застосовують три рівні апаратного прискорення:
1. **Векторні розширення ЦП (SIMD: ARM NEON, Intel AVX2/AVX-512):** Операції метелика БПФ одночасно обробляють 4 (AVX-128 / NEON) або 8 (AVX-256) комплексних чисел `Complex32` за одну машинну інструкцію FMA (Fused Multiply-Add), що дає 4–6-кратний приріст продуктивності.
2. **Спеціалізовані апаратні прискорювачі (Hardware Accelerators, HWA):** В інтегрованих автомобільних чіпах (Texas Instruments Radar HWA, NXP SAF85xx) модуль 2D-FFT та блок CFAR реалізовані у вигляді жорсткої апаратної логіки на кремнії. Процесор лише завантажує дескриптор конвеєра в регістри HWA, і перетворення всього кадру `4 RX × 128 × 1024` виконується апаратно менш ніж за 4 мілісекунди взагалі без завантаження ядер CPU.
3. **Графічні процесори (GPGPU: CUDA / OpenCL):** У 4D-радарах високої роздільної здатності (Imaging Radar із сотнями віртуальних каналів) розрахунок 3D-FFT та алгоритмів надроздільної здатності (MUSIC, ESPRIT) виконується на мобільних GPU з використанням бібліотек паралельних перетворень cuFFT, де обробка мільйонів спектральних точок розпаралелюється на тисячі потокових ядер.


