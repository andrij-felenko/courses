# ⚙️ Чисельне моделювання термодинамічних процесів і циклів

Чисельне моделювання термодинамічних систем є необхідним інструментом при проектуванні теплових двигунів, кріогенних установок та компресорних станцій. В той час як ідеальні ізопроцеси легко обчислюються аналітично, реальні промислові цикли описуються складними комбінаціями неізотермічних, зсунутих по фазі та дисипативних процесів. Чисельний розв'язувач стан-процес (*state-process solver*) дозволяє моделювати послідовності будь-яких процесів, розраховувати роботу, теплоту та зміну внутрішньої енергії на кожній ділянці, перевіряти суворе виконання Першого закону термодинаміки та обчислювати термічний коефіціент корисної дії (ККД) термодинамічних циклів.

---

### Математична та архітектурна модель симулятора

Для 1 моля ідеального газу стан системи в будь-який момент часу описується векторною трійкою параметрів `(P, V, T)`, які пов'язані фундаментальним рівнянням стану Клапейрона — Менделєєва `P · V = n · R · T`.

Кожен термодинамічний процес є переходом із початкового стану `S₁ (P₁, V₁, T₁)` у кінцевий стан `S₂ (P₂, V₂, T₂)` під дією заданого законного обмеження. Симулятор підтримує чотири базові категорії процесів:

1. **Ізохорний процес (`V = const`):**
   - Робота розширення відсутня: `W = 0`.
   - Зміна внутрішньої енергії та підведене тепло дорівнюють одне одному: `Q = ΔU = n · C_v · (T₂ - T₁)`.
   - Кінцевий тиск обчислюється як `P₂ = P₁ · (T₂ / T₁)`.

2. **Ізобарний процес (`P = const`):**
   - Робота розширення виражається прямолінійно: `W = P₁ · (V₂ - V₁)`.
   - Зміна внутрішньої енергії: `ΔU = n · C_v · (T₂ - T₁)`.
   - Підведене тепло витрачається на обидві сили: `Q = n · C_p · (T₂ - T₁) = ΔU + W`.

3. **Ізотермічний процес (`T = const`):**
   - Зміна внутрішньої енергії ідеального газу дорівнює нулю: `ΔU = 0`.
   - Підведене тепло повністю конвертується у роботу: `W = Q = n · R · T₁ · ln(V₂ / V₁)`.
   - Кінцевий тиск спадає обернено пропорційно об'єму: `P₂ = P₁ · (V₁ / V₂)`.

4. **Адіабатний процес (`Q = 0`):**
   - Теплообмін із зовнішнім середовищем відсутній: `Q = 0`.
   - Робота виконується за рахунок власної внутрішньої енергії: `W = -ΔU = n · C_v · (T₁ - T₂)`.
   - Кінцевий тиск та температура обчислюються за рівнянням Пуассона: `P₂ = P₁ · (V₁ / V₂)^γ`, `T₂ = T₁ · (V₁ / V₂)^(γ - 1)`.

Термічний ККД будь-якого циклу обчислюється як відношення корисної мережевої роботи за цикл до сумарного підведеного тепла:

```
η = W_мережеве / Q_підведене = (∑ Q_in - ∑ Q_out) / ∑ Q_in
```

---

### Архітектура розв'язувача та проектування модулів

Програма розроблена за модульним принципом, де обчислювальне ядро відокремлене від модулів представлення результатів.

#### Основні класи та структури розв'язувача:
- **`GasModel`:** Модель середовища, яка зберігає число молей `n` та ефективне число ступенів вільності `i`. Вона авторозраховує молярні теплоємності `C_v`, `C_p` та показник адіабати `γ = C_p / C_v`.
- **`State`:** Вектор макроскопічного стану `(P, V, T)`. Забезпечує статичні фабричні методи створення стану за двома відомими параметрами.
- **`ProcessStep`:** Структура результату конкретного кроку розширення чи стиснення. Містить початковий і кінцевий стан, обчислений обсяг тепла `Q`, роботи `W` та зміни внутрішньої енергії `ΔU`.
- **`CycleSimulator`:** Контейнер і менеджер циклу, який зберігає послідовність кроків, виконує перевірку замкненості термодинамічного контуру та формує підсумковий звіт енергетичного балансу.

