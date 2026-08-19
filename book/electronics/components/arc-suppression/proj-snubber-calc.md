# ⚙️ Моделювання та розрахунок перехідних процесів комутації й демпфування

Інженерний розрахунок комутаційних кіл не може обмежуватися виключно аналітичними серветковими формулами. Реальні схеми містять нелінійні ємності напівпровідникових переходів, паразитно-розподілені індуктивності друкованих провідників, паразитний опір монтажу та дискретність номіналів стандартних рядів деталей (E24/E96). Практична реалізація потребує створення обчислювальних інструментів для чисельного інтегрування диференціальних рівнянь перехідного процесу, алгоритмів автоматизованого підбору компонентів та програмних засобів усунення наслідків механічного брязкоту контактів у мікроконтролерних системах керування.

---

### 1. Чисельний аналіз перехідного процесу розмикання кола: метод Рунге — Кутти

Для точного відстеження напруги на комутаційному ключі та перевірки умов виникнення дуги розроблено симулятор на основі класичного чисельного методу Рунге — Кутти четвертого порядку (RK4).

#### Математична постановка задачі та аналіз чисельної стійкості
У просторі станів система другого порядку описується вектором стану `S = [i(t), v_c(t)]ᵀ`, де `i(t)` — струм крізь індуктивність навантаження, а `v_c(t)` — напруга на конденсаторі снабера.

Диференціальні рівняння системи в момент після розмикання контактів:

```
di(t) / dt = (V_cc - v_c(t) - i(t) · (R_s + R_load)) / L
dv_c(t) / dt = i(t) / C_s
```

Миттєва напруга на розімкненому ключі складається з напруги на ємності та спаду напруги на резисторі снабера:

```
v_switch(t) = v_c(t) + i(t) · R_s
```

При розв'язанні таких систем простий метод Ейлера виявляється чисельно нестійким або вимагає мізерного кроку `dt < L / (R_s + R_load) · 0.01` (пікосекундний діапазон), оскільки жорсткість системи диференціальних рівнянь визначається високою власною частотою `ω_0 = 1 / √(L · C_s)`. Метод Рунге — Кутти 4-го порядку (RK4) забезпечує локальну похибку порядку `O(dt⁵)` та глобальну похибку `O(dt⁴)`, що дозволяє впевнено моделювати високочастотний дзвін з кроком `dt = 10⁻⁷…10⁻⁸ с` без накопичення фазової чи амплітудної похибки.

Чисельний алгоритм покроково обчислює зміну стану з обраним кроком за часом `dt`, фіксує максимальний сплеск напруги `V_peak`, розраховує повну енергію, розсіяну на резисторі за законом Джоуля — Ленца:

```
E_res = ∫ i²(t) · R_s · dt
```
та перевіряє критерій запалювання електричної дуги Гольма: чи перевищує миттєва напруга на розриві `v_switch(t) > 12 В` за умови, що струм у каналі все ще перевищує поріг горіння дуги `i(t) > 0.4 А`.

#### Фізичні фази перехідного процесу в симуляторі
Моделювання чітко розкриває три послідовні фази розмикання кола:
1. **Фаза початкового резистивного стрибка (0…50 нс)**: струм котушки `i(0) = I_0` не може змінитися стрибком, тому в першу ж мить він протікає через демпфувальний резистор `R_s`. Напруга на ключі стрибає від нуля до `V_jump = I_0 · R_s`. Якщо `R_s` завеликий, цей сплеск одразу фіксується як `v_peak`.
2. **Фаза заряду ємності та поглинання енергії магнітного поля (50 нс…10 мкс)**: струм індуктивності заряджає конденсатор `C_s`. Енергія магнітного поля перекачується в електричне поле ємності. Напруга на конденсаторі досягає максимуму, коли струм переходить через нуль.
3. **Фаза резистивного розсіювання та згасання коливань (10 мкс…5 мс)**: накопичена енергія циркулює між `L` та `C_s`, експоненційно розсіюючись у вигляді тепла на опорі `R_s`. При критичному демпфуванні коливання взагалі відсутні — напруга плавно спадає до напруги живлення `V_cc`.

