# ⚙️ Симуляція RAKE-демодулятора мовами C та C++

Ця вставка містить повністю робочу програмну реалізацію RAKE-демодулятора мовами C та C++. Вона демонструє процес відновлення інформаційного біта у багатопроменевому каналі зі згасанням за допомогою 3 кореляційних пальців та MRC-додавання (Maximum Ratio Combining). Приклад розрахований на симуляцію роботи цифрового модема або DSP-процесора у системах стільникового зв'язку стандарту 3G CDMA.

---

### Принцип побудови алгоритму та структура даних

Симуляція складається з двох ключових частин: моделювання середовища поширення хвиль (багатопроменевого каналу з шумом) та алгоритму цифрової обробки сигналів на приймальному боці.

1. **Моделювання передавача та каналу:**
   - Інформаційний біт `d_0 ∈ {+1, -1}` розширюється за допомогою 31-чипової ПСП-послідовності (M-послідовності).
   - Сигнал проходить крізь 3 незалежні промені з затримками `τ = {0, 4, 9}` чипів, амплітудними коефіцієнтами `a = {0.85, 0.55, 0.35}` та фазами `θ = {0.2, 1.1, 2.3}` радіан.
   - До сумарного сигналу додається комплексний адитивний білий гаусів шум (AWGN) для імітації термальних завад радіоприймача.

2. **Демодулювання та кореляційна обробка в пальцях:**
   - Кожен палець RAKE відстежує свій зсув затримки `τ_k`.
   - Виконується сковзна взаємна кореляція між вхідним зашумленим потоком та місцевою ПСП-послідовністю протягом інтервалу `CHIP_LEN`.
   - Внутрішній оцінювач каналу отримує комплексний коефіцієнт передачі `h_k = a_k · e^(j·θ_k)`.

3. **Фазування та MRC-зважування:**
   - Вихідний відлік кожного пальця множиться на спряжене значення ваги `w_k = conj(h_k)`. Це скасовує фазовий зсув `θ_k` і зважує сигнал пропорційно `a_k`.
   - Комплексні результати з усіх пальців додаються у єдину сумарну софт-метрику `total_sum`.
   - Решач порівнює дісну частину `real(total_sum)` з нульовим порогом для прийняття остаточного рішення про біт `d_0`.

---

### Детальний аналіз реалізації C та C++

У реалізації мовою **C** використовується стандартний заголовок `<complex.h>` та типи `float complex`. Структура `RakeFinger` зберігає індивідуальні налаштування затримки та оцінки каналу для кожного пальця. Функція `process_finger()` виконує обчислення кореляційного інтеграла шляхом скалярного множення елементів масиву вхідного сигналу `rx_signal` на значення ПСП-коду `PN_SEQ`.

У реалізації мовою **C++** застосовано об'єктно-орієнтовану модель. Клас `RakeReceiver` капсулює вектор ПСП-послідовності `pn_seq_` та набір пальців `fingers_`. Для роботи з комплексними числами використовується `std::complex<double>`, а генерація шуму AWGN реалізована за допомогою генератора випадкових чисел `std::mt19937` із гаусовим розподілом `std::normal_distribution`.

Обидві реалізації гарантують повну пам'ятну безпеку (RAII у C++ та статечні масиви без витоків пам'яті в C).

---

### Обчислювальна складність та апаратна ресурсоємність

У реальних вбудованих системах (FPGA чи DSP) кореляційна обробка пальців RAKE вимагає високої обчислювальної продуктивності.

Для одного пальця на кожен чип сигналу виконується:
- 1 комплексне множення або віднімання/додавання (якщо ПСП є двійковою `{-1, +1}`).
- 1 комплексне акумулювання в регістрі суматора.

При частоті чипів `f_c = 3.84 МГц` (стандарт 3G WCDMA) та наявності `L = 4` пальців, сумарна кількість арифметичних операцій становить:

```
N_ops = 4 пальці · 3.84·10⁶ чипів/с · 2 (для I та Q) ≈ 30.7 МФЛОПС / МОПС
```

Саме тому в апаратних модемах (чипсетах мобільних телефонів) пальці RAKE будуються у вигляді жорстких апаратних блоків (ASIC / FPGA DSP blocks) із паралельними акумуляторами на регістрах зсуву, тоді як процесор обробляє лише повільні софт-метрики після MRC-суматора.

---

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

#define CHIP_LEN 31
#define NUM_FINGERS 3
#define TOTAL_SAMPLES (CHIP_LEN + 16)

/* ПСП-послідовність (M-послідовність 31 чип) */
static const float PN_SEQ[CHIP_LEN] = {
    1, 1, 1, 1, -1, 1, -1, 1, 1, -1, -1, 1, 1, 1, -1, 1,
    -1, -1, -1, 1, -1, 1, -1, -1, 1, -1, -1, -1, -1, 1, -1
};