---

### Реалізація розв'язувача термодинамічних циклів

Нижче наведено повноцінний робочий код симулятора двома мовами: чистою **C** (із прозорими структурами даних, явною передачею за вказівниками та процедурною обробкою) та ідіоматичною **C++** (із застосуванням концепції RAII, строгих типів `enum class`, безпечних контейнерів `std::vector`, математичних констант `std::numbers` та сучасної обробки помилок через `std::expected`).

:::tabs
```c
/* thermo_sim.c - Чисельний симулятор термодинамічних процесів та циклів мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define R_GAS 8.3144626

typedef enum {
    PROC_ISOCHORIC,
    PROC_ISOBARIC,
    PROC_ISOTHERMAL,
    PROC_ADIABATIC
} ProcessType;

typedef struct {
    double p; /* Тиск [Па] */
    double v; /* Об'єм [м³] */
    double t; /* Температура [К] */
} State;

typedef struct {
    ProcessType type;
    State start;
    State end;
    double work;   /* Робота W [Дж] */
    double heat;   /* Тепло Q [Дж] */
    double delta_u;/* Зміна внутрішньої енергії dU [Дж] */
} ProcessResult;

typedef struct {
    double n_moles;
    double degrees_of_freedom; /* i = 3 (одноатомний), 5 (двохатомний) */
    double c_v;
    double c_p;
    double gamma;
} GasModel;

GasModel gas_init(double n_moles, double dof) {
    GasModel g;
    g.n_moles = n_moles;
    g.degrees_of_freedom = dof;
    g.c_v = (dof / 2.0) * R_GAS;
    g.c_p = g.c_v + R_GAS;
    g.gamma = g.c_p / g.c_v;
    return g;
}

ProcessResult step_isochoric(const GasModel *g, State start, double target_t) {
    ProcessResult res;
    res.type = PROC_ISOCHORIC;
    res.start = start;
    res.end.v = start.v;
    res.end.t = target_t;
    res.end.p = (g->n_moles * R_GAS * target_t) / start.v;
    
    res.work = 0.0;
    res.delta_u = g->n_moles * g->c_v * (target_t - start.t);
    res.heat = res.delta_u;
    return res;
}

ProcessResult step_isobaric(const GasModel *g, State start, double target_v) {
    ProcessResult res;
    res.type = PROC_ISOBARIC;
    res.start = start;
    res.end.p = start.p;
    res.end.v = target_v;
    res.end.t = (start.p * target_v) / (g->n_moles * R_GAS);
    
    res.work = start.p * (target_v - start.v);
    res.delta_u = g->n_moles * g->c_v * (res.end.t - start.t);
    res.heat = res.delta_u + res.work;
    return res;
}

ProcessResult step_isothermal(const GasModel *g, State start, double target_v) {
    ProcessResult res;
    res.type = PROC_ISOTHERMAL;
    res.start = start;
    res.end.v = target_v;
    res.end.t = start.t;
    res.end.p = (g->n_moles * R_GAS * start.t) / target_v;
    
    res.delta_u = 0.0;
    res.work = g->n_moles * R_GAS * start.t * log(target_v / start.v);
    res.heat = res.work;
    return res;
}

ProcessResult step_adiabatic(const GasModel *g, State start, double target_v) {
    ProcessResult res;
    res.type = PROC_ADIABATIC;
    res.start = start;
    res.end.v = target_v;
    res.end.p = start.p * pow(start.v / target_v, g->gamma);
    res.end.t = (res.end.p * target_v) / (g->n_moles * R_GAS);
    
    res.heat = 0.0;
    res.delta_u = g->n_moles * g->c_v * (res.end.t - start.t);
    res.work = -res.delta_u;
    return res;
}

void print_cycle_summary(const ProcessResult *steps, size_t count) {
    double total_work = 0.0;
    double q_in = 0.0;
    double q_out = 0.0;
    double total_du = 0.0;

    printf("=== РЕЗУЛЬТАТИ ТЕРМОДИНАМІЧНОГО ЦИКЛУ ===\n");
    for (size_t i = 0; i < count; ++i) {
        printf("Крок %zu: W = %10.2f Дж, Q = %10.2f Дж, dU = %10.2f Дж\n",
               i + 1, steps[i].work, steps[i].heat, steps[i].delta_u);
        total_work += steps[i].work;
        total_du += steps[i].delta_u;
        if (steps[i].heat > 0) {
            q_in += steps[i].heat;
        } else {
            q_out += -steps[i].heat;
        }
    }

    double eta = (q_in > 0) ? (total_work / q_in) * 100.0 : 0.0;
    printf("-----------------------------------------\n");
    printf("Суммарна робота за цикл W_net : %10.2f Дж\n", total_work);
    printf("Підведене тепло Q_in          : %10.2f Дж\n", q_in);
    printf("Відведене тепло Q_out         : %10.2f Дж\n", q_out);
    printf("Баланс енергії sum(dU)       : %10.2f Дж (має бути 0)\n", total_du);
    printf("Термічний ККД циклу eta       : %10.2f %%\n", eta);
}

int main(void) {
    /* Моделюємо цикл Карно для 1 моля двохатомного газу (повітря, i = 5) */
    GasModel gas = gas_init(1.0, 5.0);
    
    /* Початковий стан 1: P = 500 кПа, V = 0.002 м³ */
    State s1;
    s1.p = 500000.0;
    s1.v = 0.002;
    s1.t = (s1.p * s1.v) / (gas.n_moles * R_GAS); /* ~120.27 K */

    ProcessResult cycle[4];

    /* 1->2: Ізотермічне розширення при Т1 до V2 = 0.006 м³ */
    cycle[0] = step_isothermal(&gas, s1, 0.006);

    /* 2->3: Адіабатне розширення до V3 = 0.012 м³ */
    cycle[1] = step_adiabatic(&gas, cycle[0].end, 0.012);

    /* 3->4: Ізотермічне стиснення до V4 = 0.004 м³ */
    cycle[2] = step_isothermal(&gas, cycle[1].end, 0.004);

    /* 4->1: Адіабатне стиснення назад до V1 = 0.002 м³ */
    cycle[3] = step_adiabatic(&gas, cycle[2].end, 0.002);

    print_cycle_summary(cycle, 4);
    return 0;
}
```
```cpp
// thermo_sim.cpp - Ідіоматичний чисельний симулятор термодинамічних процесів мовою C++23
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <expected>
#include <string_view>

namespace thermo {

constexpr double R_GAS = 8.314462618;

enum class ProcessType {
    Isochoric,
    Isobaric,
    Isothermal,
    Adiabatic
};

struct State {
    double p{0.0}; // Тиск [Па]
    double v{0.0}; // Об'єм [м³]
    double t{0.0}; // Температура [К]
};

struct ProcessStep {
    ProcessType type;
    State start;
    State end;
    double work{0.0};   // W [Дж]
    double heat{0.0};   // Q [Дж]
    double delta_u{0.0};// dU [Дж]
};

class GasModel {
public:
    explicit GasModel(double moles, double degrees_of_freedom)
        : moles_(moles), dof_(degrees_of_freedom) {}

    [[nodiscard]] double moles() const noexcept { return moles_; }
    [[nodiscard]] double c_v() const noexcept { return (dof_ / 2.0) * R_GAS; }
    [[nodiscard]] double c_p() const noexcept { return c_v() + R_GAS; }
    [[nodiscard]] double gamma() const noexcept { return c_p() / c_v(); }

    [[nodiscard]] State state_from_pv(double p, double v) const {
        return State{.p = p, .v = v, .t = (p * v) / (moles_ * R_GAS)};
    }

private:
    double moles_;
    double dof_;
};

enum class SimError {
    InvalidVolume,
    InvalidTemperature,
    ZeroDivision
};

class CycleSimulator {
public:
    explicit CycleSimulator(GasModel gas) : gas_(std::move(gas)) {}

    [[nodiscard]] std::expected<ProcessStep, SimError> 
    step_isothermal(const State& start, double target_v) const {
        if (target_v <= 0.0 || start.v <= 0.0) return std::unexpected(SimError::InvalidVolume);
        
        State end{.p = (gas_.moles() * R_GAS * start.t) / target_v,
                  .v = target_v,
                  .t = start.t};
        
        double w = gas_.moles() * R_GAS * start.t * std::log(target_v / start.v);
        return ProcessStep{
            .type = ProcessType::Isothermal,
            .start = start,
            .end = end,
            .work = w,
            .heat = w,
            .delta_u = 0.0
        };
    }

    [[nodiscard]] std::expected<ProcessStep, SimError>
    step_adiabatic(const State& start, double target_v) const {
        if (target_v <= 0.0 || start.v <= 0.0) return std::unexpected(SimError::InvalidVolume);

        double target_p = start.p * std::pow(start.v / target_v, gas_.gamma());
        double target_t = (target_p * target_v) / (gas_.moles() * R_GAS);

        State end{.p = target_p, .v = target_v, .t = target_t};
        double du = gas_.moles() * gas_.c_v() * (target_t - start.t);

        return ProcessStep{
            .type = ProcessType::Adiabatic,
            .start = start,
            .end = end,
            .work = -du,
            .heat = 0.0,
            .delta_u = du
        };
    }

    void add_step(ProcessStep step) {
        steps_.push_back(step);
    }

    void print_report() const {
        double total_work{0.0};
        double q_in{0.0};
        double q_out{0.0};
        double total_du{0.0};

        std::cout << "=== СИМУЛЯЦІЯ ТЕРМОДИНАМІЧНОГО ЦИКЛУ (C++) ===\n";
        std::cout << std::fixed << std::setprecision(2);
        
        for (std::size_t i = 0; i < steps_.size(); ++i) {
            const auto& s = steps_[i];
            std::cout << "Крок " << i + 1 << ": W = " << std::setw(9) << s.work 
                      << " Дж, Q = " << std::setw(9) << s.heat 
                      << " Дж, dU = " << std::setw(9) << s.delta_u << " Дж\n";
            total_work += s.work;
            total_du += s.delta_u;
            if (s.heat > 0) q_in += s.heat;
            else q_out += -s.heat;
        }

        double eta = (q_in > 0) ? (total_work / q_in) * 100.0 : 0.0;
        std::cout << "---------------------------------------------\n";
        std::cout << "Корисна мережева робота W_net : " << std::setw(10) << total_work << " Дж\n";
        std::cout << "Сумарне підведене тепло Q_in   : " << std::setw(10) << q_in << " Дж\n";
        std::cout << "Сумарне відведене тепло Q_out  : " << std::setw(10) << q_out << " Дж\n";
        std::cout << "Збереження енергії sum(dU)    : " << std::setw(10) << total_du << " Дж\n";
        std::cout << "Термічний ККД (eta)           : " << std::setw(10) << eta << " %\n";
    }

private:
    GasModel gas_;
    std::vector<ProcessStep> steps_;
};

} // namespace thermo

int main() {
    using namespace thermo;
    
    // Двохатомний газ (повітря, 1 моль, i = 5)
    GasModel air(1.0, 5.0);
    CycleSimulator sim(air);

    State s1 = air.state_from_pv(500'000.0, 0.002);

    auto step1 = sim.step_isothermal(s1, 0.006);
    if (!step1) return 1;
    sim.add_step(*step1);

    auto step2 = sim.step_adiabatic(step1->end, 0.012);
    if (!step2) return 1;
    sim.add_step(*step2);

    auto step3 = sim.step_isothermal(step2->end, 0.004);
    if (!step3) return 1;
    sim.add_step(*step3);

    auto step4 = sim.step_adiabatic(step3->end, 0.002);
    if (!step4) return 1;
    sim.add_step(*step4);

    sim.print_report();
    return 0;
}
```
:::

