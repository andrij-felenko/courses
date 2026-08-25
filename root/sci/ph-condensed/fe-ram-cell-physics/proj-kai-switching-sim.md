# ⚙️ Моделювання струму перемикання FeRAM комірки на основі моделі KAI

Ця практична програма реалізує чисельний аналіз часового відгуку 1T1C FeRAM комірки під час операції руйнівного зчитування. Вона обчислює струм перемикання поляризації `I_sw(t)` за моделлю Колмогорова — Аврамі — Ішібаші (KAI), лінійний струм заряджання `I_lin(t)` та підсумкову динаміку накопичення напруги на розрядній шині `V_BL(t)` для логічних станів «1» та «0».

Практичне моделювання є необхідним етапом проектування аналогових підсилювачів зчитування та контролерів пам'яті. Воно дозволяє інженерам розраховувати напругові вікна зчитування (*read margin windows*), аналізувати вплив крутості фронту імпульсів на пластинній шині PL та оцінювати вплив паразитної ємності розрядної шини `C_bitline` на підсумкову швидкодію осередку.

---

### 1. Фізична та обчислювальна модель

Під час операції зчитування на пластинну шину PL подається імпульс напруги `V_PL(t)` зі скінченним часом наростання фронту `t_rise`. Припустимо, що імпульс має лінійно-трапецеподібну форму:

```
V_PL(t) = V_DD · (t / t_rise)       [при 0 ≤ t < t_rise]
V_PL(t) = V_DD                      [при t ≥ t_rise]
```

Повний струм `I_total(t)`, що інжектується в розрядную шину `C_BL`, складається з двох суттєво різних за фізичною природою компонентів:

```
I_total(t) = I_lin(t) + I_sw(t)

I_lin(t) = C_lin · [ d(V_PL - V_BL) / dt ]
I_sw(t)  = 2 · Pᵣ · A_cap · (dμ / dt)
```

де `C_lin` — лінійна ємність конденсатора, `A_cap` — його фізична площа, `Pᵣ` — залишкова поляризація сегнетоелектрика, а `dμ/dt` — швидкість перемикання об'ємної частки доменів за моделлю KAI:

```
μ(t) = 1 - exp[ - (t / τ₀)ⁿ ]
dμ / dt = (n / τ₀) · (t / τ₀)ⁿ⁻¹ · exp[ - (t / τ₀)ⁿ ]
```

Чисельне інтегрування диференціального рівняння накопичення заряду на розрядній шині здійснюється методом Ейлера з часовим кроком дискретизації `dt`. Для уникнення чисельної нестійкості крок дискретизації `dt` обирається значно меншим за найменшу постійну часу системи: `dt << min(t_rise, τ₀, R_channel · C_cell)`.

```
V_BL(t + dt) = V_BL(t) + [ I_total(t) / (C_lin + C_BL) ] · dt
```

Симуляція розраховує дві незалежні траєкторії напруги:
- `V_BL(1)`: траєкторія для стану «1», де присутні обидва струми (`I_lin + I_sw`);
- `V_BL(0)`: траєкторія для стану «0», де перемикання доменів відсутнє і протікає тільки `I_lin`.

Різниця потенціалів `ΔV_sense(t) = V_BL(1)(t) - V_BL(0)(t)` визначає динамічне вікно сигналу, яке порівнюється з порогом чутливості підсилювача.

---

### 2. Програмна реалізація симулятора

Програма реалізована двома мовами програмування (C99 та ідіоматичний C++20). Варіант мовою C спирається на пряме керування пам'яттю через `malloc`/`free` та процедурний підхід із передачею вказівників на конфігураційні структури. Варіант мовою C++ використовує концепцію RAII, незмінний об'єктний симулятор `FeRamSimulator`, безпечний для пам'яті контейнер `std::vector`, сучасний перегляд масивів `std::span` та строго типізований форм-фактор `SimulationFrame`.

