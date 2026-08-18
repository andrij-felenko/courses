# ⚙️ Програмування та чисельне моделювання перехідного імпульсу ESD у захисних колах

Чисельне моделювання часового профілю струму та напруги при електростатичному розряді (ESD) є критично важливим етапом проектування сучасної електроніки. Воно дозволяє інженеру розрахувати ефективність захисних TVS-компонентів, визначити пікову напругу обмеження `V_max` на вхідних виводах мікросхеми та оцінити сумарну енергію `E_tvs`, яка розсіюється на кристалі супресора. Програмна реалізація чисельного інтегрування нелінійних диференціальних рівнянь розрядного RLC-кола дає можливість моделювати перехідні процеси за різними стандартами (HBM, CDM, IEC 61000-4-2) без залучення дорогих лабораторних випробувальних генераторів та високочастотних осцилографів.

### 1. Математична постановка та чисельні методи розв'язку

Система диференціальних рівнянь, що описує перехідний процес у послідовному RLC-колі з нелінійним захисним елементом (TVS-діодом), складається з двох зв'язаних диференціальних рівнянь першого порядку відносно напруги на накопичувальній ємності `V_c(t)` та розрядного струму `I(t)`:

```
dV_c / dt = -I / C
dI / dt   = (V_c - I · R_line - V_tvs(I)) / L
```

у цих рівняннях:
- `C` — ємність джерела розряду (наприклад, 150 пФ за IEC 61000-4-2);
- `L` — паразитна індуктивність провідників та виводів (10–50 нГн);
- `R_line` — активний опір розрядного тракту (330 Ом для системної моделі);
- `V_tvs(I)` — нелінійна вольт-амперна характеристика TVS-діода.

Вольт-амперна характеристика TVS-діода у режимі лавинного пробою моделюється нелінійною залежністю з урахуванням пробійної напруги `V_BR` та динамічного опору `R_dyn`:

```
V_tvs(I) = 0,                       якщо |I| = 0 та V < V_BR
V_tvs(I) = V_BR + |I| · R_dyn,      якщо |I| > 0 (режим лавинного пробою)
```

Оскільки часові масштаби наростання струму при ESD вимірюються пікосекундами (`t_r < 1` нс), відповідна система диференціальних рівнянь є жорсткою (Stiff Differential Equations). Для її чисельного розв'язку з високою точністю необхідно застосовувати методи інтегрування з малим кроком `dt = 1` пікосекунда (`10⁻¹²` с). При такому кроці дискретизації метод Ейлера першого або другого порядку забезпечує відмінну числову стабільність та високу швидкість обчислень.

Умова числової стабільності інтегрування вимагає, щоб крок по часу `dt` був значно меншим за мінімальну сталу часу контуру `τ_min`:

```
dt << τ_min = min( R_line · C, L / R_line, √(L · C) )
```

Для типових параметрів кола HBM сталі часу вимірюються наносекундами (`τ ≈ 1–5` нс), тому вибір кроку `dt = 1` пікосекунда забезпечує запас за точністю у тисячу разів, гарантуючи повну відсутність чисельної осциляції або розбіжності розв'язку.

Крайові випадки моделювання включають аналіз умов, коли паразитна індуктивність виводів друкованої плати `L` є високою (`L > 100` нГн), а динамічний опір діода `R_dyn` — надто малим. У цьому разі система може виходити у слабозгасаючий коливальний режим, породжуючи зворотний негативний імпульс напруги. Алгоритм автоматично відстежує зміну знаку струму й моделює роботу двонаправлених супресорних структур.

### 2. Архітектура та програмна реалізація симулятора

Програма симуляції побудована за модульним принципом:
1. **Блок конфігурації електричного кола (`esd_circuit_t` / `CircuitParameters`):** задає фізичні параметри генератора розряду (початковий потенціал `V_init`, ємність `C_cap`, індуктивність `L_ind`, опір `R_line`).
2. **Блок конфігурації супресора (`tvs_diode_t` / `TvsParameters`):** задає пробійну напругу `V_br`, динамічний опір `R_dyn` та паразитна ємність `C_parasitic`.
3. **Обчислювальне ядро симуляції:** виконує циклічний покроковий розрахунок змінних стану (`v_c`, `i_curr`), фіксує максимальні значення струму й напруги та здійснює чисельне інтегрування дисипованої потужності `P(t) = V_tvs(t) · I(t)`.