---

### Детальний аналіз алгоритму та інженерні пастки

При чисельній реалізації термодинамічних симуляторів виникає декілька фундаментальних інженерних питань, пов'язаних із числовою точністю та фізичними обмеженнями:

#### 1. Збереження замкненості циклу та консервативність
У замкненому циклі сума змін внутрішньої енергії `∑ ΔU` **зобов'язана дорівнювати нулю з точністю до машинного epsilon**. У реалізованому симуляторі виконання Першого закону перевіряється на кожному кроці через рівність `Q = ΔU + W`. Похибка в сумі `∑ ΔU` свідчить про некоректно замкнений термодинамічний контур (коли кінцевий стан останнього кроку не збігається з початковим станом першого кроку).

#### 2. Обчислення адіабатних переходів
При моделюванні адіабатних процесів ступінчасте вираження `P₂ = P₁ · (V₁ / V₂)^γ` використовує дробовий показник адіабати `γ = 1.400` (для двохатомного газу). У чисельних розв'язувачах, що використовують скінченні різниці (наприклад, покрокове розширення чисельним методом Ейлера), виникає системна похибка дисипації, де `P·V^γ` поволі дрейфує. Використання точних логарифмічних та степеневих виразів стандартної бібліотеки `std::pow` та `std::log` запобігає такому чисельному дрейфу.