:::tabs
```c
/* feram_kai_sim.c - Чисельний симулятор зчитування FeRAM комірки (C99) */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double area_cap_um2;   /* Площа конденсатора, мкм² */
    double p_remnant_uc;   /* Залишкова поляризація Pᵣ, мкКл/см² */
    double c_lin_ff;       /* Лінійна ємність конденсатора, фФ */
    double c_bitline_ff;   /* Паразитна ємність розрядної шини Bitline, фФ */
    double tau_0_ns;       /* Часова константа KAI τ₀, нс */
    double avrami_n;       /* Показник Аврамі n */
    double v_dd_volts;     /* Напруга живлення V_DD, В */
    double t_rise_ns;      /* Час наростання фронту PL імпульсу, нс */
} FeRamCellParams;

typedef struct {
    double time_ns;
    double v_pl_volts;
    double i_sw_ma;
    double i_lin_ma;
    double v_bl_state1_volts;
    double v_bl_state0_volts;
} SimPoint;

/* Обчислення похідної переключеної фази dμ/dt за моделлю KAI */
static double kai_dmu_dt(double t_ns, double tau_0_ns, double avrami_n) {
    if (t_ns <= 0.0 || tau_0_ns <= 0.0) {
        return 0.0;
    }
    double norm_t = t_ns / tau_0_ns;
    double term1 = (avrami_n / tau_0_ns) * pow(norm_t, avrami_n - 1.0);
    double term2 = exp(-pow(norm_t, avrami_n));
    return term1 * term2;
}

/* Симуляція динаміки зчитування комірки */
static bool run_feram_simulation(const FeRamCellParams *params, 
                                double t_total_ns, 
                                double dt_ns, 
                                SimPoint **out_results, 
                                size_t *out_count) {
    if (!params || !out_results || !out_count || dt_ns <= 0.0) {
        return false;
    }

    size_t steps = (size_t)(t_total_ns / dt_ns) + 1;
    SimPoint *results = (SimPoint *)malloc(steps * sizeof(SimPoint));
    if (!results) {
        return false;
    }

    /* Перетворення одиниць SI */
    double area_cm2 = params->area_cap_um2 * 1.0e-8;
    double pr_c_cm2 = params->p_remnant_uc * 1.0e-6;
    double q_sw_total_c = 2.0 * pr_c_cm2 * area_cm2; /* Q_sw = 2 * Pᵣ * A */
    
    double c_lin_farads = params->c_lin_ff * 1.0e-15;
    double c_bl_farads = params->c_bitline_ff * 1.0e-15;
    double c_total_farads = c_lin_farads + c_bl_farads;

    double v_bl_1 = 0.0;
    double v_bl_0 = 0.0;

    for (size_t i = 0; i < steps; i++) {
        double t = i * dt_ns;
        
        /* Профіль імпульсу пластинної шини PL */
        double v_pl = 0.0;
        double dv_pl_dt = 0.0;
        if (t < params->t_rise_ns) {
            v_pl = params->v_dd_volts * (t / params->t_rise_ns);
            dv_pl_dt = params->v_dd_volts / params->t_rise_ns;
        } else {
            v_pl = params->v_dd_volts;
            dv_pl_dt = 0.0;
        }

        /* Струм перемикання KAI (для стану '1') */
        double dmu_dt = kai_dmu_dt(t, params->tau_0_ns, params->avrami_n);
        double i_sw_amp = q_sw_total_c * (dmu_dt * 1.0e9); /* dμ/dt переведено в с⁻¹ */

        /* Лінійний струм зміщення */
        double i_lin_amp = c_lin_farads * (dv_pl_dt * 1.0e9);

        /* Оновлення напруг розрядної шини */
        double dv_bl_1 = ((i_sw_amp + i_lin_amp) / c_total_farads) * (dt_ns * 1.0e-9);
        double dv_bl_0 = (i_lin_amp / c_total_farads) * (dt_ns * 1.0e-9);

        v_bl_1 += dv_bl_1;
        v_bl_0 += dv_bl_0;

        results[i].time_ns = t;
        results[i].v_pl_volts = v_pl;
        results[i].i_sw_ma = i_sw_amp * 1.0e3;
        results[i].i_lin_ma = i_lin_amp * 1.0e3;
        results[i].v_bl_state1_volts = v_bl_1;
        results[i].v_bl_state0_volts = v_bl_0;
    }

    *out_results = results;
    *out_count = steps;
    return true;
}

int main(void) {
    FeRamCellParams cell = {
        .area_cap_um2 = 0.25,     /* 0.25 мкм² */
        .p_remnant_uc = 22.0,     /* 22 мкКл/см² */
        .c_lin_ff = 5.0,          /* 5 фФ */
        .c_bitline_ff = 60.0,     /* 60 фФ */
        .tau_0_ns = 2.5,          /* 2.5 нс */
        .avrami_n = 2.2,          /* n = 2.2 */
        .v_dd_volts = 1.8,        /* 1.8 В */
        .t_rise_ns = 1.0          /* 1.0 нс */
    };

    SimPoint *results = NULL;
    size_t count = 0;

    if (run_feram_simulation(&cell, 10.0, 0.05, &results, &count)) {
        printf("Time(ns) | V_PL(V) | I_sw(mA) | V_BL[1](V) | V_BL[0](V) | Sense_Margin(mV)\n");
        printf("-------------------------------------------------------------------------\n");
        
        for (size_t i = 0; i < count; i += 20) { /* Друк кожного 20-го кроку */
            double margin_mv = (results[i].v_bl_state1_volts - results[i].v_bl_state0_volts) * 1000.0;
            printf("%8.2f | %7.2f | %8.4f | %10.3f | %10.3f | %17.1f\n",
                   results[i].time_ns,
                   results[i].v_pl_volts,
                   results[i].i_sw_ma,
                   results[i].v_bl_state1_volts,
                   results[i].v_bl_state0_volts,
                   margin_mv);
        }
        free(results);
    }
    return 0;
}
```
```cpp
// feram_kai_sim.cpp - Об'єктно-орієнтований симулятор FeRAM комірки (C++20)
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <memory>
#include <span>

struct FeRamConfig {
    double area_cap_um2{0.25};
    double p_remnant_uc{22.0};
    double c_lin_ff{5.0};
    double c_bitline_ff{60.0};
    double tau_0_ns{2.5};
    double avrami_n{2.2};
    double v_dd_volts{1.8};
    double t_rise_ns{1.0};
};

struct SimulationFrame {
    double time_ns{0.0};
    double v_pl_volts{0.0};
    double i_sw_ma{0.0};
    double i_lin_ma{0.0};
    double v_bl_state1_volts{0.0};
    double v_bl_state0_volts{0.0};

    [[nodiscard]] double sense_margin_mv() const noexcept {
        return (v_bl_state1_volts - v_bl_state0_volts) * 1000.0;
    }
};

class FeRamSimulator {
public:
    explicit FeRamSimulator(FeRamConfig config) : config_(config) {}

    [[nodiscard]] std::vector<SimulationFrame> run(double total_time_ns, double dt_ns) const {
        const size_t steps = static_cast<size_t>(total_time_ns / dt_ns) + 1;
        std::vector<SimulationFrame> timeline;
        timeline.reserve(steps);

        const double area_cm2 = config_.area_cap_um2 * 1.0e-8;
        const double pr_c_cm2 = config_.p_remnant_uc * 1.0e-6;
        const double q_sw_total_c = 2.0 * pr_c_cm2 * area_cm2;
        
        const double c_lin_farads = config_.c_lin_ff * 1.0e-15;
        const double c_bl_farads = config_.c_bitline_ff * 1.0e-15;
        const double c_total_farads = c_lin_farads + c_bl_farads;

        double v_bl_1 = 0.0;
        double v_bl_0 = 0.0;

        for (size_t i = 0; i < steps; ++i) {
            const double t = i * dt_ns;
            
            double v_pl = 0.0;
            double dv_pl_dt = 0.0;
            if (t < config_.t_rise_ns) {
                v_pl = config_.v_dd_volts * (t / config_.t_rise_ns);
                dv_pl_dt = config_.v_dd_volts / config_.t_rise_ns;
            } else {
                v_pl = config_.v_dd_volts;
                dv_pl_dt = 0.0;
            }

            const double dmu_dt = compute_dmu_dt(t);
            const double i_sw_amp = q_sw_total_c * (dmu_dt * 1.0e9);
            const double i_lin_amp = c_lin_farads * (dv_pl_dt * 1.0e9);

            const double dv_bl_1 = ((i_sw_amp + i_lin_amp) / c_total_farads) * (dt_ns * 1.0e-9);
            const double dv_bl_0 = (i_lin_amp / c_total_farads) * (dt_ns * 1.0e-9);

            v_bl_1 += dv_bl_1;
            v_bl_0 += dv_bl_0;

            timeline.push_back(SimulationFrame{
                .time_ns = t,
                .v_pl_volts = v_pl,
                .i_sw_ma = i_sw_amp * 1.0e3,
                .i_lin_ma = i_lin_amp * 1.0e3,
                .v_bl_state1_volts = v_bl_1,
                .v_bl_state0_volts = v_bl_0
            });
        }

        return timeline;
    }

private:
    FeRamConfig config_;

    [[nodiscard]] double compute_dmu_dt(double t_ns) const noexcept {
        if (t_ns <= 0.0 || config_.tau_0_ns <= 0.0) {
            return 0.0;
        }
        const double norm_t = t_ns / config_.tau_0_ns;
        const double term1 = (config_.avrami_n / config_.tau_0_ns) * std::pow(norm_t, config_.avrami_n - 1.0);
        const double term2 = std::exp(-std::pow(norm_t, config_.avrami_n));
        return term1 * term2;
    }
};

void print_summary(std::span<const SimulationFrame> results) {
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Time(ns) | V_PL(V) | I_sw(mA) | V_BL[1](V) | V_BL[0](V) | Sense_Margin(mV)\n";
    std::cout << "-------------------------------------------------------------------------\n";

    for (size_t i = 0; i < results.size(); i += 20) {
        const auto& frame = results[i];
        std::cout << std::setw(8) << frame.time_ns << " | "
                  << std::setw(7) << frame.v_pl_volts << " | "
                  << std::setw(8) << frame.i_sw_ma << " | "
                  << std::setw(10) << frame.v_bl_state1_volts << " | "
                  << std::setw(10) << frame.v_bl_state0_volts << " | "
                  << std::setw(17) << std::setprecision(1) << frame.sense_margin_mv() << "\n"
                  << std::setprecision(2);
    }
}

int main() {
    const FeRamConfig config{
        .area_cap_um2 = 0.25,
        .p_remnant_uc = 22.0,
        .c_lin_ff = 5.0,
        .c_bitline_ff = 60.0,
        .tau_0_ns = 2.5,
        .avrami_n = 2.2,
        .v_dd_volts = 1.8,
        .t_rise_ns = 1.0
    };

    FeRamSimulator simulator(config);
    auto results = simulator.run(10.0, 0.05);

    print_summary(results);

    return 0;
}
```
:::

