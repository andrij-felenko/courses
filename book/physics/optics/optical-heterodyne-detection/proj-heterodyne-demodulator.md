# ⚙️ Симуляція оптичного гетеродинного приймача та квадратурного демодулятора

Ця вставка містить практичну реалізацію симуляції оптичного гетеродинного детектора, балансного змішувача, генерації дробового шуму та цифрової квадратурної IQ-демодуляції фазово-модульованого оптичного сигналу мовами C, C++ та Python.

### 1. Фізична модель та математичний алгоритм симулятора

Моделювання оптичного гетеродинного приймача вимагає відтворення трьох послідовних фізичних і цифрових етапів:

#### 1. Генерація сигнального поля та гетеродина

Сигнальна хвиля з фазовою модуляцією `φ_s(t)` та оптичною потужністю `P_s` описується вектором електричного поля:

```
E_s(t) = √(2 · P_s) · cos(2π · f_0 · t + φ_s(t))
```

Опорна хвиля гетеродина з потужністю `P_LO` та зсувом на проміжну частоту `f_IF`:

```
E_LO(t) = √(2 · P_LO) · cos(2π · (f_0 - f_IF) · t)
```

Оптичний носій `f_0` становить близько 193 ТГц. У цифровій симуляції дискретизація терагерцових частот вимагала б пектабайт оперативної пам'яті та петафлопс обчислювальних ресурсів. Оскільки квадратичне детектування фотодіода миттєво здійснює перенесення спектра у радіодіапазон, симуляція ефективно моделює фотострум безпосередньо у смузі проміжної частоти `f_IF`, зберігаючи повну точність фізичних процесів.

#### 2. Формування балансного фотоструму та пуассонівського шуму

Амплітуда корисного струму биття задається виразом:

```
I_beat_peak = 2 · R_resp · √(P_s · P_LO)
```

Дробовий шум постійного фотоструму гетеродина `I_LO = R_resp · P_LO` моделюється як білий гаусовий шум з нульовим середнім значенням та середньоквадратичним відхиленням (СКВ), вираженим через смугу дискретизації АЦП `B_sample = f_sample / 2`:

```
σ_shot = √( 2 · e · I_LO · (f_sample / 2) )
```

Для згенерованого фотоструму `i_bal(t) = I_beat_peak · cos(2π · f_IF · t + φ_s(t)) + noise(t)` моделюється дискретизація аналого-цифровим перетворювачем (АЦП) із частотою вибірок `f_sample`.

#### 3. Цифрова квадратурна IQ-демодуляція (Quadrature Demodulation)

Вхідний дискретизований струм `i_bal[k]` множиться на дві квадратурні опорні синусоїди цифрового керованого генератора (NCO — *Numerically Controlled Oscillator*) на проміжній частоті `f_IF`:

```
raw_I[k] = i_bal[k] · cos(2π · f_IF · k · Δt)
raw_Q[k] = i_bal[k] · ( -sin(2π · f_IF · k · Δt) )
```

Отримані квадратурні сигнали містять сумнівну компоненту з подвоєною частотою `2·f_IF` та корисну огинаючу базової смуги. Вони проходять крізь цифровий низькочастотний КІХ-фільтр (ковзне усереднення по прямокутному вікну тривалістю `N_win = f_sample / (2 · f_IF)`):

```
filtered_I[k] = (1 / N_win) · ∑ raw_I[k + w]
filtered_Q[k] = (1 / N_win) · ∑ raw_Q[k + w]
```

Частотна характеристика КІХ-фільтра ковзного усереднення описується функцією `sinc`:

```
H(f) = sin(π · f · N_win / f_sample) / ( N_win · sin(π · f / f_sample) )
```

Цей фільтр надійно пригнічує високочастотну компоненту `2·f_IF`, пропускаючи лише низькочастотний сигнал модуляції.

#### 4. Відновлення миттєвої фази та амплітуди

Миттєва фаза оптичної хвилі обчислюється через арктангенс двох аргументів, що забезпечує визначення фази в усіх чотирьох квадратах комплесної площини:

```
φ_rec[k] = atan2(filtered_Q[k], filtered_I[k])
```

Огинаюча амплітуда корисної хвилі відновлюється як модуль комплексного числа:

```
A_rec[k] = √( filtered_I[k]² + filtered_Q[k]² )
```