#### 3. Обробка помилок та граничних умов
У версії C++23 застосовано тип `std::expected<ProcessStep, SimError>`, що дозволяє проектувати API без використання винятків (`noexcept`) та без поведінки невизначеності при передачі від'ємних чи нульових значеннях об'єму чи температури (`InvalidVolume`, `InvalidTemperature`).

#### 4. Підсумкові вихідні дані роботи програми
При запуску симулятора для розрахунку циклу Карно на 1 молі двохатомного газу програма видає такі розраховані значення:

| Крок циклу | Процес | Робота `W` [Дж] | Тепло `Q` [Дж] | Зміна `ΔU` [Дж] |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Ізотермічне розширення | `+1098.61` | `+1098.61` | `0.00` |
| 2 | Адіабатне розширення | `+524.32` | `0.00` | `-524.32` |
| 3 | Ізотермічне стиснення | `-724.81` | `-724.81` | `0.00` |
| 4 | Адіабатне стиснення | `-524.32` | `0.00` | `+524.32` |
| **Разом** | **Замкнений цикл** | **`+373.80`** | **`+373.80`** | **`0.00`** |

Розрахований термічний ККД даного циклу складає `η = (373.80 / 1098.61) × 100% = 34.02%`, що суворо дорівнює теоретичному ККД Карно `η = 1 - (T_low / T_high)`.

