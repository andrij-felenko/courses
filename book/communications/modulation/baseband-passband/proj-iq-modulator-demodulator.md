# ⚙️ Моделювання квадратурного модулятора та демодулятора

Симуляція квадратурного переносу сигналів (Up-conversion) та зворотного демодулювання (Down-conversion) демонструє повний дискретний цикл перетворення між низькочастотними квадратурними компонентами `I/Q` та фізичним смуговим сигналом. Модель описує процеси, що відбуваються всередині сучасних цифрових радіотрансиверів (SDR, Wi-Fi, 5G), де формування базової смуги (Baseband) здійснюється програмно або в ПЛІС, а перенесення у радіочастотну смугу (Passband) відбувається через квадратурні змішувачі.

### 1. Повний цифровий тракт трансивера

У цифровому радіозв'язку обробка сигналів розбита на три рівні:
1. **Digital Baseband (Цифрова базова смуга):** Процесор ЦОС або ПЛІС генерує послідовність комплексних відліків `s_l[n] = I[n] + j Q[n]`. Сюди входять кодування, формування імпульсів фільтрами Найквіста (Raised Cosine), модуляційні сузір'я (QPSK, QAM-64, QAM-256).
2. **Mixed-Signal (Аналогово-цифровий межа):** Цифро-аналогові перетворювачі (ЦАП) перетворюють цифрові масиви `I[n]` та `Q[n]` на аналогові струми `I(t)` та `Q(t)`.
3. **RF Front-End (Радіочастотний тракт):** Квадратурний модулятор виконує Up-conversion перенесення сигналів `I(t)` та `Q(t)` на несучу частоту `f_c`, утворюючи дійсний радіочастотний смуговий сигнал `s(t)`.

Приймач виконує дзеркальні операції у зворотному порядку: радіочастотний смуговий сигнал `s(t)` підсилюється малошумним підсилювачем (LNA), розгалужується і переноситься квадратурними змішувачами у низькочастотну область. Після ФНЧ-фільтрації АЦП оцифровує вибіркові значення `I[n]` та `Q[n]` для подальшої цифрової обробки.

### 2. Дискретна математична модель

Процес квадратурної модуляції та демодуляції у дискретному часі `t = n / f_s` будується на п'яти послідовних етапах:

1. **Генерація низькочастотних сигналів (Baseband):** Формування двох незалежних дійсних сигналів `I[n]` та `Q[n]` із шириною спектра, обмеженою граничною частотою `B < f_c`. У комплексному вигляді це відповідає огинаючій `s_l[n] = I[n] + j · Q[n]`.
2. **Квадратурна модуляція (Up-conversion):** Дискретні низькочастотні сигнали множаться на синфазне `cos(2π f_c n / f_s)` та квадратурне `-sin(2π f_c n / f_s)` коливання опорного гетеродина `f_c`:

```
s[n] = I[n] · cos(2π · f_c · n / f_s) - Q[n] · sin(2π · f_c · n / f_s)
```

   Отриманий сигнал `s[n]` є суто дійсним смуговим сигналом (Passband), спектр якого симетрично розташований навколо `± f_c`.
3. **Моделювання каналу зв'язку:** До смугового сигналу `s[n]` додається адитивний білий гаусів шум (AWGN) із заданою дисперсією `σ²`, фазовий зсув каналу `Δφ` та амплітудне загасання `α`:

```
s_rx[n] = α · s[n] · cos(Δφ) + w[n]
```

4. **Квадратурне детектування (Down-conversion):** Прийнятий смуговий сигнал розгалужується на два паралельних плечі й множиться на гетеродинні коливання приймача:

```
I_raw[n] = 2 · s_rx[n] · cos(2π · f_c · n / f_s)

Q_raw[n] = -2 · s_rx[n] · sin(2π · f_c · n / f_s)
```

   Множник 2 компенсує втрату половини енергії амплітуди під час розщеплення сигналу.
5. **Низькочастотна фільтрація (ФНЧ):** Завдяки тригонометричним тотожностям `2 · cos²(θ) = 1 + cos(2θ)` у сигналах `I_raw[n]` та `Q_raw[n]` виникають високочастотні компоненти на подвоєній несучій частоті `2 f_c`. Низькочастотний КІХ-фільтр (або ковзне середнє) відсікає складники `2 f_c` і виділяє відновлені низькочастотні сигнали `I_rec[n] ≈ I[n]` та `Q_rec[n] ≈ Q[n]`.

### 3. Алгоритмічний розрахунок КІХ-фільтра

Для видалення подвоєної частоти `2 f_c` в умовах дискретної обробки застосовується КІХ-фільтр низьких частот із симетричною імпульсною характеристикою `h[k]`. Вихідні відновлені відліки `I_rec[n]` обчислюються як дискретна згортка:

```
I_rec[n] = ∑_{k=-M}^{+M} I_raw[n - k] · h[k]
```

де `L = 2M + 1` — довжина імпульсної характеристики фільтра. У найпростішому випадку застосовується фільтр ковзного середнього, для якого всі коефіцієнти однакові: `h[k] = 1 / L`.

Для більш якісного пригнічення бокових пелюсток спектра `2 f_c` використовуються КІХ-фільтри на основі sinc-функції з вікном Хеммінга:

```
h_ideal[k] = (2 f_cut / f_s) · sinc( 2 π f_cut k / f_s )

w_hamming[k] = 0.54 + 0.46 · cos( 2 π k / L )

h[k] = h_ideal[k] · w_hamming[k]
```

де `f_cut` — частота зрізу ФНЧ, яку вибирають в інтервалі `B < f_cut < 2f_c - B`.

### 4. Програмна реалізація симулятора

Нижче наведено три варіанти виконання симулятора. Вкладення C демонструє роботу на рівні баферів та статичних масивів, C++ висвітлює об'єктно-орієнтований підхід із контейнерами та комплексною алгеброю, а Python показує векторну обробку сигналів за допомогою бібліотеки NumPy.

:::tabs
```c
/* C implementation: manual memory management, explicit loop processing */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PI 3.14159265358979323846

typedef struct {
    double fs;          /* Частота дискретизації (Гц) */
    double fc;          /* Несуча частота (Гц) */
    size_t num_samples;
    double *i_baseband;
    double *q_baseband;
    double *passband;
    double *i_recovered;
    double *q_recovered;
} IQModem;

IQModem* iq_modem_create(size_t n, double fs, double fc) {
    IQModem *m = (IQModem*)malloc(sizeof(IQModem));
    if (!m) return NULL;
    m->fs = fs;
    m->fc = fc;
    m->num_samples = n;
    m->i_baseband = (double*)calloc(n, sizeof(double));
    m->q_baseband = (double*)calloc(n, sizeof(double));
    m->passband = (double*)calloc(n, sizeof(double));
    m->i_recovered = (double*)calloc(n, sizeof(double));
    m->q_recovered = (double*)calloc(n, sizeof(double));
    return m;
}

void iq_modem_free(IQModem *m) {
    if (!m) return;
    free(m->i_baseband);
    free(m->q_baseband);
    free(m->passband);
    free(m->i_recovered);
    free(m->q_recovered);
    free(m);
}

/* Up-conversion: Baseband (I, Q) -> Passband s(t) */
void iq_modulate(IQModem *m) {
    double dt = 1.0 / m->fs;
    for (size_t n = 0; n < m->num_samples; n++) {
        double t = n * dt;
        double carrier_i = cos(2.0 * PI * m->fc * t);
        double carrier_q = sin(2.0 * PI * m->fc * t);
        m->passband[n] = m->i_baseband[n] * carrier_i - m->q_baseband[n] * carrier_q;
    }
}

/* Down-conversion з ФНЧ ковзним середнім */
void iq_demodulate(IQModem *m, int filter_len) {
    double dt = 1.0 / m->fs;
    double *i_raw = (double*)malloc(m->num_samples * sizeof(double));
    double *q_raw = (double*)malloc(m->num_samples * sizeof(double));

    /* 1. Множення на квадратурні гетеродини */
    for (size_t n = 0; n < m->num_samples; n++) {
        double t = n * dt;
        i_raw[n] =  2.0 * m->passband[n] * cos(2.0 * PI * m->fc * t);
        q_raw[n] = -2.0 * m->passband[n] * sin(2.0 * PI * m->fc * t);
    }

    /* 2. Низькочастотна фільтрація (ФНЧ) */
    for (size_t n = 0; n < m->num_samples; n++) {
        double sum_i = 0.0, sum_q = 0.0;
        int count = 0;
        for (int k = -filter_len / 2; k <= filter_len / 2; k++) {
            int idx = (int)n + k;
            if (idx >= 0 && idx < (int)m->num_samples) {
                sum_i += i_raw[idx];
                sum_q += q_raw[idx];
                count++;
            }
        }
        m->i_recovered[n] = sum_i / count;
        m->q_recovered[n] = sum_q / count;
    }

    free(i_raw);
    free(q_raw);
}

int main(void) {
    size_t N = 1000;
    double fs = 10000.0; /* 10 кГц */
    double fc = 2000.0;  /* 2 кГц несуча */

    IQModem *m = iq_modem_create(N, fs, fc);
    if (!m) return 1;

    /* Створення низькочастотних сигналів (100 Гц та 50 Гц) */
    for (size_t n = 0; n < N; n++) {
        double t = n / fs;
        m->i_baseband[n] = cos(2.0 * PI * 100.0 * t);
        m->q_baseband[n] = sin(2.0 * PI * 50.0 * t);
    }

    iq_modulate(m);
    iq_demodulate(m, 41);

    printf("Зразок [500]: I_orig=%.4f -> I_rec=%.4f | Q_orig=%.4f -> Q_rec=%.4f\n",
           m->i_baseband[500], m->i_recovered[500],
           m->q_baseband[500], m->q_recovered[500]);

    iq_modem_free(m);
    return 0;
}
```
```cpp
// C++ implementation: RAII, std::vector, std::complex, modern idioms
#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <numeric>

class IQModem {
public:
    IQModem(std::size_t samples, double fs, double fc)
        : fs_(fs), fc_(fc),
          baseband_(samples), passband_(samples), recovered_(samples) {}

    void set_baseband(const std::vector<std::complex<double>>& input) {
        baseband_ = input;
    }

    void modulate() {
        const double dt = 1.0 / fs_;
        for (std::size_t n = 0; n < baseband_.size(); ++n) {
            const double t = n * dt;
            const double phase = 2.0 * std::numbers::pi * fc_ * t;
            // s(t) = Re{ s_l(t) * e^(j w_c t) } = I(t)*cos(w_c t) - Q(t)*sin(w_c t)
            const std::complex<double> carrier{std::cos(phase), std::sin(phase)};
            passband_[n] = (baseband_[n] * carrier).real();
        }
    }

    void demodulate(std::size_t filter_len) {
        const std::size_t N = passband_.size();
        const double dt = 1.0 / fs_;
        std::vector<std::complex<double>> raw(N);

        for (std::size_t n = 0; n < N; ++n) {
            const double t = n * dt;
            const double phase = 2.0 * std::numbers::pi * fc_ * t;
            const std::complex<double> lo{2.0 * std::cos(phase), -2.0 * std::sin(phase)};
            raw[n] = passband_[n] * lo;
        }

        // Застосування ФНЧ (КІХ-фільтр ковзного середнього)
        const int half_w = static_cast<int>(filter_len / 2);
        for (std::size_t n = 0; n < N; ++n) {
            std::complex<double> sum{0.0, 0.0};
            int count = 0;
            for (int k = -half_w; k <= half_w; ++k) {
                const int idx = static_cast<int>(n) + k;
                if (idx >= 0 && idx < static_cast<int>(N)) {
                    sum += raw[idx];
                    ++count;
                }
            }
            recovered_[n] = sum / static_cast<double>(count);
        }
    }

    const std::vector<double>& get_passband() const { return passband_; }
    const std::vector<std::complex<double>>& get_recovered() const { return recovered_; }

private:
    double fs_;
    double fc_;
    std::vector<std::complex<double>> baseband_;
    std::vector<double> passband_;
    std::vector<std::complex<double>> recovered_;
};

int main() {
    constexpr std::size_t N = 1000;
    constexpr double fs = 10000.0;
    constexpr double fc = 2000.0;

    IQModem modem(N, fs, fc);
    std::vector<std::complex<double>> input_signal(N);

    for (std::size_t n = 0; n < N; ++n) {
        const double t = n / fs;
        const double i_val = std::cos(2.0 * std::numbers::pi * 100.0 * t);
        const double q_val = std::sin(2.0 * std::numbers::pi * 50.0 * t);
        input_signal[n] = {i_val, q_val};
    }

    modem.set_baseband(input_signal);
    modem.modulate();
    modem.demodulate(41);

    const auto& rec = modem.get_recovered();
    std::cout << "Зразок [500]: Orig=" << input_signal[500] 
              << " -> Rec=" << rec[500] << '\n';

    return 0;
}
```
```py
# Python implementation using NumPy for vectorized DSP
import numpy as np

def iq_modulate(i_bb, q_bb, fs, fc):
    """Up-conversion: низькочастотні I/Q -> смуговий RF сигнал s(t)"""
    t = np.arange(len(i_bb)) / fs
    carrier_i = np.cos(2 * np.pi * fc * t)
    carrier_q = np.sin(2 * np.pi * fc * t)
    s_passband = i_bb * carrier_i - q_bb * carrier_q
    return s_passband

def iq_demodulate(s_passband, fs, fc, filter_len=41):
    """Down-conversion: смуговий RF -> низькочастотні I/Q через ФНЧ"""
    t = np.arange(len(s_passband)) / fs
    # Множення на квадратурний гетеродин
    i_raw =  2.0 * s_passband * np.cos(2 * np.pi * fc * t)
    q_raw = -2.0 * s_passband * np.sin(2 * np.pi * fc * t)
    
    # ФНЧ (КІХ-фільтр ковзного середнього)
    kernel = np.ones(filter_len) / filter_len
    i_rec = np.convolve(i_raw, kernel, mode='same')
    q_rec = np.convolve(q_raw, kernel, mode='same')
    return i_rec, q_rec

# Перевірка симуляції
if __name__ == "__main__":
    fs, fc, N = 10000.0, 2000.0, 1000
    t = np.arange(N) / fs
    i_orig = np.cos(2 * np.pi * 100 * t)
    q_orig = np.sin(2 * np.pi * 50 * t)

    s_rf = iq_modulate(i_orig, q_orig, fs, fc)
    i_rec, q_rec = iq_demodulate(s_rf, fs, fc)

    print(f"Зразок [500]: I_orig={i_orig[500]:.4f} -> I_rec={i_rec[500]:.4f}")
    print(f"Зразок [500]: Q_orig={q_orig[500]:.4f} -> Q_rec={q_rec[500]:.4f}")
```
:::