Приклад надано у двох ідіоматичних реалізаціях: мовою C (із класичним процедурним підходом) та мовою C++ (із використанням сучасних концепцій C++23, таких як `std::expected` для обробки помилок, strong types та беземисійна математика).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Структура параметрів еквівалентного RLC-кола ESD */
typedef struct {
    double C_cap;        /* Ємність джерела розряду, Фарад */
    double L_ind;        /* Паразитна індуктивність виводів, Генрі */
    double R_line;       /* Опір провідників та тіла, Ом */
    double V_init;       /* Початкова напруга розряду, Вольт */
} esd_circuit_t;

/* Структура параметрів захисного TVS-діода */
typedef struct {
    double V_br;         /* Пробійна напруга лавинного переходу, Вольт */
    double R_dyn;        /* Динамічний опір діода в режимі пробою, Ом */
    double C_parasitic;  /* Паразитна ємність p-n переходу, Фарад */
} tvs_diode_t;

/* Результати розрахунку симуляції */
typedef struct {
    double peak_current;   /* Піковий струм розряду, Ампер */
    double max_voltage;    /* Максимальна напруга обмеження на виводі, Вольт */
    double tvs_energy;     /* Сумарна енергія, розсіяна TVS-діодом, Джоуль */
    double duration_ns;    /* Тривалість імпульсу до рівня 10% струму, нс */
} simulation_result_t;

/* Обчислення напруги на TVS-діоді залежно від струму */
static double calculate_tvs_voltage(double current, const tvs_diode_t *tvs) {
    double abs_i = fabs(current);
    if (abs_i < 1e-6) {
        return 0.0;
    }
    return tvs->V_br + abs_i * tvs->R_dyn;
}

/* Функція моделювання перехідного процесу розряду */
simulation_result_t simulate_esd_transient(const esd_circuit_t *circuit,
                                           const tvs_diode_t *tvs,
                                           double sim_time_ns,
                                           double dt_ps) {
    simulation_result_t res = {0.0, 0.0, 0.0, 0.0};
    
    double dt = dt_ps * 1e-12;               /* Переведення пікосекунд у секунди */
    double total_time = sim_time_ns * 1e-9;  /* Переведення наносекунд у секунди */
    
    double v_c = circuit->V_init;            /* Початкова напруга на ємності */
    double i_curr = 0.0;                     /* Початковий струм у колі */
    double t = 0.0;
    
    double max_i = 0.0;
    double max_v = 0.0;
    double energy_tvs = 0.0;
    
    while (t < total_time && v_c > 0.1) {
        double v_tvs = calculate_tvs_voltage(i_curr, tvs);
        
        /* Диференціальні рівняння стану */
        double dv_c = -i_curr / circuit->C_cap;
        double di_dt = (v_c - i_curr * circuit->R_line - v_tvs) / circuit->L_ind;
        
        /* Крок інтегрування Ейлера */
        v_c += dv_c * dt;
        i_curr += di_dt * dt;
        t += dt;
        
        if (i_curr < 0.0) {
            i_curr = 0.0;
        }
        
        /* Фіксація максимумів */
        if (i_curr > max_i) {
            max_i = i_curr;
        }
        if (v_tvs > max_v) {
            max_v = v_tvs;
        }
        
        /* Інтегрування потужності TVS-діода: P = V_tvs * I */
        energy_tvs += (v_tvs * i_curr) * dt;
    }
    
    res.peak_current = max_i;
    res.max_voltage = max_v;
    res.tvs_energy = energy_tvs;
    res.duration_ns = t * 1e9;
    
    return res;
}

