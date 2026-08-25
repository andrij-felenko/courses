# ⚙️ Програмна реалізація DSB-SC та петлі Костаса в SDR

Програмна реалізація двосмугової модуляції з пригніченою несучою (DSB-SC) та її когерентного демодулятора за допомогою петлі Костаса є базовим блоком у системах програмно-визначального радіо (англ. *Software-Defined Radio*, SDR). Модулятор перемножує дискретний цифровий сигнал повідомлення `m[n]` на відсплановані відліки цифрового синтезатора прямого синтезу (NCO). Демодулятор розділяє вхідний потік на квадратурні вітки `I` та `Q`, фільтрує їх рекурсивними ФНЧ та використовує добуток `I · Q` як сигнал помилки для підстроювання частоти й фази NCO.

### 1. Архитектура цифрового модулятора DSB-SC

Цифровий модулятор приймає потік відліків мовного чи даних сигналу `m[n]`, дискретизований із частотою `f_s`. Числовий генератор (NCO) на кожному кроці дискретизації обчислює за поточною фазою `ϕ[n]` значення косинуса. Після множення `s[n] = m[n] · cos(ϕ[n])` фаза розширюється на крок `Δϕ = 2π · f_c / f_s`. При перевищенні `2π` фазовий акумулятор виконує скидання (обгортання) фази.

Для запобігання втрати точності з плаваючою крапкою після мільйонів ітерацій обгортання фази `ϕ` виконується через `fmod(phase, 2π)` або викликом вирівнювання у діапазоні `[0, 2π)`. У реальних високопродуктивних DSP-ядрах фазовий акумулятор реалізується на 32-розрядних цілих числах без знака (`uint32_t`), де переповнення регістра природно реалізує точну арифметику за модулем `2³²`.

### 2. Математика дискретних фільтрів та петлі Костаса

Цифровий демодулятор (петля Костаса) працює як зворотний тракт. Прийнятий цифровий сигнал `s[n]` множиться на косинусну та синусну опорні хвилі NCO. Низькочастотна фільтрація каналів I та Q здійснюється дискретним однополюсним ІІР-фільтром першого порядку (англ. *Single-Pole IIR Filter*):

```
y[n] = y[n−1] + α · (x[n] − y[n−1])
```

де коефіцієнт згладжування `α = dt / (RC + dt)` розраховується через частоту зрізу ФНЧ `f_cut`. Добуток відфільтрованих відліків `e[n] = I[n] · Q[n]` створює миттєвий сигнал помилки фази. Цей сигнал подається на пропорційно-інтегральний регулятор (PI-фільтр), який формує підстроювальне значення частоти для NCO.

Дискретні коефіцієнти PI-фільтра `K_p` та `K_i` пов'язані з нормованою шумовою смугою петлі `θ_n = ω_n / f_s` та коефіцієнтом демпфування `ζ = 0.707` за допомогою наближення білінійного Z-перетворення:

```
denom = 1 + 2·ζ·θ_n + θ_n²
K_p = (4·ζ·θ_n) / denom
K_i = (4·θ_n²) / denom
```

### 3. Алгоритмічний покроковий розбір обробки відліків

Процес обробки кожного нового цифрового відліку вхідного сигналу складається з 6 послідовних кроків:

1. **Генерування опорних відліків NCO:** Синтезатор обчислює квадратурні відліки `nco_i = cos(phase)` та `nco_q = -sin(phase)`.
2. **Квадратурне змішування:** Вхідний відлік `s[n]` перемножується на опорні коливання. Множник `2.0` компенсує втрату амплітуди наполовину при тригонометричному розкладанні добутку косинусів.
3. **Рекурсивна фільтрація ФНЧ:** Сигнали проходять крізь дискретні однополюсні ІІР-фільтри каналів I та Q. Стан фільтрів зберігається у змінних `lpf_i` та `lpf_q`.
4. **Обчислення фазового дискримінатора:** Формується сигнал помилки фази `error = lpf_i * lpf_q`. Завдяки квадрату повідомлення сигнал помилки не реагує на фазові інверсії інформаційного сигналу.
5. **Пропорційно-інтегральна корекція (PI):** Накопичується стан інтегратора `integrator += K_i * error`. Сума `control = K_p * error + integrator` визначає миттєве коригування частоти.
6. **Оновлення фазового акумулятора NCO:** Поточна фаза розширюється на суму номінальної частоти та корекції: `phase += freq + control`. Фаза нормалізується у діапазоні `[0, 2π)`.

Нижче наведено робочі алгоритми цифрової обробки сигналів для модуляції та детектування DSB-SC двома мовами — C та C++.