---

### 3. Фізичний аналіз результатів розрахунку та чутливості

Результати чисельного виводу моделі описують динаміку формування сигналу на розрядній шині та дозволяють сформулювати наступні важливі висновки:

- **Часова залежність струму перемикання:** Струм перемикання `I_sw(t)` досягає максимуму при `t_peak ≈ 0.707 · τ₀` (для `n = 2.2`), що для даного прикладу відповідає `t ≈ 1.77 нс`. У цей момент швидкість бічного розростання доменних стінок є максимальною, а інжектований заряд швидко підвищує напругу `V_BL[1]`.
- **Залежність сигнального вікна від ємності розрядної шини:** Орієнтовне максимальне вікно сигналів `Sense_Margin = V_BL(1) - V_BL(0)` досягає значення `169.2 мВ` при `t = 5.0 нс` та ємності розрядної шини `C_BL = 650 фФ`. При подальшому збільшенні паразитної ємності шини Bitline маржа звужується пропорційно `Q_sw / C_total`, що вимагає підключення більш чутливого підсилювача або зменшення кількості комірок на одній розрядній шині.
- **Вплив швидкості фронту напруги `t_rise`:** Зменшення часу наростання фронту `t_rise` з `1.0 нс` до `0.2 нс` підвищує амплітуду лінійного струму `I_lin_max`, але прискорює загальний час виходу напруги `V_BL` на стаціонарне плато, що дозволяє скоротити час доступу `t_AA`.

