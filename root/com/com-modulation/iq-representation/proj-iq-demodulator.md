# ⚙️ Алгоритм та програма квадратурної модуляції і демодуляції

Ця вставка містить практичну реалізацію цифрового квадратурного модулятора, демодулятора з фільтрацією низьких частот (ФНЧ) та алгоритму компенсації апаратурного I/Q-дисбалансу мовами C та C++.

### 1. Архітектурний опис цифрового конвеєра обробки

Обробка квадратурного сигналу у сучасних програмно-визначених радіосистемах (SDR) та програмно-апаратних трансіверах цифрового зв'язку складається з чотирьох послідовних алгоритмічних етапів:

1. **Генерація базових компонент (Baseband Processing):** формування послідовності комплексних відліків `z[n] = I[n] + j Q[n]` із вхідного потоку даних. На цьому етапі біти інформації відображаються у точки сузір'я (наприклад, QPSK, 16-QAM чи 256-QAM) або формують комплексну суму піднесучих частот у модуляції OFDM. У цифровому процесорі ці відліки зберігаються у вигляді масиву пар чисел або одиничного масиву комплексних чисел з плаваючою крапкою.
2. **Цифровий підйом на несучу частоту (Digital Upconversion):** розрахунок відліків радіочастотного або проміжного сигналу за дискретною тригонометричною формулою:
```
s[n] = I[n] · cos(2π f_c n / F_s) - Q[n] · sin(2π f_c n / F_s)
```
де `f_c` — цифрова несуча частота, а `F_s` — частота дискретизації АЦП/ЦАП. У реальних FPGA або DSP замість обчислення математичних функцій `cos` та `sin` використовують цифровий генератор із керованою частотою (NCO — Numerically Controlled Oscillator) на основі алгоритму CORDIC або табличного вибірки таблиць синуса (LUT — Look-Up Table).
3. **Цифрова демодуляція та ФНЧ (Digital Downconversion & Low-Pass Filtering):** перемноження відліків прийнятого сигналу `s[n]` на ортогональні цифрові носії `cos(2π f_c n / F_s)` та `-sin(2π f_c n / F_s)` з подальшою фільтрацією низьких частот (ФНЧ) для пригнічення сумарних гармонік `2f_c` та виділення огинаючого `I'[n]` і `Q'[n]`.
4. **Цифрова компенсація спотворень (IQ Imbalance & DC Offset Correction):** алгоритмічне видалення постійного зсуву нульового рівня (DC offset) та ортогоналізація компонент за допомогою розкладання Грама-Шмідта для відновлення симетрії сузір'я та пригнічення дзеркального каналу в ефірі.

### 2. Математика дискретної фільтрації та корекції

Для низькочастотної фільтрації у цифрових демодуляторах використовують КІХ-фільтри (FIR — Finite Impulse Response) або спрощені рекурсивні ІІХ-фільтри першого порядку (EMA — Exponential Moving Average). Різницеве рівняння однополюсного ІІХ-фільтра має вигляд:

```
y[n] = y[n-1] + α · (x[n] - y[n-1])
```

Коефіцієнт згладжування `α` розраховується через бажану частоту зрізу `f_cutoff` та частоту дискретизації `F_s`:

```
α = 2π · f_cutoff / (2π · f_cutoff + F_s)
```

Для корекції фазового та амплітудного дисбалансу використовується матричне перетворення Грама-Шмідта. Якщо аналогова схема додає фазову помилку `Δφ` та має співвідношення коефіцієнтів підсилення `g = g_Q / g_I`, то виправлені відліки обчислюються за формулами:

```
I_corr[n] = I_raw[n]
Q_corr[n] = (Q_raw[n] - I_raw[n] · tg(Δφ)) / (cos(Δφ) · g)
```

Ці операції легко паралеляться на векторних SIMD-інструкціях процесорів (AVX2/NEON) або виконуються у конвеєрі FPGA. Крім того, після проходження цифрового ФНЧ потік відліків часто зменшують за частотою дискретизації (процес децимації), щоб передавати у подальші блоки обробки лише мінімально необхідну кількість комплексних відліків на один символ сузір'я.

### 3. Програмна реалізація мовами C та C++

Нижче наведено повну та самодостатню реалізацію обробки IQ-сигналу мовами C та C++. 

Приклад мовою C++ є строго ідіоматичним: він спирається на тип `std::complex<float>`, обгортки для безпечного доступу до послідовної пам'яті `std::span`, семантику керування ресурсами RAII, математичні константи з `<numbers>` та алгоритми розрахунку зі стандартної бібліотеки `<numeric>`. На відміну від прямого перекладу з C, код C++ усуває ручне керування пам'яттю `malloc/free`, гарантує відсутність витоків ресурсів і показує сучасний стиль написання DSP-алгоритмів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Структура для збереження квадратурного відліку в декартових координатах
typedef struct {
    float i;
    float q;
} iq_sample_t;