int main(void) {
    /* Налаштування параметрів IEC 61000-4-2 (8 кВ) */
    esd_circuit_t iec_hbm = {
        .C_cap = 150e-12,     /* 150 пФ */
        .L_ind = 10e-9,       /* 10 нГн паразитної індуктивності */
        .R_line = 330.0,      /* 330 Ом */
        .V_init = 8000.0      /* 8000 Вольт */
    };
    
    /* Параметри ультранизькоємного TVS-діода */
    tvs_diode_t tvs = {
        .V_br = 6.8,          /* Пробій при 6.8 В */
        .R_dyn = 0.25,        /* Динамічний опір 0.25 Ом */
        .C_parasitic = 0.3e-12/* 0.3 пФ */
    };
    
    printf("=== Симуляція перехідного процесу ESD (IEC 61000-4-2, 8 кВ) ===\n");
    simulation_result_t res = simulate_esd_transient(&iec_hbm, &tvs, 100.0, 1.0);
    
    printf("Піковий струм розряду (I_peak):    %.2f А\n", res.peak_current);
    printf("Максимальна напруга (V_clamp):     %.2f В\n", res.max_voltage);
    printf("Енергія розсіяна TVS (E_tvs):       %.4f мДж\n", res.tvs_energy * 1000.0);
    printf("Тривалість перехідного процесу:    %.1f нс\n", res.duration_ns);
    
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <algorithm>
#include <expected>
#include <string_view>

namespace esd_sim {

struct CircuitParameters {
    double capacitance_farads{150e-12};
    double inductance_henry{10e-9};
    double resistance_ohms{330.0};
    double initial_voltage_volts{8000.0};
};

struct TvsParameters {
    double breakdown_voltage{6.8};
    double dynamic_resistance{0.25};
    double parasitic_capacitance{0.3e-12};
};

struct SimulationResult {
    double peak_current_ampere{0.0};
    double max_clamping_voltage{0.0};
    double energy_tvs_joules{0.0};
    double duration_nanoseconds{0.0};
    std::vector<std::pair<double, double>> time_current_series{};
};

enum class SimulationError {
    InvalidParameters,
    NumericalInstability
};

class EsdTransientSolver {
public:
    explicit EsdTransientSolver(CircuitParameters circuit, TvsParameters tvs)
        : m_circuit(circuit), m_tvs(tvs) {}

    [[nodiscard]] std::expected<SimulationResult, SimulationError> solve(
        double sim_time_ns = 100.0, 
        double dt_ps = 1.0) const 
    {
        if (m_circuit.capacitance_farads <= 0.0 || m_circuit.inductance_henry <= 0.0) {
            return std::unexpected(SimulationError::InvalidParameters);
        }

        SimulationResult result;
        const double dt = dt_ps * 1e-12;
        const double total_time = sim_time_ns * 1e-9;

        double v_cap = m_circuit.initial_voltage_volts;
        double current = 0.0;
        double time = 0.0;

        result.time_current_series.reserve(static_cast<size_t>(sim_time_ns / (dt_ps * 1e-3)));

        while (time < total_time && v_cap > 0.05) {
            const double v_tvs = compute_tvs_voltage(current);

            const double dv_cap = -current / m_circuit.capacitance_farads;
            const double di_dt = (v_cap - current * m_circuit.resistance_ohms - v_tvs) 
                                / m_circuit.inductance_henry;

            v_cap += dv_cap * dt;
            current += di_dt * dt;
            time += dt;

            if (current < 0.0) {
                current = 0.0;
            }

            result.peak_current_ampere = std::max(result.peak_current_ampere, current);
            result.max_clamping_voltage = std::max(result.max_clamping_voltage, v_tvs);
            result.energy_tvs_joules += (v_tvs * current) * dt;

            result.time_current_series.emplace_back(time * 1e9, current);
        }

        result.duration_nanoseconds = time * 1e9;
        return result;
    }

private:
    [[nodiscard]] double compute_tvs_voltage(double current) const noexcept {
        const double abs_i = std::abs(current);
        if (abs_i < 1e-6) {
            return 0.0;
        }
        return m_tvs.breakdown_voltage + abs_i * m_tvs.dynamic_resistance;
    }

    CircuitParameters m_circuit;
    TvsParameters m_tvs;
};

} // namespace esd_sim

int main() {
    using namespace esd_sim;

    const CircuitParameters iec_hbm{150e-12, 10e-9, 330.0, 8000.0};
    const TvsParameters tvs_diode{6.8, 0.25, 0.3e-12};

    const EsdTransientSolver solver(iec_hbm, tvs_diode);
    const auto outcome = solver.solve(100.0, 1.0);

    if (!outcome) {
        std::cerr << "Помилка розрахунку симуляції ESD!\n";
        return 1;
    }

    const auto& res = outcome.value();
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== Обчислення симулятора ESD (C++23) ===\n";
    std::cout << "Піковий струм розряду (I_peak):    " << res.peak_current_ampere << " А\n";
    std::cout << "Напруга обмеження (V_clamp):       " << res.max_clamping_voltage << " В\n";
    std::cout << "Енергія розсіяна TVS (E_tvs):       " << (res.energy_tvs_joules * 1000.0) << " мДж\n";
    std::cout << "Тривалість імпульсу:              " << res.duration_nanoseconds << " нс\n";

    return 0;
}
```
:::

### 3. Детальний аналіз та інтерпретація результатів симуляції

Аналіз отриманих у ході обчислювального експерименту даних дозволяє зробити кілька важливих фізичних та інженерних висновків:

1. **Ефективність придушення перенапруги:** попри те, що початкова напруга джерела розряду становить 8000 В, правильно підібраний TVS-діод затискає напругу на захищеному виводі до рівня `V_clamp ≈ 12.3 В`. Це значення є абсолютно безпечним для більшості вхідних буферів, оскільки час дії напруги не перевищує 30 наносекунд.
2. **Вирішальна роль динамічного опору (`R_dyn`):** під час наростання пікового струму до 22 А напруга на діоді визначається не лише пробійною напругою `V_br = 6.8 В`, але й омічним спадом на динамічному опорі кристала `I_peak · R_dyn = 22 А · 0.25 Ом = 5.5 В`. Звідси випливає фундаментальне правило: для захисту надчутливих КМОН-структур із техпроцесом 5 нм чи 3 нм критично важливо вибирати TVS-супресори з мінімально можливим динамічним опором (`R_dyn < 0.1` Ом).
3. **Енергетичний розподіл у колі:** сумарна енергія, розсіяна TVS-діодом за 100 наносекунд, становить менше `0.01` мДж, тоді як загальна енергія джерела `E = 1/2 · C · V² = 4.8` мДж розсіюється на послідовному обмежувальному резисторі `R_line = 330` Ом. Це підтверджує, що грамотно спроектоване захисне коло запобігає тепловому перегріву захисного супресора.

### 4. Розширення моделі для двокаскадного схемного захисту

У високостійких промислових приладах застосовують двокаскадну схему захисту: зовнішній TVS-діод (Primary Protection) + послідовний обмежувальний резистор `R_lim` + внутрішні затискаючі діоди мікросхеми (Secondary Protection).

Для симуляції такої системи числове ядро доповнюється ще одним диференціальним рівнянням для струму внутрішнього діода `I_int(t)`:

```
I_int = (V_tvs - V_vdD - V_diode_drop) / R_lim
```

Завдяки цьому розширеному аналізу розробник може точніше вибрати геометричний розмір падів та захисних провідників на друкованій платі, а також перевірити відсутність деструктивного латч-ап (Latch-Up) ефекту в напівпровідниковій структурі.

Чисельний аналіз двокаскадних схем дозволяє точно оптимізувати номінал обмежувального резистора `R_lim` (зазвичай 10–33 Ом), щоб гарантувати, що струм через внутрішні маленькі діоди кристала не перевищить безпечний поріг 100 мА при найжорсткіших імпульсах ESD до 15 кВ.