Нижче наведено паралельні реалізації симулятора мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

// Параметри електричного кола комутації
typedef struct {
    double v_cc;        // Напруга живлення, В
    double i_0;         // Початковий струм котушки, А
    double l_ind;       // Індуктивність навантаження, Гн
    double r_load;      // Власний активний опір обмотки, Ом
    double r_snubber;   // Демпфувальний опір снабера, Ом
    double c_snubber;   // Ємність снабера, Ф
} CircuitParams;

// Результати моделювання перехідного процесу
typedef struct {
    double v_peak;      // Максимальна зафіксована напруга на ключі, В
    double energy_res;  // Енергія, розсіяна на резисторі у вигляді тепла, Дж
    double t_settle;    // Час згасання струму до 1 % від початкового, с
    bool arc_ignited;   // Прапорець виникнення стійкої дуги (U > 12 В при I > 0.4 А)
} SimResult;

typedef struct {
    double i;   // Миттєвий струм через індуктивність
    double vc;  // Миттєва напруга на ємності
} State;

// Обчислення похідних системи диференціальних рівнянь
static void compute_derivatives(const CircuitParams* p, const State* s, double* di_dt, double* dvc_dt) {
    *di_dt = (p->v_cc - s->vc - s->i * (p->r_snubber + p->r_load)) / p->l_ind;
    *dvc_dt = s->i / p->c_snubber;
}