// Перетворення полярних координат (амплітуда A, фаза phi) у прямокутні (I, Q)
static inline iq_sample_t polar_to_iq(float amp, float phase_rad) {
    iq_sample_t s;
    s.i = amp * cosf(phase_rad);
    s.q = amp * sinf(phase_rad);
    return s;
}

// Перетворення прямокутних компонент (I, Q) у полярні координати (амплітуда A, фаза phi)
static inline void iq_to_polar(iq_sample_t s, float *amp, float *phase_rad) {
    *amp = sqrtf(s.i * s.i + s.q * s.q);
    *phase_rad = atan2f(s.q, s.i);
}

// Рекурсивний ФНЧ першого порядку (Exponential Moving Average Filter)
typedef struct {
    float alpha;
    float state;
} lpf_1pole_t;

static inline float lpf_process(lpf_1pole_t *f, float in) {
    f->state += f->alpha * (in - f->state);
    return f->state;
}

// Функція корекції постійної складової (DC offset removal)
void correct_dc_offset(iq_sample_t *samples, size_t count) {
    if (!samples || count == 0) return;

    float sum_i = 0.0f;
    float sum_q = 0.0f;

    for (size_t n = 0; n < count; ++n) {
        sum_i += samples[n].i;
        sum_q += samples[n].q;
    }

    float mean_i = sum_i / (float)count;
    float mean_q = sum_q / (float)count;

    for (size_t n = 0; n < count; ++n) {
        samples[n].i -= mean_i;
        samples[n].q -= mean_q;
    }
}

// Повний конвеєр модуляції, цифрового переносу та демодуляції
void run_iq_pipeline(size_t num_samples, float sample_rate, float carrier_freq) {
    iq_sample_t *tx_iq = (iq_sample_t *)malloc(num_samples * sizeof(iq_sample_t));
    float *rf_signal = (float *)malloc(num_samples * sizeof(float));
    iq_sample_t *rx_iq = (iq_sample_t *)malloc(num_samples * sizeof(iq_sample_t));

    if (!tx_iq || !rf_signal || !rx_iq) {
        free(tx_iq); free(rf_signal); free(rx_iq);
        return;
    }

    // 1. Генерація базового IQ-сигналу (вектор, що обертається з частотою 1 кГц)
    float mod_freq = 1000.0f;
    for (size_t n = 0; n < num_samples; ++n) {
        float t = (float)n / sample_rate;
        float phase = 2.0f * (float)M_PI * mod_freq * t;
        tx_iq[n] = polar_to_iq(1.0f, phase);
    }

    // 2. Цифровий квадратурний модулятор (Upconversion)
    for (size_t n = 0; n < num_samples; ++n) {
        float t = (float)n / sample_rate;
        float wc = 2.0f * (float)M_PI * carrier_freq * t;
        rf_signal[n] = tx_iq[n].i * cosf(wc) - tx_iq[n].q * sinf(wc);
    }

    // 3. Цифровий квадратурний демодулятор (Downconversion + ФНЧ)
    lpf_1pole_t lpf_i = { .alpha = 0.05f, .state = 0.0f };
    lpf_1pole_t lpf_q = { .alpha = 0.05f, .state = 0.0f };

    for (size_t n = 0; n < num_samples; ++n) {
        float t = (float)n / sample_rate;
        float wc = 2.0f * (float)M_PI * carrier_freq * t;

        // Перемноження на ортогональні несучі
        float raw_i = rf_signal[n] * cosf(wc);
        float raw_q = rf_signal[n] * (-sinf(wc));

        // Фільтрація з відновленням амплітудного масштабу (множник 2.0)
        rx_iq[n].i = 2.0f * lpf_process(&lpf_i, raw_i);
        rx_iq[n].q = 2.0f * lpf_process(&lpf_q, raw_q);
    }

    // Корекція можливого постійного зсуву
    correct_dc_offset(rx_iq, num_samples);

    printf("Контрольний відлік [100]: TX (I=%.3f, Q=%.3f) -> RX (I=%.3f, Q=%.3f)\n",
           tx_iq[100].i, tx_iq[100].q, rx_iq[100].i, rx_iq[100].q);

    free(tx_iq);
    free(rf_signal);
    free(rx_iq);
}
```
```cpp
#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <numeric>
#include <span>

// Комплексний відлік базової смуги
using IQSample = std::complex<float>;

// Клас цифрового ФНЧ з автозбереженням стану (RAII)
class LowPassFilter {
public:
    explicit LowPassFilter(float alpha) noexcept : alpha_(alpha), state_(0.0f) {}

    [[nodiscard]] float process(float input) noexcept {
        state_ += alpha_ * (input - state_);
        return state_;
    }

    void reset() noexcept { state_ = 0.0f; }

private:
    float alpha_;
    float state_;
};

// Усунення DC offset за допомогою std::span та алгоритмів STL
void correct_dc_offset(std::span<IQSample> samples) noexcept {
    if (samples.empty()) return;

    IQSample sum = std::accumulate(samples.begin(), samples.end(), IQSample{0.0f, 0.0f});
    IQSample mean = sum / static_cast<float>(samples.size());

    for (auto& sample : samples) {
        sample -= mean;
    }
}