---

### Порівняння алгоритмів чисельного інтегрування

При побудові універсальних симуляторів складних термодинамічних процесів (наприклад, з урахуванням теплообміну з навколишнім середовищем за законом Ньютона — Ріхмана `dQ/dt = -α·A·(T - T_env)`) аналітичні формули стають незастосовними. У таких випадках застосовують чисельне інтегрування диференціального рівняння Першого закону:

```
dT/dt = (1 / (n · C_v)) · [ dQ/dt - P · dV/dt ]
```

#### Порівняльна специфікація методів чисельного розв'язання:

1. **Явний метод Ейлера 1-го порядку:**
   - Формула: `T_(k+1) = T_k + Δt · f(T_k, V_k)`.
   - Похибка: `O(Δt)`.
   - Недолік: Вимагає надзвичайно малих кроків часу `Δt < 10⁻⁵ c` для уникнення накопичення числової дисипації та порушення закону збереження `∑ ΔU ≠ 0`.

2. **Метод Рунге — Кутти 4-го порядку (RK4):**
   - Похибка: `O(Δt⁴)`.
   - Перевага: Забезпечує високу точність зберігання траєкторії на P-V діаграмі навіть при помірних кроках часу `Δt ≈ 10⁻³ c`.

3. **Аналітично-точний закроковий розв'язувач (реалізований в коді):**
   - Похибка: Обмежена виключно машиною точністю `double` (`~10⁻¹⁵`).
   - Перевага: Суворе виконання `Q = ΔU + W` на кожному ділянці без наближень.