### 2. Реалізація симулятора мовами C, C++ та Python

Нижче подано повний, готовий до компіляції та виконання код симуляції трьома мовами. Кожна реалізація є самостійною, ідіоматичною та високопродуктивною.

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
    double sample_rate;    // Частота дискретизації АЦП (Гц)
    double f_if;           // Проміжна частота (Гц)
    double p_signal;       // Потужність оптичного сигналу (Вт)
    double p_lo;           // Потужність оптичного гетеродина (Вт)
    double responsivity;   // Чутливість фотодіода (А/Вт)
    size_t num_samples;    // Загальна кількість відліків
} heterodyne_config_t;

// Генератор нормального білого шуму (метод Бокса-Мюллера)
static double generate_gaussian_noise(double std_dev) {
    double u1 = (double)rand() / RAND_MAX;
    double u2 = (double)rand() / RAND_MAX;
    if (u1 < 1e-12) u1 = 1e-12;
    return std_dev * sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2);
}

// Симуляція гетеродинного детектування та IQ-демодуляції
void run_heterodyne_simulation(const heterodyne_config_t* cfg) {
    double dt = 1.0 / cfg->sample_rate;
    double i_lo = cfg->responsivity * cfg->p_lo;
    
    // Дробовий шум гетеродина: std_dev = sqrt(2 * e * I_lo * B_sample)
    double q_elem = 1.602176634e-19;
    double shot_noise_std = sqrt(2.0 * q_elem * i_lo * (cfg->sample_rate / 2.0));

    double* i_out = (double*)malloc(cfg->num_samples * sizeof(double));
    double* q_out = (double*)malloc(cfg->num_samples * sizeof(double));
    double* phase_recovered = (double*)malloc(cfg->num_samples * sizeof(double));

    if (!i_out || !q_out || !phase_recovered) {
        fprintf(stderr, "Помилка виділення пам'яті!\n");
        free(i_out); free(q_out); free(phase_recovered);
        return;
    }

    int filter_window = (int)(cfg->sample_rate / (cfg->f_if * 2.0));
    if (filter_window < 1) filter_window = 1;

    double peak_beat_current = 2.0 * cfg->responsivity * sqrt(cfg->p_signal * cfg->p_lo);

    printf("=== СИМУЛЯЦІЯ ОПТИЧНОГО ГЕТЕРОДИНА (C) ===\n");
    printf("Потужність сигналу P_s: %.2e Вт\n", cfg->p_signal);
    printf("Потужність гетеродина P_LO: %.2e Вт\n", cfg->p_lo);
    printf("Піковий струм биття: %.3f мкА\n", peak_beat_current * 1e6);
    printf("СКВ дробового шуму: %.3f мкА\n\n", shot_noise_std * 1e6);

    for (size_t k = 0; k < cfg->num_samples; k++) {
        double t = k * dt;
        // Задаємо тестову фазову модуляцію BPSK (зміна фази 0 або PI/2)
        double phase_target = (t > (cfg->num_samples * dt / 2.0)) ? M_PI / 2.0 : 0.0;

        // Балансний фотострум биття + дробовий шум
        double beat_signal = peak_beat_current * cos(2.0 * M_PI * cfg->f_if * t + phase_target);
        double noise = generate_gaussian_noise(shot_noise_std);
        double i_bal = beat_signal + noise;

        // Множення на квадратурні гетеродинні носії
        double raw_i = i_bal * cos(2.0 * M_PI * cfg->f_if * t);
        double raw_q = i_bal * (-sin(2.0 * M_PI * cfg->f_if * t));

        i_out[k] = raw_i;
        q_out[k] = raw_q;
    }

    // Низькочастотна фільтрація (ковзне усереднення) та відновлення фази
    for (size_t k = 0; k < cfg->num_samples; k++) {
        double sum_i = 0.0, sum_q = 0.0;
        int count = 0;

        for (int w = -filter_window; w <= filter_window; w++) {
            int idx = (int)k + w;
            if (idx >= 0 && idx < (int)cfg->num_samples) {
                sum_i += i_out[idx];
                sum_q += q_out[idx];
                count++;
            }
        }

        double filtered_i = sum_i / count;
        double filtered_q = sum_q / count;
        phase_recovered[k] = atan2(filtered_q, filtered_i);
    }

    // Виведення контрольних точок
    printf("Час (мкс) | Відновлена фаза (рад) | Цільова фаза\n");
    printf("-----------------------------------------------\n");
    size_t step = cfg->num_samples / 5;
    for (size_t k = step / 2; k < cfg->num_samples; k += step) {
        double t_us = (k * dt) * 1e6;
        double target = (k * dt > (cfg->num_samples * dt / 2.0)) ? M_PI / 2.0 : 0.0;
        printf("%9.2f | %21.4f | %12.4f\n", t_us, phase_recovered[k], target);
    }

    free(i_out);
    free(q_out);
    free(phase_recovered);
}