/* Специфікація пальця RAKE */
typedef struct {
    int delay_chips;            /* Часова затримка τ_k */
    float complex channel_h;    /* Оцінка каналу h_k = a_k * exp(j*theta_k) */
    float complex finger_out;   /* Результат обробки пальця */
} RakeFinger;

/* Очищення та зважування в окремому пальці */
static float complex process_finger(const float complex *rx_signal, int signal_len, 
                                   const RakeFinger *finger) {
    float complex corr = 0.0f + 0.0f * I;
    int tau = finger->delay_chips;

    /* Дерозширення: множення на зсунуту ПСП та інтегрування */
    for (int i = 0; i < CHIP_LEN; i++) {
        if (i + tau < signal_len) {
            corr += rx_signal[i + tau] * PN_SEQ[i];
        }
    }
    corr /= (float)CHIP_LEN;

    /* MRC ваговий коефіцієнт: w_k = conj(h_k) */
    float complex weight = conjf(finger->channel_h);

    return corr * weight;
}

int main(void) {
    /* Параметри каналу для 3 променів */
    int delays[NUM_FINGERS] = {0, 4, 9};
    float amps[NUM_FINGERS] = {0.85f, 0.55f, 0.35f};
    float phases[NUM_FINGERS] = {0.2f, 1.1f, 2.3f};

    /* Переданий інформаційний символ (+1) */
    float tx_bit = 1.0f;

    /* Моделювання вхідного сигналу r(t) */
    float complex rx_signal[TOTAL_SAMPLES] = {0};

    for (int k = 0; k < NUM_FINGERS; k++) {
        float complex h_k = amps[k] * (cosf(phases[k]) + I * sinf(phases[k]));
        int tau = delays[k];

        for (int i = 0; i < CHIP_LEN; i++) {
            rx_signal[i + tau] += tx_bit * PN_SEQ[i] * h_k;
        }
    }

    /* Додавання шуму AWGN */
    for (int i = 0; i < TOTAL_SAMPLES; i++) {
        float n_re = ((float)rand() / RAND_MAX - 0.5f) * 0.3f;
        float n_im = ((float)rand() / RAND_MAX - 0.5f) * 0.3f;
        rx_signal[i] += n_re + I * n_im;
    }

    /* Конфігурація RAKE-приймача */
    RakeFinger fingers[NUM_FINGERS];
    for (int k = 0; k < NUM_FINGERS; k++) {
        fingers[k].delay_chips = delays[k];
        /* У реальному приймачі h_k оцінюється за пілот-сигналом */
        fingers[k].channel_h = amps[k] * (cosf(phases[k]) + I * sinf(phases[k]));
    }

    /* Обробка на пальцях та MRC додавання */
    float complex total_sum = 0.0f + 0.0f * I;
    printf("=== Демодулювання пальців RAKE (C) ===\n");

    for (int k = 0; k < NUM_FINGERS; k++) {
        fingers[k].finger_out = process_finger(rx_signal, TOTAL_SAMPLES, &fingers[k]);
        total_sum += fingers[k].finger_out;

        printf("Палець %d (τ=%d): вихід = %+.3f %+.3fj (абс = %.3f)\n",
               k, fingers[k].delay_chips,
               crealf(fingers[k].finger_out), cimagf(fingers[k].finger_out),
               cabsf(fingers[k].finger_out));
    }

    /* Прийняття рішення */
    float soft_decision = crealf(total_sum);
    int detected_bit = (soft_decision > 0.0f) ? 1 : -1;

    printf("---------------------------------------\n");
    printf("Сумарний MRC сигнал: %+.3f %+.3fj\n", crealf(total_sum), cimagf(total_sum));
    printf("Детектований біт: %d (оригінал: %+d)\n", detected_bit, (int)tx_bit);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <complex>
#include <random>
#include <numeric>
#include <iomanip>

class RakeReceiver {
public:
    using Complex = std::complex<double>;

    struct Finger {
        int delay_chips;
        Complex channel_h;
        Complex finger_output{0.0, 0.0};
    };

    explicit RakeReceiver(std::vector<double> pn_sequence)
        : pn_seq_(std::move(pn_sequence)) {}

    void set_fingers(std::vector<Finger> fingers) {
        fingers_ = std::move(fingers);
    }

    Complex process(const std::vector<Complex>& rx_signal) {
        Complex total_sum{0.0, 0.0};

        for (auto& finger : fingers_) {
            Complex corr{0.0, 0.0};
            const int tau = finger.delay_chips;

            for (size_t i = 0; i < pn_seq_.size(); ++i) {
                if (i + tau < rx_signal.size()) {
                    corr += rx_signal[i + tau] * pn_seq_[i];
                }
            }
            corr /= static_cast<double>(pn_seq_.size());

            // MRC weighting: w_k = conj(h_k)
            const Complex weight = std::conj(finger.channel_h);
            finger.finger_output = corr * weight;

            total_sum += finger.finger_output;
        }

        return total_sum;
    }

    const std::vector<Finger>& fingers() const { return fingers_; }

private:
    std::vector<double> pn_seq_;
    std::vector<Finger> fingers_;
};

int main() {
    // 31-чипова PN послідовність
    const std::vector<double> pn_seq = {
        1, 1, 1, 1, -1, 1, -1, 1, 1, -1, -1, 1, 1, 1, -1, 1,
        -1, -1, -1, 1, -1, 1, -1, -1, 1, -1, -1, -1, -1, 1, -1
    };

    const size_t total_samples = pn_seq.size() + 16;
    using Complex = std::complex<double>;

    // Параметри багатопроменевого каналу
    struct Path { int delay; double amp; double phase; };
    const std::vector<Path> paths = {
        {0, 0.85, 0.2},
        {4, 0.55, 1.1},
        {9, 0.35, 2.3}
    };

    const double tx_bit = 1.0;
    std::vector<Complex> rx_signal(total_samples, Complex{0.0, 0.0});

    // Формування каналу
    for (const auto& path : paths) {
        Complex h_k = std::polar(path.amp, path.phase);
        for (size_t i = 0; i < pn_seq.size(); ++i) {
            rx_signal[i + path.delay] += tx_bit * pn_seq[i] * h_k;
        }
    }

    // AWGN шум
    std::mt19937 rng(42);
    std::normal_distribution<double> noise_dist(0.0, 0.15);
    for (auto& sample : rx_signal) {
        sample += Complex{noise_dist(rng), noise_dist(rng)};
    }

    // Налаштування RAKE приймача
    RakeReceiver rake(pn_seq);
    std::vector<RakeReceiver::Finger> fingers;
    for (const auto& path : paths) {
        fingers.push_back({path.delay, std::polar(path.amp, path.phase)});
    }
    rake.set_fingers(fingers);

    // Виконання прийому
    Complex total_mrc = rake.process(rx_signal);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "=== Демодулювання пальців RAKE (C++) ===\n";
    for (size_t i = 0; i < rake.fingers().size(); ++i) {
        const auto& f = rake.fingers()[i];
        std::cout << "Палець " << i << " (τ=" << f.delay_chips
                  << "): вихід = " << f.finger_output
                  << " (абс = " << std::abs(f.finger_output) << ")\n";
    }

    std::cout << "-----------------------------------------\n";
    std::cout << "Сумарний MRC сигнал: " << total_mrc << "\n";
    std::cout << "Детектований біт: " << (total_mrc.real() > 0 ? 1 : -1)
              << " (оригінал: " << static_cast<int>(tx_bit) << ")\n";

    return 0;
}
```
:::

---

### Аналіз результатів симуляції та крайові випадки

При виконанні програми кожен палець витягує свою частку енергії переданого біта. Завдяки поворотній фазі `w_k = conj(h_k)` усередині MRC-множника виходи окремих пальців повертаються до додатної дійсної осі. Як результат, корисний сигнал підсилюється пропорційно сумі квадратів амплітуд `a_0² + a_1² + a_2²`, тоді як випадкові шумові складові з додаються некогерентно. Це гарантує правильне прийняття рішення навіть за умов високого рівня завад у каналі.

Розглянемо важливі крайові випадки, які слід враховувати під час практичного проектування цифрових модемів:
1. **Помилка рассинхронізації затримок `Δτ < T_c / 2`:** Якщо затримка пальця відхиляється від реального піку променя більше ніж на пів чипа, значення автокореляції ПСП стрімко спадає, і палець втрачає до 50% корисного сигналу. Для усунення цього ефекту в реальних DSP застосовують внутрішній контур Early-Late DLL tracking.
2. **Падіння потужності променя нижче порогу:** Якщо один із відбитих променів згасає (наприклад, `a_2 < 0.05`), його внесок у MRC-суму стає мізерним, але шум на виході корелятора додається до загальної суми. Реальний приймач повинен мати алгоритм порогової селекції (*finger thresholding*), який відключає пальці із SNR нижчим за допустиму межу.
3. **Ефект швидкого Доплерівського зсуву:** При швидкостях руху абонента понад 120 км/год фаза каналу `θ_k(t)` змінюється надто швидко для усереднення пілотними символами. У таких умовах алгоритм оцінювання каналу має використовувати фільтрацію Калмана для екстраполяції фази каналу між пілотними інтервалами.