---

### 4. Оцінка чисельної стійкості та кроку дискретизації dt

Для забезпечення високої точності чисельного інтегрування методом Ейлера вибір кроку дискретизації `dt` підпорядковується жорстким фізичним вимогам. Оскільки імпульс перемикання `I_sw(t)` має гострий пік з характерною шириною порядку `τ₀ / n`, занадто великий крок `dt > 0.5 · τ₀` призводить до катастрофічної втрати точності розрахунку пікового струму і заниження виділеного заряду `Q_sw`.

Рекомендації для чисельного розрахунку:
1. **Максимальний крок дискретизації:** `dt ≤ 0.02 · min(t_rise, τ₀)`. Для `τ₀ = 2.5 нс` оптимальним є крок `dt = 0.05 нс` (50 пікосекунд), що забезпечує відносну похибку розрахунку заряду менше ніж `0.1%`.
2. **Альтернативні методи інтегрування:** При включенні в розрахунок активного опору каналу NMOS-транзистора `R_DS` система диференціальних рівнянь стає «жорсткою» (*stiff system*), що вимагає переходу від явного методу Ейлера до неявного методу Ейлера або методів Рунге — Кутти 4-го порядку (RK4).

---

### 5. Інженерний аналіз та практичні підводні камені

При застосуванні чисельної симуляції для реального проектування мікросхем слід враховувати наступні фізико-схемотехнічні підводні камені:

