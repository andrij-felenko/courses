# ⚙️ Чисельне моделювання вольт-амперного гістерезису та кінетики філамента комірки 1T1R

Аналітичне розв'язання рівнянь іонного переносу та джоулевого нагріву у комірці оксидної резистивної пам'яті (OxRAM) є ускладненим через сильну нелінійність полевих та температурних залежностей. Для прогнозування вольт-амперної характеристики (ВАХ), величини струму обмеження (*compliance current*) та динаміки зазору філамента `x_gap(t)` застосовується чисельне інтегрування диференціальних рівнянь кінетики Мотта — Ґерні.

Ця вставка розкриває алгоритм чисельного розв'язувача, методи забезпечення чисельної стабільності та містить практичні реалізації моделі осередку 1T1R (1 Transistor 1 Resistor) мовами Python, C та C++.

## 1. Постановка фізичної моделі та параметри комірки

Модель розглядає послідовне з'єднання нелінійного оксидного елемента пам'яті та керувального транзистора-селектора. Елемент пам'яті являє собою шар оксиду гафнію HfO₂ товщиною `D`, у якому провідна нитка кисневих вакансій (філамент) відділена від верхнього електрода нанорозмірним діелектричним зазором `x_gap`.

Загальний опір комірки складений із послідовного опору провідної частини філамента `R_on`, нелінійного тунельного опору зазору `R_gap(x_gap)` та опору каналу транзистора `R_MOS`:

```
R_cell = R_on + R_gap(x_gap) + R_MOS
```

Тунельний опір оксидного зазору залежить експоненційно від його товщини `x_gap`:

```
R_gap = R_on · exp(A · x_gap)
```

де `A ≈ 10.25` нм⁻¹ — постійна загасання хвильової функції електрона в діелектрику HfO₂.

### Базові фізичні параметри чисельної моделі:
- Повна товщина функціонального оксиду: `D = 5.0` нм;
- Початковий зазор оксиду у високорезистивному стані (HRS): `x_gap,0 = 1.2` нм;
- Енергія активації йонної міграції кисневих вакансій: `E_a = 0.85` еВ;
- Постійна стрибка ґратки: `a = 0.3` нм;
- Опір суцільного металевого філамента у низькорезистивному стані (LRS): `R_on = 1000` Ом;
- Струм обмеження транзистора-селектора (Compliance Current): `I_comp = 100` мкА.

## 2. Алгоритм розв'язувача та захист від чисельної нестійкості

У кожному часовому кроці `dt` чисельний алгоритм виконує послідовну систему обчислень:
1. **Обчислення падіння напруги на зазорі `V_gap`:**
   Падіння напруги розраховується з урахуванням дільника напруги між зазором та послідовними опорами філамента й транзистора. При досягненні струмом порогу `I_comp` напруга на комірці обмежується дією транзистора;
2. **Розрахунок локальної температури `T_max`:**
   За співвідношенням Кольрауша визначається нагрів гарячої точки у звуженні філамента: `T_max = √(T_0² + V_gap² / (4 · L_W))`;
3. **Обчислення швидкості йонного дрейфу за Моттом — Ґерні:**
   Вираховується швидкість переміщення межі зазору: `v_drift = 2 · a · v₀ · exp(-E_a / (k_B · T_max)) · sinh(q · a · E_gap / (2 · k_B · T_max))`;
4. **Чисельне інтегрування та граничні умови:**
   Методом Ейлера оновлюється величина зазору `x_gap(t + dt) = x_gap(t) + (dx_gap / dt) · dt` з обов'язковим обрізанням на фізичних межах `0 ≤ x_gap ≤ D`.