:::tabs
```c
/* dsb_costas.h / dsb_costas.c - C implementation of DSB-SC Modulator & Costas Loop */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double phase;
    double phase_increment; // 2 * PI * f_c / f_s
} dsb_modulator_t;

typedef struct {
    double phase;
    double freq;            // Поточна частота NCO (рад/відлік)
    double alpha;           // Коефіцієнт ФНЧ для I/Q (0..1)
    double kp;              // Пропорційний коефіцієнт петлі
    double ki;              // Інтегральний коефіцієнт петлі
    double lpf_i;           // Стан ФНЧ вітки I
    double lpf_q;           // Стан ФНЧ вітки Q
    double integrator;      // Стан інтегратора петльового фільтра
} costas_loop_t;

void dsb_modulator_init(dsb_modulator_t *mod, double f_carrier, double sample_rate) {
    mod->phase = 0.0;
    mod->phase_increment = 2.0 * M_PI * f_carrier / sample_rate;
}

double dsb_modulate_sample(dsb_modulator_t *mod, double m_sample) {
    double carrier = cos(mod->phase);
    mod->phase += mod->phase_increment;
    if (mod->phase >= 2.0 * M_PI) {
        mod->phase -= 2.0 * M_PI;
    }
    return m_sample * carrier;
}

void costas_loop_init(costas_loop_t *loop, double f_carrier, double sample_rate, 
                      double lpf_cutoff, double damping, double loop_bw) {
    loop->phase = 0.0;
    loop->freq = 2.0 * M_PI * f_carrier / sample_rate;
    
    // Коефіцієнт однополюсного ФНЧ: alpha = dt / (RC + dt)
    double dt = 1.0 / sample_rate;
    double rc = 1.0 / (2.0 * M_PI * lpf_cutoff);
    loop->alpha = dt / (rc + dt);
    
    // Розрахунок коефіцієнтів PI петльового фільтра
    double denom = 1.0 + 2.0 * damping * loop_bw + loop_bw * loop_bw;
    loop->kp = (4.0 * damping * loop_bw) / denom;
    loop->ki = (4.0 * loop_bw * loop_bw) / denom;
    
    loop->lpf_i = 0.0;
    loop->lpf_q = 0.0;
    loop->integrator = 0.0;
}

double costas_demodulate_sample(costas_loop_t *loop, double input_sample) {
    // 1. Генерування квадратурних опорних сигналів NCO
    double nco_i = cos(loop->phase);
    double nco_q = -sin(loop->phase);
    
    // 2. Змішування (перемноження)
    double raw_i = input_sample * nco_i * 2.0;
    double raw_q = input_sample * nco_q * 2.0;
    
    // 3. Низькочастотна фільтрація (ФНЧ I та Q)
    loop->lpf_i += loop->alpha * (raw_i - loop->lpf_i);
    loop->lpf_q += loop->alpha * (raw_q - loop->lpf_q);
    
    // 4. Детектор фазової помилки: e = I * Q
    double error = loop->lpf_i * loop->lpf_q;
    
    // 5. Петльовий PI-фільтр
    loop->integrator += loop->ki * error;
    double control = loop->kp * error + loop->integrator;
    
    // 6. Оновлення фази та частоти NCO
    loop->phase += loop->freq + control;
    while (loop->phase >= 2.0 * M_PI) loop->phase -= 2.0 * M_PI;
    while (loop->phase < 0.0)         loop->phase += 2.0 * M_PI;
    
    // Відновлений аудіосигнал береться з виходу вітки I
    return loop->lpf_i;
}
```
```cpp
// CostasLoop.hpp - Idiomatic C++20 implementation of Costas Loop SDR Demodulator
#pragma once
#include <vector>
#include <span>
#include <cmath>
#include <numbers>
#include <algorithm>

namespace sdr {

class CostasLoop {
public:
    struct Config {
        double sampleRate{48000.0};
        double carrierFreq{10000.0};
        double lpfCutoff{3000.0};
        double damping{0.707};
        double loopBandwidth{0.05};
    };

    explicit CostasLoop(const Config& cfg)
        : m_phase(0.0)
        , m_nominalFreq(2.0 * std::numbers::pi * cfg.carrierFreq / cfg.sampleRate)
        , m_freqOffset(0.0)
        , m_lpfI(0.0)
        , m_lpfQ(0.0)
        , m_integrator(0.0)
    {
        double dt = 1.0 / cfg.sampleRate;
        double rc = 1.0 / (2.0 * std::numbers::pi * cfg.lpfCutoff);
        m_alpha = dt / (rc + dt);

        double denom = 1.0 + 2.0 * cfg.damping * cfg.loopBandwidth + cfg.loopBandwidth * cfg.loopBandwidth;
        m_kp = (4.0 * cfg.damping * cfg.loopBandwidth) / denom;
        m_ki = (4.0 * cfg.loopBandwidth * cfg.loopBandwidth) / denom;
    }

    [[nodiscard]] double processSample(double inputSample) noexcept {
        const double ncoI = std::cos(m_phase);
        const double ncoQ = -std::sin(m_phase);

        const double rawI = inputSample * ncoI * 2.0;
        const double rawQ = inputSample * ncoQ * 2.0;

        // Ітерація однополюсного IIR ФНЧ
        m_lpfI += m_alpha * (rawI - m_lpfI);
        m_lpfQ += m_alpha * (rawQ - m_lpfQ);

        // Фазовий дискримінатор петлі Костаса
        const double error = m_lpfI * m_lpfQ;

        // Пропорційно-інтегральний фільтр (PI)
        m_integrator += m_ki * error;
        const double control = m_kp * error + m_integrator;

        // Оновлення NCO
        m_phase += (m_nominalFreq + control);
        m_phase = std::fmod(m_phase, 2.0 * std::numbers::pi);
        if (m_phase < 0.0) {
            m_phase += 2.0 * std::numbers::pi;
        }

        return m_lpfI;
    }

    void processBlock(std::span<const float> input, std::span<float> output) noexcept {
        const std::size_t count = std::min(input.size(), output.size());
        for (std::size_t i = 0; i < count; ++i) {
            output[i] = static_cast<float>(processSample(input[i]));
        }
    }

    [[nodiscard]] double currentPhaseError() const noexcept { return m_lpfQ; }
    [[nodiscard]] double estimatedFrequencyOffsetHz(double sampleRate) const noexcept {
        return (m_integrator * sampleRate) / (2.0 * std::numbers::pi);
    }

private:
    double m_phase;
    double m_nominalFreq;
    double m_freqOffset;
    double m_alpha;
    double m_kp;
    double m_ki;
    double m_lpfI;
    double m_lpfQ;
    double m_integrator;
};

} // namespace sdr
```
:::