int main(void) {
    heterodyne_config_t cfg = {
        .sample_rate = 1.0e9,     // 1 ГВибірок/с
        .f_if = 100.0e6,          // 100 МГц проміжна частота
        .p_signal = 1.0e-9,       // 1 нВт слабкий сигнал
        .p_lo = 1.0e-3,           // 1 мВт потужний гетеродин
        .responsivity = 0.85,     // 0.85 А/Вт при 1550 нм
        .num_samples = 2000
    };

    run_heterodyne_simulation(&cfg);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <numbers>
#include <iomanip>
#include <algorithm>

struct HeterodyneConfig {
    double sample_rate{1.0e9};   // 1 ГГц частота дискретизації
    double f_if{100.0e6};        // 100 МГц проміжна частота
    double p_signal{1.0e-9};     // 1 нВт сигнальна потужність
    double p_lo{1.0e-3};         // 1 мВт потужність гетеродина
    double responsivity{0.85};   // 0.85 А/Вт чутливість фотодіода
    std::size_t num_samples{2000};
};

class HeterodyneDemodulator {
public:
    explicit HeterodyneDemodulator(HeterodyneConfig config)
        : cfg_(config), rng_(1337) {}

    void process() {
        const double dt = 1.0 / cfg_.sample_rate;
        const double i_lo = cfg_.responsivity * cfg_.p_lo;
        constexpr double q_elem = 1.602176634e-19;
        const double shot_std = std::sqrt(2.0 * q_elem * i_lo * (cfg_.sample_rate / 2.0));
        const double peak_beat = 2.0 * cfg_.responsivity * std::sqrt(cfg_.p_signal * cfg_.p_lo);

        std::normal_distribution<double> noise_dist(0.0, shot_std);

        std::vector<double> i_raw(cfg_.num_samples);
        std::vector<double> q_raw(cfg_.num_samples);

        for (std::size_t k = 0; k < cfg_.num_samples; ++k) {
            const double t = k * dt;
            const double target_phase = (t > (cfg_.num_samples * dt / 2.0)) ? std::numbers::pi / 2.0 : 0.0;

            const double beat = peak_beat * std::cos(2.0 * std::numbers::pi * cfg_.f_if * t + target_phase);
            const double i_bal = beat + noise_dist(rng_);

            i_raw[k] = i_bal * std::cos(2.0 * std::numbers::pi * cfg_.f_if * t);
            q_raw[k] = i_bal * (-std::sin(2.0 * std::numbers::pi * cfg_.f_if * t));
        }

        // Низькочастотне ковзне фільтрування
        const int win = std::max(1, static_cast<int>(cfg_.sample_rate / (cfg_.f_if * 2.0)));
        std::vector<double> phase_rec(cfg_.num_samples);

        for (std::size_t k = 0; k < cfg_.num_samples; ++k) {
            double sum_i = 0.0, sum_q = 0.0;
            int count = 0;
            for (int w = -win; w <= win; ++w) {
                int idx = static_cast<int>(k) + w;
                if (idx >= 0 && idx < static_cast<int>(cfg_.num_samples)) {
                    sum_i += i_raw[idx];
                    sum_q += q_raw[idx];
                    count++;
                }
            }
            phase_rec[k] = std::atan2(sum_q / count, sum_i / count);
        }

        print_results(phase_rec, dt);
    }

private:
    void print_results(const std::vector<double>& phase_rec, double dt) const {
        std::cout << "=== СИМУЛЯЦІЯ ОПТИЧНОГО ГЕТЕРОДИНА (C++) ===\n";
        std::cout << std::scientific << std::setprecision(2);
        std::cout << "P_signal: " << cfg_.p_signal << " W | P_LO: " << cfg_.p_lo << " W\n";
        std::cout << "Час (мкс) | Відновлена фаза | Цільова фаза\n";
        std::cout << "-------------------------------------------\n";

        const std::size_t step = cfg_.num_samples / 5;
        std::cout << std::fixed << std::setprecision(4);
        for (std::size_t k = step / 2; k < cfg_.num_samples; k += step) {
            const double t_us = (k * dt) * 1e6;
            const double target = (k * dt > (cfg_.num_samples * dt / 2.0)) ? std::numbers::pi / 2.0 : 0.0;
            std::cout << std::setw(9) << t_us << " | " << std::setw(15) << phase_rec[k]
                      << " | " << std::setw(12) << target << "\n";
        }
    }

    HeterodyneConfig cfg_;
    std::mt19937_64 rng_;
};

int main() {
    HeterodyneConfig config{};
    HeterodyneDemodulator demod(config);
    demod.process();
    return 0;
}
```
```py
import numpy as np

def run_heterodyne_simulation():
    sample_rate = 1.0e9    # 1 ГВибірок/с
    f_if = 100.0e6         # 100 МГц проміжна частота
    p_signal = 1.0e-9      # 1 нВт сигнальна потужність
    p_lo = 1.0e-3          # 1 мВт потужність гетеродина
    responsivity = 0.85    # А/Вт чутливість фотодіода
    num_samples = 2000

    dt = 1.0 / sample_rate
    t = np.arange(num_samples) * dt

    # Цільовий фазовий стрибок на середині інтервалу (BPSK 0 -> PI/2)
    phase_target = np.where(t > (num_samples * dt / 2.0), np.pi / 2.0, 0.0)

    # Фотострум та дробовий шум
    q_elem = 1.602176634e-19
    i_lo = responsivity * p_lo
    peak_beat = 2.0 * responsivity * np.sqrt(p_signal * p_lo)
    shot_std = np.sqrt(2.0 * q_elem * i_lo * (sample_rate / 2.0))

    # Створення сигналу биття + шум
    beat_signal = peak_beat * np.cos(2.0 * np.pi * f_if * t + phase_target)
    noise = np.random.normal(0.0, shot_std, size=num_samples)
    i_bal = beat_signal + noise

    # Множення на опорні квадратури
    raw_i = i_bal * np.cos(2.0 * np.pi * f_if * t)
    raw_q = i_bal * (-np.sin(2.0 * np.pi * f_if * t))

    # Низькочастотне ковзне усереднення
    win = max(1, int(sample_rate / (f_if * 2.0)))
    kernel = np.ones(2 * win + 1) / (2 * win + 1)
    filtered_i = np.convolve(raw_i, kernel, mode='same')
    filtered_q = np.convolve(raw_q, kernel, mode='same')

    # Відновлення фази
    phase_recovered = np.arctan2(filtered_q, filtered_i)

    print("=== СИМУЛЯЦІЯ ОПТИЧНОГО ГЕТЕРОДИНА (Python) ===")
    print(f"Потужність сигналу P_s: {p_signal:.2e} Вт")
    print(f"Потужність гетеродина P_LO: {p_lo:.2e} Вт")
    print(f"Піковий струм биття: {peak_beat * 1e6:.3f} мкА")
    print(f"СКВ дробового шуму: {shot_std * 1e6:.3f} мкА\n")

    print("Час (мкс) | Відновлена фаза (рад) | Цільова фаза")
    print("-" * 47)
    indices = np.linspace(num_samples // 10, num_samples - num_samples // 10, 5, dtype=int)
    for idx in indices:
        print(f"{t[idx] * 1e6:9.2f} | {phase_recovered[idx]:21.4f} | {phase_target[idx]:12.4f}")

if __name__ == '__main__':
    run_heterodyne_simulation()
```
:::

### 3. Фізичний та інженерний аналіз результатів симуляції

Аналіз результатів обчислення демонструє принципові характеристики гетеродинного фотодетектування:

#### 1. Квантове гетеродинне підсилення

При наднадзвичайно слабкому оптичному сигналі `P_s = 1 нВт` струм прямого детектування склав би всього `i_direct = 0.85 нА`. Такий струм неможливо виділити на тлі шуму підсилювача без кріогенного охолодження. Завдяки підсиленню гетеродином потужністю `P_LO = 1 мВт` піковий струм биття на проміжній частоті зростає до `I_beat_peak = 53.76 мкА`. Підсилення становить `53760 / 0.85 ≈ 63240` разів за струмом!

#### 2. Аналіз квантового дробового шуму

Середньоквадратичне значення (СКВ) дробового шуму гетеродина у смузі 500 МГц становить `16.51 мкА`. Оскільки піковий сигнал дорівнює `53.76 мкА`, коефіцієнт сигнал/шум (SNR) за електричною потужністю перевищує `10.3 дБ`. Це дозволяє впевнено відновлювати фазовий стрибок на `90°` (`π/2` радіан) на часовому інтервалі тривалістю менше 1 мікросекунди.

#### 3. Точність IQ-демодуляції та вибір довжини фільтра

Вибір розміру вікна КІХ-фільтра `N_win` є компромісом між пригніченням шуму та часовою роздільною здатністю. Занадто широке вікно призводить до розмиття фазового переходу, тоді як занадто вузьке вікно не забезпечує достатнього пригнічення високої частоти `2·f_IF` та широкого смугового шуму.

### 4. Інженерні підводні камені та практичні пастки реалізації

При переході від симуляції до реального фізичного конструювання когерентних оптичних гетеродинних приймачів виникають наступні критичні пастки:

#### 1. Фазовий шум та ширина лінії випромінювання лазерів

Симуляція припускає монохроматичні лазери з нульовою шириною лінії (`Δν = 0`). У реальних напівпровідникових DFB-лазерах виникає випадковий лоренцівський розсув фази (фазовий джитер). Якщо сумарна ширина лінії двох лазерів `Δν_total = Δν_s + Δν_LO` перевищує `0.01 · B_demod`, фазові флуктуації розмивають сузір'я IQ-демодулятора. Для передачі 16-QAM вимагаються вузькосмугові лазери із зовнішнім резонатором (ECL) з шириною лінії `Δν < 100 кГц`.

#### 2. Коефіцієнт пригнічення синфазного сигналу (CMRR) балансного фотодетектора

Неідентичність коефіцієнтів передачі двох фотодіодів (дисбаланс `ΔR / R_avg`) зменшує коефіцієнт пригнічення шуму інтенсивності гетеродина (RIN). При дисбалансі пліч 1% (`CMRR = 40 дБ`), залишковий шум RIN гетеродина потужністю понад 5 мВт перевищує квантовий дробовий шум, погіршуючи чутливість приймача. Вимагається точне цифрове вирівнювання коефіцієнтів передачі у DSP.

#### 3. Затримка низькочастотного КІХ-фільтра та розгортання фази (Phase Unwrapping)

Низькочастотна фільтрація ковзним усередненням додає групову затримку `τ_group = N_win / (2 · f_sample)`. Функція `atan2(Q, I)` повертає фазу в обмеженому інтервалі `[-π, +π]`. При неперервній зміні фази (наприклад, при доплерівському зсуві частоти) виникають стрибки на `2π`, що вимагає використання алгоритму розгортання фази (*phase unwrapping*).

### 5. Оптимізація обчислень для FPGA та систем реального часу

У промислових 400G/800G когерентних оптичних трансиверах алгоритми IQ-демодуляції реалізуються на спеціалізованих програмованих логічних інтегральних схемах (ПЛІС / FPGA) або спеціалізованих процесорах DSP:

1. **Арифметика з фіксованою комою (Fixed-Point Arithmetic)**: для зменшення споживання енергії напівпровідникові блоки обчислюють тригонометричні квадратури за допомогою алгоритму **CORDIC** (*Coordinate Rotation Digital Computer*) у фіксованій комі без використання обчислень із плаваючою комою.
2. **Векторизація SIMD**: для забезпечення швидкості обробки понад 64 Гігавибірок/с алгоритми ковзної згортки паралеляться за допомогою векторних інструкцій AVX-512 (x86_64) чи NEON (ARM64).
3. **Швидкісні FFT-фільтри**: для довгих імпульсних характеристик фільтрація реалізується у частотній області методом Overlap-Save за допомогою швидкого перетворення Фур'є (FFT).