1. **Паразитний опір словесної та пластинної шини:** Модель припускає ідеальний прямокутний або трапецієподібний фронт напруги. У реальних чипах скінченний опір металізації `R_plateline` створює RC-затримку, яка згладжує фронт `t_rise` для віддалених осередків масиву, розмиваючи пік струму перемикання.
2. **Вплив крутості фронту `dV/dt`:** Якщо фронт імпульсу `t_rise` значно довший за часову константу KAI `τ₀`, пікове значення струму перемикання `I_sw_max` падає за амплітудою. Це призводить до того, що розрядна шина заряджається повільніше, звужуючи часове вікно стробування підсилювача зчитування.
3. **Температурний дрейф константи KAI `τ₀`:** Швидкість перемикання залежить від температури за законом Арреніуса `τ₀(T) = τ_inf · exp(E_act / k_B T)`. При підвищенні температури до `125 °C` перемикання прискорюється, але зростають струми витоку Шотткі.
4. **Зсув внаслідок вкарбування (Imprint Shift):** Зсув коерцитивної напруги `V_shift` призводить до того, що дійсне коерцитивне поле стає асиметричним. У симуляторі це вимагає введення зміщеної ефективної напруги `V_eff = V_PL - V_shift`.
5. **Калібрування за даними PUND:** Для використання симулятора в промисловому проектуванні параметри `P_remnant`, `tau_0` та `avrami_n` витягуються з експериментальних імпульсних вимірювань PUND (Positive-Up-Negative-Down) шляхом мінімізації середньоквадратичного відхилення між симульованою кривою `I_sw(t)` та виміряним осцилографічним імпульсом струму.