// Запуск симуляції методом Рунге - Кутти 4-го порядку (RK4)
SimResult simulate_turn_off(const CircuitParams p, double dt, double t_max) {
    SimResult res = { .v_peak = 0.0, .energy_res = 0.0, .t_settle = 0.0, .arc_ignited = false };
    State s = { .i = p.i_0, .vc = 0.0 };
    
    double t = 0.0;
    const double i_threshold = p.i_0 * 0.01;
    bool settled = false;

    while (t < t_max) {
        // Миттєва напруга на розімкненому ключі
        double v_sw = s.vc + s.i * p.r_snubber;
        if (v_sw > res.v_peak) {
            res.v_peak = v_sw;
        }

        // Перевірка порогових умов горіння дуги
        if (v_sw > 12.0 && s.i > 0.4) {
            res.arc_ignited = true;
        }

        // Інтегрування розсіюваної теплової енергії на резисторі
        res.energy_res += (s.i * s.i * p.r_snubber) * dt;

        if (!settled && fabs(s.i) < i_threshold) {
            res.t_settle = t;
            settled = true;
        }

        // Класичний алгоритм RK4
        double k1_i, k1_vc;
        compute_derivatives(&p, &s, &k1_i, &k1_vc);

        State s2 = { s.i + 0.5 * dt * k1_i, s.vc + 0.5 * dt * k1_vc };
        double k2_i, k2_vc;
        compute_derivatives(&p, &s2, &k2_i, &k2_vc);

        State s3 = { s.i + 0.5 * dt * k2_i, s.vc + 0.5 * dt * k2_vc };
        double k3_i, k3_vc;
        compute_derivatives(&p, &s3, &k3_i, &k3_vc);

        State s4 = { s.i + dt * k3_i, s.vc + dt * k3_vc };
        double k4_i, k4_vc;
        compute_derivatives(&p, &s4, &k4_i, &k4_vc);

        s.i += (dt / 6.0) * (k1_i + 2.0 * k2_i + 2.0 * k3_i + k4_i);
        s.vc += (dt / 6.0) * (k1_vc + 2.0 * k2_vc + 2.0 * k3_vc + k4_vc);

        t += dt;
    }

    return res;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <array>
#include <utility>

struct CircuitParams {
    double v_cc{24.0};        // Напруга живлення, В
    double i_0{0.5};          // Початковий струм котушки, А
    double l_ind{0.08};       // Індуктивність навантаження, Гн
    double r_load{48.0};      // Власний опір обмотки, Ом
    double r_snubber{91.0};   // Опір снабера, Ом
    double c_snubber{10e-6};  // Ємність снабера, Ф
};

struct SimResult {
    double v_peak{0.0};
    double energy_res{0.0};
    double t_settle{0.0};
    bool arc_ignited{false};
};

class SnubberSimulator {
public:
    explicit SnubberSimulator(CircuitParams params) noexcept : params_{params} {}

    [[nodiscard]] SimResult run(double dt = 1e-7, double t_max = 5e-3) const noexcept {
        SimResult res{};
        double current_i = params_.i_0;
        double current_vc = 0.0;
        double t = 0.0;
        const double i_threshold = params_.i_0 * 0.01;
        bool settled = false;

        auto compute_derivs = [this](double i, double vc) noexcept -> std::pair<double, double> {
            double di = (params_.v_cc - vc - i * (params_.r_snubber + params_.r_load)) / params_.l_ind;
            double dvc = i / params_.c_snubber;
            return {di, dvc};
        };

        while (t < t_max) {
            const double v_sw = current_vc + current_i * params_.r_snubber;
            if (v_sw > res.v_peak) {
                res.v_peak = v_sw;
            }

            if (v_sw > 12.0 && current_i > 0.4) {
                res.arc_ignited = true;
            }

            res.energy_res += (current_i * current_i * params_.r_snubber) * dt;

            if (!settled && std::abs(current_i) < i_threshold) {
                res.t_settle = t;
                settled = true;
            }

            // Інтегрування RK4
            const auto [k1_i, k1_vc] = compute_derivs(current_i, current_vc);
            const auto [k2_i, k2_vc] = compute_derivs(current_i + 0.5 * dt * k1_i, current_vc + 0.5 * dt * k1_vc);
            const auto [k3_i, k3_vc] = compute_derivs(current_i + 0.5 * dt * k2_i, current_vc + 0.5 * dt * k2_vc);
            const auto [k4_i, k4_vc] = compute_derivs(current_i + dt * k3_i, current_vc + dt * k3_vc);

            current_i += (dt / 6.0) * (k1_i + 2.0 * k2_i + 2.0 * k3_i + k4_i);
            current_vc += (dt / 6.0) * (k1_vc + 2.0 * k2_vc + 2.0 * k3_vc + k4_vc);
            t += dt;
        }

        return res;
    }

private:
    CircuitParams params_;
};
```
:::

---

### 2. Автоматизований калькулятор підбору компонентів за рядом E24

Розрахункові значення ємності й опору майже ніколи не збігаються з реальними номіналами деталей, що випускаються промисловістю. Алгоритм підбору виконує такі інженерні кроки:

1. **Обчислення теоретичної ємності `C_exact`** за допустимою амплітудою сплеску `V_max` та накопиченою енергією магнітного поля:
   ```
   C_exact = (L · I²) / (V_max² - V_cc²)
   ```
2. **Квантування ємності до найближчого більшого або рівного номіналу ряду E24** (`1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1`).
3. **Обчислення характеристичного опору** `Z_0 = √(L / C_e24)` та підбір найближчого резистора ряду E24 для забезпечення критичного демпфування `ζ ≈ 0.7…1.0`.
4. **Розрахунок теплового дерейтингу резистора**: паспортна розсіювана потужність резистора повинна перевищувати розрахункову потужність циклічних втрат `P = C · V_cc² · f_sw` щонайменше у 2 рази (коефіцієнт запасу 2.0) для забезпечення тривалого ресурсу без перегріву.

#### Алгоритм логарифмічного пошуку в мантисах E24
Стандартний ряд E24 має геометричну прогресію зі знаменником `q = 10^(1/24) ≈ 1.10`. Щоб знайти найближчий стандартний номінал для довільного дійсного числа `X > 0`:
1. Відокремлюємо десятковий порядок: `exp_val = floor(log10(X))`.
2. Знаходимо мантису: `mantissa = X / 10^(exp_val)`.
3. У масиві 24 базових значень `E24_MANTISSAS` знаходимо елемент із мінімальною абсолютною різницею `|mantissa - E24[k]|`.
4. Множимо знайдену мантису на `10^(exp_val)`.

:::tabs
```c
#include <stdio.h>
#include <math.h>

// Базові мантиси номіналів стандартного ряду E24
static const double E24_MANTISSAS[24] = {
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
};

// Функція квантування до найближчого номіналу ряду E24
double find_closest_e24(double value) {
    if (value <= 0.0) return 0.0;
    double exp_val = floor(log10(value));
    double mantissa = value / pow(10.0, exp_val);

    double best_mantissa = E24_MANTISSAS[0];
    double min_delta = fabs(mantissa - E24_MANTISSAS[0]);

    for (int i = 1; i < 24; ++i) {
        double delta = fabs(mantissa - E24_MANTISSAS[i]);
        if (delta < min_delta) {
            min_delta = delta;
            best_mantissa = E24_MANTISSAS[i];
        }
    }
    return best_mantissa * pow(10.0, exp_val);
}

typedef struct {
    double c_exact;        // Точна розрахункова ємність, Ф
    double c_standard;     // Стандартна ємність з ряду E24, Ф
    double r_exact;        // Точний характеристичний опір, Ом
    double r_standard;     // Стандартний опір з ряду E24, Ом
    double p_resistor_w;   // Необхідна потужність резистора з 2-кратним запасом, Вт
} SnubberDesignOutput;

SnubberDesignOutput design_rc_snubber(double v_cc, double i_load, double l_ind, double f_sw, double v_max_allowable) {
    SnubberDesignOutput out;
    double delta_v_sq = (v_max_allowable * v_max_allowable) - (v_cc * v_cc);
    if (delta_v_sq <= 0.0) delta_v_sq = 1.0;
    
    out.c_exact = (l_ind * i_load * i_load) / delta_v_sq;
    out.c_standard = find_closest_e24(out.c_exact);

    out.r_exact = sqrt(l_ind / out.c_standard);
    out.r_standard = find_closest_e24(out.r_exact);

    // Втрати потужності: P = C * V_cc^2 * f_sw * Margin (2.0)
    out.p_resistor_w = out.c_standard * v_cc * v_cc * f_sw * 2.0;

    return out;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <array>
#include <algorithm>

class SnubberDesignEngine {
public:
    static constexpr std::array<double, 24> E24_MANTISSAS = {
        1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
        3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
    };

    struct Result {
        double c_exact{0.0};
        double c_standard{0.0};
        double r_exact{0.0};
        double r_standard{0.0};
        double p_rating_w{0.0};
    };

    [[nodiscard]] static double quantize_to_e24(double value) noexcept {
        if (value <= 0.0) return 0.0;
        const double exp_val = std::floor(std::log10(value));
        const double mantissa = value / std::pow(10.0, exp_val);

        auto nearest = std::min_element(E24_MANTISSAS.begin(), E24_MANTISSAS.end(),
            [mantissa](double a, double b) noexcept {
                return std::abs(mantissa - a) < std::abs(mantissa - b);
            });

        return *nearest * std::pow(10.0, exp_val);
    }

    [[nodiscard]] static Result compute(double v_cc, double i_load, double l_ind, double f_sw, double v_max) noexcept {
        Result res{};
        const double v_diff_sq = (v_max * v_max) - (v_cc * v_cc);
        const double denom = (v_diff_sq > 0.0) ? v_diff_sq : 1.0;

        res.c_exact = (l_ind * i_load * i_load) / denom;
        res.c_standard = quantize_to_e24(res.c_exact);

        res.r_exact = std::sqrt(l_ind / res.c_standard);
        res.r_standard = quantize_to_e24(res.r_exact);

        // 100 % запас за тепловою потужністю (коефіцієнт 2.0)
        res.p_rating_w = res.c_standard * v_cc * v_cc * f_sw * 2.0;
        return res;
    }
};
```
:::

---

### 3. Програмне придушення брязкоту контактів (Debounce State Machine)

Коли мікроконтролер опитує стан механічних контактів реле, кінцевих вимикачів чи кнопок, пружний відскік контактної пари породжує серію швидких імпульсів розмикання тривалістю від 0.5 до 5 мс. Якщо прошивка реагує на кожен фронт перериванням, виникає лавиноподібне перевантаження процесора та багаторазове вмикання силового навантаження з виникненням руйнівних мікродуг.

#### Фізика контактного брязкоту та вимоги до алгоритму
Пружна пластина якоря реле після зіткнення з нерухомим контактом зазнає серії затухаючих механічних коливань. Кожен відскік розриває електричний контакт на час від 50 до 500 мкс. Якщо в цей час комутується індуктивне навантаження, кожен відскік породжує мікродугу, розплавляючи метал у точці дотику.

Якщо алгоритм обробки кнопок чи реле використовує просту перевірку з затримкою `delay(20)`, процесор безплідно блокується, втрачаючи можливість обслуговувати інші вузли системи. Професійний підхід полягає у використанні неблокуючого **інтегрувального фільтра стабільності (Integrator Debounce Filter)**, що викликається з фіксованою дискретизацією (наприклад, у системному таймерному перериванні кожну 1 мс).

Стан контакту вважається зміненим лише тоді, коли новий логічний рівень безперервно утримується протягом `N_samples` вибірок (типово 10–20 вибірок, що відповідає 10–20 мс стабільності). Будь-який випадковий імпульс або переривання брязкоту скидає лічильник у нуль, запобігаючи хибному спрацьовуванню.

#### Безпека в багатопотокових RTOS та обробниках переривань (ISR)
У системах реального часу (FreeRTOS, Zephyr) виклик `debounce_engine_process` виконується у низькопріоритетній задачі таймера або безпосередньо в обробнику тика. Коли фільтр фіксує зміну стану, він генерує подію (FreeRTOS `xQueueSendFromISR` або `xTaskNotifyFromISR`), сповіщаючи задачу керування силовим приводом. Це виключає блокування ягідних переривань і гарантує детермінований час реакції.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint8_t counter;       // Поточний лічильник стабільності вибірки
    uint8_t threshold;     // Поріг підтвердження стану (кількість відліків)
    bool stable_state;     // Відфільтрований стабільний стан контакту
} DebounceEngine;

void debounce_engine_init(DebounceEngine* eng, uint8_t filter_samples) {
    eng->counter = 0;
    eng->threshold = filter_samples;
    eng->stable_state = false;
}

// Викликається періодично з системного таймера (наприклад, системний тик SysTick 1 мс)
bool debounce_engine_process(DebounceEngine* eng, bool raw_input_pin) {
    if (raw_input_pin != eng->stable_state) {
        eng->counter++;
        if (eng->counter >= eng->threshold) {
            eng->stable_state = raw_input_pin;
            eng->counter = 0;
        }
    } else {
        eng->counter = 0; // Скидання лічильника при будь-якому випадковому коливанні
    }
    return eng->stable_state;
}
```
```cpp
#include <cstdint>

template <std::uint8_t StabilityThreshold = 15>
class ContactDebounceFilter {
public:
    constexpr ContactDebounceFilter() = default;

    // Періодична обробка вибірки у таймерному перериванні
    bool process_sample(bool raw_input_pin) noexcept {
        if (raw_input_pin != stable_state_) {
            if (++sample_counter_ >= StabilityThreshold) {
                stable_state_ = raw_input_pin;
                sample_counter_ = 0;
            }
        } else {
            sample_counter_ = 0;
        }
        return stable_state_;
    }

    [[nodiscard]] constexpr bool get_state() const noexcept {
        return stable_state_;
    }

private:
    std::uint8_t sample_counter_{0};
    bool stable_state_{false};
};
```
:::

Програмна фільтрація разом із апаратними демпфувальними ланцюгами утворює багаторівневий комплекс захисту комутаційного вузла, повністю усуваючи дугоутворення та збільшуючи напрацювання контактів на відмову в десятки разів.