### 4. Особливості реалізації C++ та обробки буферів

Реалізація мовою C++20 використовує сучасні ідіоми збірки безпечного коду без сирих вказівників:
* **Клас `sdr::CostasLoop`:** інкапсулює повністю весь стан демодулятора (стан NCO, стан ФНЧ каналів I та Q, стан інтегратора петлі).
* **Семантика RAII:** об'єкт ініціалізується структурами конфігурації `Config` у конструкторі, що гарантує відсутність неузгоджених станів чи неініціалізованих змінних.
* **Передача масивів через `std::span`:** метод `processBlock()` приймає зрізи пам'яті `std::span<const float>` без виділення динамічної пам'яті у купі (heap allocation) на кожному кадрі аудіо/RF. Це уможливлює роботу в режимі жорсткого реального часу без паузи на збирання сміття чи перевиділення векторів.

### 5. Налаштування параметрів, AGC та оптимізація обчислень

Практична реалізація вимагає уваги до балансу коефіцієнтів петлі `K_p` та `K_i`. Занадто широка смуга петлі `loopBandwidth` призводить до фазового тремтіння (джитера) під впливом шуму ефіру, а занадто вузька смуга спричиняє тривале захоплення фази або зрив синхронізму при доплерівському зсуві частоти.

У реальних SDR-трактах перед петлею Костаса обов'язково встановлюють блок автоматичного регулювання підсилення (AGC). Оскільки вихід фазового детектора `e = I · Q` пропорційний квадрату амплітуди вхідного сигналу `A_c² · m²(t)`, коливання рівня вхідного RF-сигналу без AGC змінюють ефективне підсилення петлі `K_d`, що руйнує розрахований коефіцієнт демпфування `ζ` і може перевести петлю у стан автоколивальної нестабільності.

Для оптимізації обчислювальної швидкодії в обробці реального часу замість прямих викликів `cos()` та `sin()` застосовують табличний синтез NCO (Look-Up Table, LUT) з лінійною інтерполяцією або алгоритм CORDIC, що дозволяє обробляти потік відліків із частотою дискретизації у сотні мегагерц на центральних процесорах без використання графічних підсилювачів. Векторизація SIMD (ARM NEON або x86 AVX2) дозволяє паралельно підраховувати відліки каналів I та Q для блоків із тисяч зразків.