### 5. Практичний аналіз та інженерні пастки

У реальних радіочастотних трансиверах аналогова частина завжди володіє неідеальностями. Симуляційна модель дозволяє дослідити три ключові апаратні дефекти:

#### А. Фазовий зсув приймального гетеродина (`Δφ`)
Якщо опорний гетеродин приймача має фазову помилку `Δφ` відносно гетеродина передавача, то відновлені компоненти `I_rec` та `Q_rec` зазнають взаємного проникнення каналів (повороту вектора на квадратурній площині):

```
I_rec[n] = I[n] · cos(Δφ) + Q[n] · sin(Δφ)

Q_rec[n] = -I[n] · sin(Δφ) + Q[n] · cos(Δφ)
```

При фазовій помилці `Δφ = 90°` синфазний сигнал `I[n]` повністю переходить у квадратурне плече `Q[n]`, а `Q[n]` — в `I[n]`. Для компенсації цього ефекту цифровий приймач містить систему синхронізації фази (Costas Loop або цифровий rotator).

#### Б. Дисбаланс амплітуд та квадратури (IQ Imbalance)
У фізичних аналогових мікросхемах підсилювачі плечей `I` та `Q` можуть мати відмінні коефіцієнти підсилення `g_I ≠ g_Q`, а фазообертач гетеродина може давати кут `90° + ψ` замість точних `90°`. Це спричиняє появу **дзеркальної завади** (*image interference*) у спектрі відновленої базової смуги. Величина пригнічення дзеркального каналу обчислюється як:

```
IRR = 10 · log10( (1 + 2g cos(ψ) + g²) / (1 - 2g cos(ψ) + g²) )
```

де `g = g_Q / g_I`.

#### В. Постійне зміщення ЦАП/АЦП (DC Offset / LO Leakage)
Наявність постійної напруги зміщення (DC offset) на входах аналогових змішувачів призводить до того, що несуча частота гетеродина `f_c` просочується прямо в вихідний ефірний сигнал. На спектрі це виглядає як вузький гострий пік по центру смугового сигналу. При детектуванні Zero-IF цей пік перетворюється на постійний струм на частоті 0 Гц, який перекриває корисні низькочастотні дані.

#### Г. Оцінка амплітуди помилки вектора (EVM)
Для комплексної оцінки якості роботи модулятора та демодулятора обчислюють параметр **EVM** (*Error Vector Magnitude*):

```
EVM = √[ (1 / N) · ∑_{n=1}^{N} | s_l,rec[n] - s_l,orig[n] |² ] / |s_max|
```

У якісних радіосистемах Wi-Fi 6 та 5G значення EVM повинно бути нижчим за `-30 dB` (менше 3% відхилення), що вимагає високої точності фільтрації та відсутності просочування гетеродина.

### 6. Взаємодія з SDR-апаратурою (UHD / GNU Radio)

У реальних інженерних проєктах на базі SDR (Software Defined Radio) поданий вище алгоритм реалізується у системних бібліотеках:

1. **Формат передачі даних:** Комплексний Baseband потік передається з хост-комп'ютера на плату SDR у вигляді масивів interleaved значень `int16_t` чи `float32_t`: `[I0, Q0, I1, Q1, I2, Q2, ...]`.
2. **Драйвер UHD (USRP Hardware Driver):** При зверненні до пристрою через API:
```cpp
usrp->set_tx_freq(2.45e9); // Налаштування несучої fc
usrp->set_tx_rate(10e6);   // Налаштування частоти дискретизації Baseband fs
```
драйвер записує коефіцієнти в регістри синтезатора частот (PLL) для Up-conversion, а цифровий КІХ-фільтр усередині ПЛІС радіокарти інтерполює низькочастотний масив `I/Q` до внутрішньої частоти ЦАП.
3. **Обробка в GNU Radio:** Блок `QT GUI Frequency Sink` або `Complex to Mag/Phase` приймає потік типів `gr_complex` (що є аналогом `std::complex<float>`), розкладаючи його на амплітуду `A[n]` та фазу `φ[n]` за тим самим математичним принципом, що продемонстровано у нашому симуляторі.