// Алгоритм цифрової ортогоналізації Грама-Шмідта для компенсації IQ-дисбалансу
void correct_iq_imbalance(std::span<IQSample> samples, float phase_error_rad, float gain_ratio) noexcept {
    float tan_ph = std::tan(phase_error_rad);
    float sec_ph = 1.0f / std::cos(phase_error_rad);

    for (auto& s : samples) {
        float i_corr = s.real();
        float q_corr = (s.imag() - i_corr * tan_ph) * sec_ph * gain_ratio;
        s = IQSample{i_corr, q_corr};
    }
}

// Ідіоматичний C++ конвеєр обробки IQ-сигналу
void run_iq_pipeline_cpp(size_t num_samples, float sample_rate, float carrier_freq) {
    std::vector<IQSample> tx_iq(num_samples);
    std::vector<float> rf_signal(num_samples);
    std::vector<IQSample> rx_iq(num_samples);

    constexpr float mod_freq = 1000.0f; // 1 кГц

    // 1. Генерація комплексного огинаючого z(t) = e^(j w_m t)
    for (size_t n = 0; n < num_samples; ++n) {
        float t = static_cast<float>(n) / sample_rate;
        float phase = 2.0f * std::numbers::pi_v<float> * mod_freq * t;
        tx_iq[n] = std::polar(1.0f, phase);
    }

    // 2. Цифрова квадратурна модуляція (Upconversion): Re{ z(t) * e^(j w_c t) }
    for (size_t n = 0; n < num_samples; ++n) {
        float t = static_cast<float>(n) / sample_rate;
        float wc = 2.0f * std::numbers::pi_v<float> * carrier_freq * t;
        rf_signal[n] = tx_iq[n].real() * std::cos(wc) - tx_iq[n].imag() * std::sin(wc);
    }

    // 3. Цифрова квадратурна демодуляція
    LowPassFilter lpf_i(0.05f);
    LowPassFilter lpf_q(0.05f);

    for (size_t n = 0; n < num_samples; ++n) {
        float t = static_cast<float>(n) / sample_rate;
        float wc = 2.0f * std::numbers::pi_v<float> * carrier_freq * t;

        float raw_i = rf_signal[n] * std::cos(wc);
        float raw_q = rf_signal[n] * (-std::sin(wc));

        rx_iq[n] = IQSample{
            2.0f * lpf_i.process(raw_i),
            2.0f * lpf_q.process(raw_q)
        };
    }

    // 4. Корекція постійного зсуву та дисбалансу
    correct_dc_offset(rx_iq);
    correct_iq_imbalance(rx_iq, 0.01f, 1.02f); // Компенсація фазової помилки 0.01 рад та несиметрії 2%

    std::cout << "Контрольний відлік C++ [100]: TX " << tx_iq[100] << " -> RX " << rx_iq[100] << '\n';
}
```
:::

### 4. Детальний аналіз алгоритмічних кроків та нюанси обробки

1. **Математика цифрового модулятора:** у коді вираз `rf_signal[n] = tx_iq[n].real() * std::cos(wc) - tx_iq[n].imag() * std::sin(wc)` виконує точний цифровий підйом комплексного сигналу базової смуги на цифровий носій. Використання знака «мінус» перед уявним доданком є важливим стандартом: воно забезпечує правильне узгодження від'ємних частот базової смуги з нижньою бічною смугою радіоефіру.
2. **Фільтрація низьких частот (ФНЧ):** у програмі реалізовано рекурсивний фільтр першого порядку `state += alpha * (input - state)`. Коефіцієнт `alpha = 0.05` розрахований так, щоб частота зрізу була значно меншою за несучу частоту `carrier_freq`, але більшою за максимальну частоту модулювального сигналу. Це забезпечує повне пригнічення високочастотних сумарних гармонік `2f_c` та чисте виділення вихідних компонент `I(t)` та `Q(t)`.
3. **Множник 2.0 при демодуляції:** під час перемноження вхідного сигналу на гармонічні несучі амплітуда вихідних компонент зменшується вдвічі (оскільки `cos²(x) = 1/2 + 1/2 cos(2x)`). Тому у демодуляторі додається відновлювальний множник `2.0f`, який повертає точну початкову амплітуду сигналу.
4. **Матрична корекція дисбалансу:** функція `correct_iq_imbalance` реалізує матричну компенсацію Грама-Шмідта. Вона усуває перехресне зчеплення між каналами `I` та `Q`, яке виникає у реальному аналоговому залізі при відхиленні фазового кута між гетеродинами від `90°` та амплітудній несиметрії підсилювачів.
5. **Оптимізація пам'яті та обчислень:** у високонавантажених SDR-системах векторні операції над відліками `IQSample` виконуються за допомогою SIMD-інструкцій (наприклад, `vdivps`, `vmulps` у х86 або NEON у ARM). Використання вирівняних у пам'яті масивів `std::vector<std::complex<float>>` дозволяє процесору завантажувати по чотири або вісім комплексних відліків за один такт.