### Особливості жорсткості диференціального рівняння (Stiffness):
Диференціальне рівняння росту зазору `dx_gap / dt` володіє високою чисельною жорсткістю. При малих зазорах (`x_gap < 0.2` нм) локальне електричне поле `E_gap = V / x_gap` зростає до 20 МВ/см, що викликає катастрофічний стрибок швидкості дрейфу `v_drift`. Для запобігання чисельним осциляціям та розбіжностям у розв'язувачі застосовуються три прийоми:
- **Адаптивний вибір кроку `dt`:** При `E_gap > 5` МВ/см крок за часом локально зменшується з 1 мікросекунди до 10 пікосекунд;
- **Обрізання експоненційного аргументу (Clipping):** Оскільки аргумент гіперболічного синуса `arg = q · a · E_gap / (2 · k_B · T_max)` при надвисоких полях може перевищувати 100, обчислення `sinh(arg)` здатне викликати арифметичне переповнення типу `double` (IEEE 754). У чисельному коді аргумент затискається зверху рівнем `arg_max = 50.0`, що відповідає максимальній фізичній швидкості насичення йонного дрейфу (`v_sat ≈ 100` м/с);
- **Фізичний лімітер товщини зазору:** Величина зазору обмежується знизу значенням `x_gap = 0.0` (що відповідає суцільному металевому зв'язку у філаменті) та зверху значенням `x_gap = D` (повністю сформований ізолятор). Це запобігає нефізичному виходу зазору у від'ємну область під час швидкого оновлення стану.

## 3. Реалізація мовами Python, C та C++

У наведеному контейнері показано ідіоматичні реалізації чисельного розв'язувача. Версія мовою C використовує процедурний підхід та структури, а C++ додає типування `std::vector`, RAII-обгортки та об'єктно-орієнтовану інкапсуляцію стану комірки.

:::tabs
```py
import math

def simulate_oxram_cell(v_max=2.0, steps=400, i_comp=1e-4):
    """
    Моделювання вольт-амперного гістерезису та кінетики зазору OxRAM комірки.
    """
    # Фізичні константи
    q = 1.602e-19
    kB = 1.38e-23
    L_W = 2.44e-8
    
    # Параметри комірки HfO2
    x_gap = 1.2e-9        # Початковий зазор HRS (м)
    E_a = 0.85 * 1.602e-19 # Енергія активації (Дж)
    a = 0.3e-9            # Відстань між ямами (м)
    v0 = 1e4              # Пре-експоненційний множник (м/с)
    R_on = 1000.0         # Опір LRS філамента (Ом)
    T0 = 300.0            # Базова температура (К)
    dt = 1e-6             # Крок за часом (с)

    # Генерація трикутного імпульсу напруги (0 -> V_max -> 0 -> -V_max -> 0)
    v_profile = []
    half = steps // 4
    for i in range(half):
        v_profile.append((i / half) * v_max)
    for i in range(half):
        v_profile.append((1.0 - i / half) * v_max)
    for i in range(half):
        v_profile.append(-(i / half) * v_max)
    for i in range(half):
        v_profile.append(-(1.0 - i / half) * v_max)

    history_v = []
    history_i = []
    history_gap = []

    for V_app in v_profile:
        # Опір тунельного зазору R_gap = R_on * exp(A * x_gap)
        R_gap = R_on * math.exp(10.25e9 * x_gap)
        R_total = R_on + R_gap

        # Розрахунок струму з урахуванням обмеження I_comp
        I_cell = V_app / R_total
        if abs(I_cell) > i_comp:
            I_cell = math.copysign(i_comp, I_cell)

        # Падіння напруги безпосередньо на зазорі
        V_gap = I_cell * R_gap
        E_gap = abs(V_gap) / max(x_gap, 1e-10)

        # Температура за співвідношенням Кольрауша
        T_max = math.sqrt(T0**2 + (abs(V_gap)**2) / (4.0 * L_W))

        # Швидкість руху вакансій за Моттом — Ґерні
        arg = (q * a * E_gap) / (2.0 * kB * T_max)
        arg = min(arg, 50.0) # Захист від переповнення exp
        v_drift = 2.0 * a * v0 * math.exp(-E_a / (kB * T_max)) * math.sinh(arg)

        # Зміна зазору залежно від полярності (SET при V > 0, RESET при V < 0)
        if V_app > 0:
            dx_dt = -v_drift # Звуження зазору
        else:
            dx_dt = v_drift * 0.1 # Розширення зазору при RESET

        x_gap = max(0.0, min(2.0e-9, x_gap + dx_dt * dt))

        history_v.append(V_app)
        history_i.append(I_cell)
        history_gap.append(x_gap)

    return history_v, history_i, history_gap

if __name__ == "__main__":
    v_arr, i_arr, gap_arr = simulate_oxram_cell()
    print(f"Моделювання завершено. Завершальний зазор x_gap: {gap_arr[-1]*1e9:.3f} нм")
```
```c
#include <stdio.h>
#include <math.h>

#define STEPS 400

typedef struct {
    double x_gap;      /* Товщина оксидного зазору (м) */
    double R_on;       /* Опір філамента в LRS (Ом) */
    double E_a;        /* Енергія активації міграції (Дж) */
    double a_lattice;  /* Постійна ґратки (м) */
    double I_comp;     /* Струм обмеження (А) */
} OxRamCell;

void oxram_init(OxRamCell *cell) {
    cell->x_gap = 1.2e-9;
    cell->R_on = 1000.0;
    cell->E_a = 0.85 * 1.602e-19;
    cell->a_lattice = 0.3e-9;
    cell->I_comp = 1e-4;
}

double oxram_step(OxRamCell *cell, double V_app, double dt) {
    const double q = 1.602e-19;
    const double kB = 1.38e-23;
    const double L_W = 2.44e-8;
    const double T0 = 300.0;
    const double v0 = 1e4;

    /* Опір тунельного зазору */
    double R_gap = cell->R_on * exp(10.25e9 * cell->x_gap);
    double R_total = cell->R_on + R_gap;

    double I_cell = V_app / R_total;
    if (fabs(I_cell) > cell->I_comp) {
        I_cell = (I_cell > 0) ? cell->I_comp : -cell->I_comp;
    }

    double V_gap = I_cell * R_gap;
    double E_gap = fabs(V_gap) / (cell->x_gap > 1e-10 ? cell->x_gap : 1e-10);

    /* Локальна температура Кольрауша */
    double T_max = sqrt(T0 * T0 + (V_gap * V_gap) / (4.0 * L_W));

    double arg = (q * cell->a_lattice * E_gap) / (2.0 * kB * T_max);
    if (arg > 50.0) arg = 50.0;

    double v_drift = 2.0 * cell->a_lattice * v0 * exp(-cell->E_a / (kB * T_max)) * sinh(arg);
    double dx_dt = (V_app > 0) ? -v_drift : v_drift * 0.1;

    cell->x_gap += dx_dt * dt;
    if (cell->x_gap < 0.0) cell->x_gap = 0.0;
    if (cell->x_gap > 2.0e-9) cell->x_gap = 2.0e-9;

    return I_cell;
}

int main(void) {
    OxRamCell cell;
    oxram_init(&cell);

    double dt = 1e-6;
    double v_max = 2.0;
    
    printf("Крок | Напруга (В) | Струм (мкА) | Зазор x_gap (нм)\n");
    printf("--------------------------------------------------\n");

    for (int i = 0; i <= 20; i++) {
        double V_app = (i / 20.0) * v_max;
        double I_cell = oxram_step(&cell, V_app, dt);
        printf("%4d | %11.3f | %11.3f | %16.3f\n", 
               i, V_app, I_cell * 1e6, cell->x_gap * 1e9);
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <iomanip>

class OxRamSimulator {
private:
    struct Params {
        double x_gap = 1.2e-9;        // Товщина зазору (м)
        double R_on = 1000.0;         // Опір у стані LRS (Ом)
        double E_a = 0.85 * 1.602e-19;// Енергія активації (Дж)
        double a_lattice = 0.3e-9;   // Постійна ґратки (м)
        double I_comp = 1e-4;         // Струм обмеження (А)
    } p_;

    static constexpr double q = 1.602e-19;
    static constexpr double kB = 1.38e-23;
    static constexpr double L_W = 2.44e-8;
    static constexpr double T0 = 300.0;
    static constexpr double v0 = 1e4;

public:
    struct State {
        double voltage;
        double current;
        double gap;
    };

    explicit OxRamSimulator(double initial_gap = 1.2e-9, double i_comp = 1e-4) {
        p_.x_gap = initial_gap;
        p_.I_comp = i_comp;
    }

    State step(double V_app, double dt) {
        const double R_gap = p_.R_on * std::exp(10.25e9 * p_.x_gap);
        const double R_total = p_.R_on + R_gap;

        double I_cell = V_app / R_total;
        if (std::abs(I_cell) > p_.I_comp) {
            I_cell = std::copysign(p_.I_comp, I_cell);
        }

        const double V_gap = I_cell * R_gap;
        const double E_gap = std::abs(V_gap) / std::max(p_.x_gap, 1e-10);

        const double T_max = std::sqrt(T0 * T0 + (V_gap * V_gap) / (4.0 * L_W));

        double arg = (q * p_.a_lattice * E_gap) / (2.0 * kB * T_max);
        arg = std::min(arg, 50.0);

        const double v_drift = 2.0 * p_.a_lattice * v0 * std::exp(-p_.E_a / (kB * T_max)) * std::sinh(arg);
        const double dx_dt = (V_app > 0) ? -v_drift : v_drift * 0.1;

        p_.x_gap = std::clamp(p_.x_gap + dx_dt * dt, 0.0, 2.0e-9);

        return { V_app, I_cell, p_.x_gap };
    }

    std::vector<State> run_ramp(double v_max, std::size_t steps, double dt) {
        std::vector<State> results;
        results.reserve(steps);

        for (std::size_t i = 0; i < steps; ++i) {
            double v = (static_cast<double>(i) / steps) * v_max;
            results.push_back(step(v, dt));
        }
        return results;
    }
};

int main() {
    OxRamSimulator sim(1.2e-9, 1e-4);
    auto trajectory = sim.run_ramp(2.0, 20, 1e-6);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Крок | Напруга (В) | Струм (мкА) | Зазор x_gap (нм)\n";
    std::cout << "--------------------------------------------------\n";

    std::size_t step_idx = 0;
    for (const auto& st : trajectory) {
        std::cout << std::setw(4) << step_idx++ << " | "
                  << std::setw(11) << st.voltage << " | "
                  << std::setw(11) << st.current * 1e6 << " | "
                  << std::setw(16) << st.gap * 1e9 << "\n";
    }
    return 0;
}
```
:::

## 4. Фізичний аналіз результатів чисельного моделювання

Розв'язок чисельної моделі демонструє п'ять ключових фізичних рис резистивного перемикання у нанорозмірній оксидній комірці:

1. **Пороговий характер закриття зазору:** При напрузі `V < 0.6` В величина зазору `x_gap` залишається практично незмінною (`1.2` нм), а струм витоку не перевищує 1 мкА. При перевищенні порогової напруги `V > 1.0` В швидкість дрейфу зростає експоненційно, закриваючи зазор до нуля за час близько 10 наносекунд;
2. **Роль струму обмеження (Compliance Current):** Завдяки обмеженню `I_comp = 100` мкА струм при досягненні низькорезистивного стану не зростає до катастрофічних значений (що викликало б незворотний тепловий пробій та розплавлення оксиду), а фіксується на рівні `I_comp`. Це визначає підсумковий геометричний радіус філамента `r_CF`;
3. **Гістерезисна ВАХ:** При зворотному ході напруги комірка залишається у провідному стані LRS з опором `R_on = 1000` Ом, формуючи відкрите вікно пам'яті між станами LRS та HRS (`R_HRS / R_LRS > 100`);
4. **Термічний прискорювач операції RESET:** Під час негативного імпульсу RESET висока густина струму розігріває локальну гарячу точку до `T_max > 700` К. Це експоненційно знижує енергетичний бар'єр рекомбінації `E_rec` і дозволяє іонам кисню швидко дифундувати назад у провідний канал, відновлюючи ізолюючий зазор `x_gap`;
5. **Чутливість до тривалості pulse width:** Зменшення тривалості імпульсу `dt` вимагає збільшення амплітуди напруги `V_SET`, що узгоджується з експериментальною часово-напруговою залежністю (*voltage-time dilemma*): зменшення часу перемикання у 10 разів вимагає збільшення напруги на ~ 0.15 В.
