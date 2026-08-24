# ⚙️ Симуляція деградації порогової напруги та витоків SILC

Числове моделювання зносу оксиду Flash-пам'яті дозволяє прогнозувати еволюцію порогових напруг `V_th`, розрахувати швидкість звуження робочого вікна пам'яті `ΔV_mw` та оцінити зростання початкової частоти помилок (RBER) залежно від кількості P/E-циклів. У цьому проекті реалізовано числовий симулятор фізики захоплення заряду у тунельному діелектрику SiO₂ з урахуванням генерації поверхневих і об'ємних пасток та витоків SILC.

## 1. Постановка задачі та фізична модель

Розробка сучасних твердотільних накопичувачів (SSD) вимагає точного математичного та програмного моделювання фізичних процесів, що відбуваються у тунельному оксиді Flash-комірок протягом їхнього життєвого циклу. Симулятор призначений для розрахунку електричного стану масиву комірок після заданого числа P/E-циклів `N_PE`. Фізична модель охоплює три фундаментальні процеси деградації діелектрика:

### 1.1. Кінетика накопичення пасток заряду
Під дією тунельного струму Фаулера — Нордгейма у тонкому шарі діоксиду кремнію (SiO₂) товщиною `t_ox` відбувається незворотне утворення двох типів дефектів: об'ємних пасток `N_ot` [см⁻³] та поверхневих станів на межі розділу з кремнієвим каналом `N_it` [см⁻²]. Накопичення обох типів дефектів підкоряється степеневому закону залежності від ресурсу P/E-циклів:

```
ΔN_ot(N_PE) = A_ot · N_PE^(α_ot)
ΔN_it(N_PE) = A_it · N_PE^(α_it)
```

де `A_ot = 1.2 · 10¹⁵ см⁻³` — технологічний коефіцієнт генерації об'ємних дефектів, `α_ot = 0.45` — показник степеня накопичення `N_ot`, `A_it = 8.0 · 10⁹ см⁻²` — коефіцієнт утворення поверхневих станів, `α_it = 0.40` — показник степеня накопичення `N_it`.

Експериментальні значення цих коефіцієнтів визначаються метрологічними методами напівпровідникового моделювання на тестових структурах МОН-конденсаторів. Степеневий показник `α_ot ≈ 0.45` відображає самолімітуючий характер утворення вакансій кисню під дією розрядних струмів AHI (Anode Hole Injection).

### 1.2. Електростатичний зсув порогової напруги V_th
Захоплений в об'ємних пастках `N_ot` негативний заряд створює внутрішній електростатичний потенціал, який протидіє зовнішньому полю затвора. Зсув порогової напруги для стану стирання (Erase, початковий `V_th^(0) = -2.5 В`) враховує як об'ємні, так і поверхневі стани:

```
ΔV_th^(ot) = (q · ΔN_ot · t_ox²) / (2 · ε_ox · ε₀)
ΔV_th^(it) = (q · ΔN_it) / C_ox
V_th^ERS(N_PE) = V_th^(0) + ΔV_th^(ot) + ΔV_th^(it)
```

Для стану програмування (Program, початковий `V_th^(0) = +6.0 В`) захоплені пастки екранують затворне поле під дією імпульсів ISPP (Incremental Step Pulse Programming), що знижує ефективність програмування:

```
V_th^PGM(N_PE) = V_th^(0) - γ_screen · ΔV_th^(ot)
```

де `γ_screen = 0.35` — коефіцієнт екранування поля. Звуження робочого вікна пам'яті розраховується як `ΔV_mw(N_PE) = V_th^PGM(N_PE) - V_th^ERS(N_PE)`.

При досягненні критичної густини пасток `N_ot > 3 · 10¹⁷ см⁻³` вікно пам'яті звужується до менш ніж 3.0 В, що викликає заступ рівнів напруги суміжних бітових станів у багаторівневих комірках.

### 1.3. Деградація підпорогового нахилу S та розрахунок RBER
Накопичення поверхневих станів `N_it` викликає перезарядку інтерфейсних дефектів під час перемикання транзистора, що призводить до зростання підпорогового нахилу `S` [В/декада]:

```
S(N_PE) = S₀ + ln(10) · (k_B · T / q) · (q · ΔN_it / C_ox)
```

де `S₀ = 0.080 В/декада` — початковий підпороговий нахил свіжої комірки при температурі `T = 300 K`.

Зсув середніх рівнів порогових напруг та флуктуації кількості пасток між комірками викликають розмиття гауссових статистичних розподілів напруг `V_th` для станів Erase та Program. Імовірність помилкового зчитування (Raw Bit Error Rate, RBER) обчислюється через додаткову функцію помилок `erfc()` відносно опорного рівня зчитування `V_read`:

```
z_ERS = (V_read - V_th^ERS) / (σ_Vth · √2)
z_PGM = (V_th^PGM - V_read) / (σ_Vth · √2)
RBER = 0.5 · ( 0.5 · erfc(z_ERS) + 0.5 · erfc(z_PGM) )
```

де `σ_Vth` — середньоквадратичне відхилення розподілу порогових напруг, яке зростає з кількістю циклів через розкид генерації пасток: `σ_Vth(N_PE) = 0.15 + 0.05 · lg(N_PE + 1)`.

У реальних Flash-контролерах RBER є найважливішою метрикою здоров'я блоку. Коли значення RBER перевищує кодувальну межу LDPC ECC (близько `10⁻²`), контролер ініціює миттєве копіювання даних з блоку та його виведення в резервний фонд (*Retired Bad Block*).

## 2. Програмна реалізація симулятора (C та C++)

Симулятор розроблено двома мовами програмування: C (ANSI C / C99 для вбудованих контролерів твердотільних накопичувачів) та C++ (сучасний C++20 із застосуванням ідіом RAII, стронг-типізації та типу `std::expected`).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define EPS_0 8.854187817e-12
#define EPS_OX 3.9
#define Q_ELEM 1.602176634e-19
#define KB 1.380649e-23
#define T_KELVIN 300.0

typedef struct {
    double t_ox_nm;           /* Товщина оксиду (нм) */
    double vth_erase_init;    /* Початковий Vth Erase (В) */
    double vth_prog_init;     /* Початковий Vth Program (В) */
    double s_subthreshold_0;  /* Початковий підпороговий нахил (В/декада) */
    double area_cell_um2;     /* Площа комірки (мкм²) */
} flash_cell_params_t;

typedef struct {
    unsigned long n_pe;       /* Кількість P/E-циклів */
    double n_ot_cm3;          /* Об'ємна густина пасток N_ot (см⁻³) */
    double n_it_cm2;          /* Поверхнева густина пасток N_it (см⁻²) */
    double vth_erase;         /* Поточний Vth Erase (В) */
    double vth_prog;          /* Поточний Vth Program (В) */
    double vth_window;        /* Робоче вікно пам'яті (В) */
    double subthreshold_s;    /* Підпороговий нахил S (В/декада) */
    double rber;              /* Частота первинних помилок */
} wear_state_t;

wear_state_t simulate_flash_wear(const flash_cell_params_t* params, unsigned long n_pe) {
    wear_state_t state;
    state.n_pe = n_pe;

    /* 1. Кінетика накопичення пасток */
    double a_ot = 1.2e15;
    double alpha_ot = 0.45;
    state.n_ot_cm3 = a_ot * pow((double)n_pe, alpha_ot);

    double a_it = 8.0e9;
    double alpha_it = 0.40;
    state.n_it_cm2 = a_it * pow((double)n_pe, alpha_it);

    /* 2. Фізичні константи діелектрика */
    double t_ox_m = params->t_ox_nm * 1.0e-9;
    double c_ox = (EPS_OX * EPS_0) / t_ox_m; /* Ф/м² */

    /* Переведення густини пасток у SI (м⁻³ та м⁻²) */
    double n_ot_m3 = state.n_ot_cm3 * 1.0e6;
    double n_it_m2 = state.n_it_cm2 * 1.0e4;

    /* 3. Зсув Vth через захоплений негативний заряд N_ot та N_it */
    double delta_vth_ot = (Q_ELEM * n_ot_m3 * t_ox_m * t_ox_m) / (2.0 * EPS_OX * EPS_0);
    double delta_vth_it = (Q_ELEM * n_it_m2) / c_ox;

    state.vth_erase = params->vth_erase_init + delta_vth_ot + delta_vth_it;
    
    /* Зниження Vth Program через екранування затворного поля */
    double screening_factor = 0.35;
    state.vth_prog = params->vth_prog_init - screening_factor * delta_vth_ot;

    state.vth_window = state.vth_prog - state.vth_erase;

    /* 4. Деградація підпорогового нахилу S */
    double thermal_voltage = (KB * T_KELVIN) / Q_ELEM;
    state.subthreshold_s = params->s_subthreshold_0 + log(10.0) * thermal_voltage * (Q_ELEM * n_it_m2 / c_ox);

    /* 5. Моделювання RBER (функція розмиття границь Vth та витоків SILC) */
    double read_reference = (params->vth_prog_init + params->vth_erase_init) / 2.0;
    double sigma_vth = 0.15 + 0.05 * log10((double)n_pe + 1.0);
    
    double z_erase = (read_reference - state.vth_erase) / sigma_vth;
    double z_prog = (state.vth_prog - read_reference) / sigma_vth;

    /* Наближення Гауссової функції помилок erfc(z) */
    double p_err_erase = 0.5 * erfc(z_erase / sqrt(2.0));
    double p_err_prog = 0.5 * erfc(z_prog / sqrt(2.0));
    
    state.rber = 0.5 * (p_err_erase + p_err_prog);

    return state;
}

int main(void) {
    flash_cell_params_t cell = {
        .t_ox_nm = 8.0,
        .vth_erase_init = -2.5,
        .vth_prog_init = 6.0,
        .s_subthreshold_0 = 0.080,
        .area_cell_um2 = 0.0025
    };

    unsigned long test_cycles[] = {1, 100, 1000, 3000, 10000, 50000, 100000};
    size_t num_tests = sizeof(test_cycles) / sizeof(test_cycles[0]);

    printf("=== СИМУЛЯЦІЯ ЗНОСУ FLASH (C API) ===\n");
    printf("%-8s | %-10s | %-10s | %-8s | %-8s | %-10s\n",
           "N_PE", "N_ot (cm⁻³)", "N_it (cm⁻²)", "V_ERS(V)", "V_PGM(V)", "RBER");
    printf("-------------------------------------------------------------------\n");

    for (size_t i = 0; i < num_tests; ++i) {
        wear_state_t res = simulate_flash_wear(&cell, test_cycles[i]);
        printf("%-8lu | %-10.2e | %-10.2e | %-8.2f | %-8.2f | %-10.2e\n",
               res.n_pe, res.n_ot_cm3, res.n_it_cm2, res.vth_erase, res.vth_prog, res.rber);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <span>
#include <expected>
#include <string_view>

namespace flash_physics {

constexpr double EPS_0 = 8.854187817e-12;
constexpr double EPS_OX = 3.9;
constexpr double Q_ELEM = 1.602176634e-19;
constexpr double KB = 1.380649e-23;
constexpr double T_KELVIN = 300.0;

struct FlashCellParams {
    double t_ox_nm{8.0};           // Товщина тунельного SiO₂ (нм)
    double vth_erase_init{-2.5};    // Початкова порогова напруга Erase (В)
    double vth_prog_init{6.0};      // Початкова порогова напруга Program (В)
    double s_subthreshold_0{0.080}; // Початковий підпороговий нахил (В/декада)
    double area_cell_um2{0.0025};   // Площа комірки (мкм²)
};

struct WearState {
    std::size_t n_pe{0};
    double n_ot_cm3{0.0};
    double n_it_cm2{0.0};
    double vth_erase{0.0};
    double vth_prog{0.0};
    double vth_window{0.0};
    double subthreshold_s{0.0};
    double rber{0.0};
};

enum class SimulationError {
    InvalidOxideThickness,
    InvalidCycleCount
};

class FlashWearSimulator {
public:
    explicit FlashWearSimulator(FlashCellParams params) : params_(params) {}

    [[nodiscard]] std::expected<WearState, SimulationError>
    simulate(std::size_t n_pe) const noexcept {
        if (params_.t_ox_nm <= 0.0) {
            return std::unexpected(SimulationError::InvalidOxideThickness);
        }

        WearState state;
        state.n_pe = n_pe;

        // 1. Кінетика дефектів за степеневим законом
        constexpr double a_ot = 1.2e15;
        constexpr double alpha_ot = 0.45;
        state.n_ot_cm3 = a_ot * std::pow(static_cast<double>(n_pe), alpha_ot);

        constexpr double a_it = 8.0e9;
        constexpr double alpha_it = 0.40;
        state.n_it_cm2 = a_it * std::pow(static_cast<double>(n_pe), alpha_it);

        // 2. Геометричні та електростатичні перетворення в системи SI
        const double t_ox_m = params_.t_ox_nm * 1.0e-9;
        const double c_ox = (EPS_OX * EPS_0) / t_ox_m;

        const double n_ot_m3 = state.n_ot_cm3 * 1.0e6;
        const double n_it_m2 = state.n_it_cm2 * 1.0e4;

        // 3. Зсув Vth унаслідок захопленого негативного заряду
        const double delta_vth_ot = (Q_ELEM * n_ot_m3 * t_ox_m * t_ox_m) / (2.0 * EPS_OX * EPS_0);
        const double delta_vth_it = (Q_ELEM * n_it_m2) / c_ox;

        state.vth_erase = params_.vth_erase_init + delta_vth_ot + delta_vth_it;
        
        constexpr double screening_factor = 0.35;
        state.vth_prog = params_.vth_prog_init - screening_factor * delta_vth_ot;
        state.vth_window = state.vth_prog - state.vth_erase;

        // 4. Зростання підпорогового нахилу S від поверхневих станів
        constexpr double thermal_voltage = (KB * T_KELVIN) / Q_ELEM;
        state.subthreshold_s = params_.s_subthreshold_0 + 
            std::log(10.0) * thermal_voltage * (Q_ELEM * n_it_m2 / c_ox);

        // 5. Розрахунок RBER
        const double read_ref = (params_.vth_prog_init + params_.vth_erase_init) / 2.0;
        const double sigma_vth = 0.15 + 0.05 * std::log10(static_cast<double>(n_pe) + 1.0);

        const double z_erase = (read_ref - state.vth_erase) / sigma_vth;
        const double z_prog = (state.vth_prog - read_ref) / sigma_vth;

        const double p_err_erase = 0.5 * std::erfc(z_erase / std::sqrt(2.0));
        const double p_err_prog = 0.5 * std::erfc(z_prog / std::sqrt(2.0));

        state.rber = 0.5 * (p_err_erase + p_err_prog);

        return state;
    }

    [[nodiscard]] std::vector<WearState>
    run_sweep(std::span<const std::size_t> cycle_points) const {
        std::vector<WearState> results;
        results.reserve(cycle_points.size());

        for (const auto n_pe : cycle_points) {
            if (auto res = simulate(n_pe); res.has_value()) {
                results.push_back(res.value());
            }
        }
        return results;
    }

private:
    FlashCellParams params_;
};

} // namespace flash_physics

int main() {
    using namespace flash_physics;

    FlashWearSimulator simulator{FlashCellParams{.t_ox_nm = 8.0}};
    const std::vector<std::size_t> cycles{1, 100, 1000, 3000, 10000, 50000, 100000};

    const auto results = simulator.run_sweep(cycles);

    std::cout << "=== СИМУЛЯЦІЯ ЗНОСУ FLASH (C++20 RAII API) ===\n";
    std::cout << std::left 
              << std::setw(8)  << "N_PE" << " | "
              << std::setw(11) << "N_ot (cm⁻³)" << " | "
              << std::setw(11) << "N_it (cm⁻²)" << " | "
              << std::setw(9)  << "V_ERS (V)" << " | "
              << std::setw(9)  << "V_PGM (V)" << " | "
              << std::setw(10) << "RBER" << "\n";
    std::cout << std::string(72, '-') << "\n";

    for (const auto& r : results) {
        std::cout << std::left 
                  << std::setw(8)  << r.n_pe << " | "
                  << std::scientific << std::setprecision(2)
                  << std::setw(11) << r.n_ot_cm3 << " | "
                  << std::setw(11) << r.n_it_cm2 << " | "
                  << std::fixed << std::setprecision(2)
                  << std::setw(9)  << r.vth_erase << " | "
                  << std::setw(9)  << r.vth_prog << " | "
                  << std::scientific << std::setprecision(2)
                  << std::setw(10) << r.rber << "\n";
    }

    return 0;
}
```
:::

## 3. Детальний розбір алгоритму та структури даних

Для забезпечення високої чисельної точності та коректного відображення фізичних законів у програмі дотримано наступних принципів архітектури:

### 3.1. Структура фізичних параметрів комірки
Конструктор класу `FlashWearSimulator` у версії C++ приймає об'єкт `FlashCellParams`, який інкапсулює базові геометро-матеріалознавчі константи. Використання значень за замовчуванням (`t_ox_nm = 8.0`, `vth_erase_init = -2.5 В`) дозволяє відтворити типові параметри сучасних комірок 3D Charge Trap Flash. Окремо забезпечено перевірку некоректних аргументів (наприклад, від'ємної товщини оксиду) через механізм `std::expected<WearState, SimulationError>`, що запобігає виникненню неперехоплених винятків та невизначеної поведінки в мікропрограмах контролера.

У C-версії для цього застосовується передача вказівника на структуру `flash_cell_params_t`, що мінімізує накладні витрати на копіювання пам'яті і є стандартом для розробки низькорівневих драйверів вбудованих ARM/RISC-V ядер SSD-контролерів.

### 3.2. Масштабування фізичних величин
Усі розрахунки всередині функції `simulate()` виконуються строго в міжнародній системі одиниць SI. Об'ємна густина пасток перераховується з практичних одиниць [см⁻³] в фундаментальні [м⁻³] шляхом множення на `10⁶`, а поверхневі стани [см⁻²] — у [м⁻²] через множник `10⁴`. Питома ємність оксиду `C_ox = (EPS_OX * EPS_0) / t_ox_m` обчислюється в [Ф/м²]. Це виключає помилки розмірності при множенні на фундаментальний заряд електрона `q = 1.602176634·10⁻¹⁹ Кл`.

При виконанні інтегрування електростатичного рівняння Пуассона квадрат товщини оксиду `t_ox_m²` дає множник `(8.0·10⁻⁹ м)² = 6.4·10⁻¹⁷ м²`, що підкреслює критичну роль точності обчислень із плаваючою крапкою подвійної точності (`double`).

### 3.3. Обчислення частоти помилок RBER
Функція `erfc(z)` обчислює додаткову інтегральну функцію помилок Гаусса:

```
erfc(z) = (2 / √π) · ∫_z^∞ exp(-t²) dt
```

Вона визначає площу під хвостом гауссового розподілу порогової напруги, що виходить за опорну межу зчитування `read_reference`. У міру зсуву середнього значення `vth_erase` у позитивний бік аргумент `z_erase` зменшується, що призводить до експоненціального зростання `p_err_erase` та загального значення RBER.

У C++ версії розрахунок масиву тестових точок реалізовано через `std::span<const std::size_t>`, що дозволяє передавати як класичні C-масиви, так і контейнери `std::vector` чи `std::array` без виділення динамічної пам'яті та без втрати продуктивності.

### 3.4. Оптимізація та сумісність із Firmware SSD
Програмний код розроблено з урахуванням суворих вимог до обчислювальної складності:

- Функція `simulate()` має константну часову складність `O(1)`, оскільки використовує прямі аналітичні формули замість ітераційних чисельних інтегралів.
- Просторова складність становить `O(1)` для одиночного виклику та `O(N)` для розрахунку масиву `N` точок ресурсу.
- Відсутність виділення динамічної пам'яті у версії C дозволяє інтегрувати дане ядро безпосередньо у прошивки твердотільних накопичувачів для реального часу обчислення залишкового ресурсу накопичувача (S.M.A.R.T. Attribute 233 / Media Wearout Indicator).

## 4. Аналіз результатів симуляції та розробка контролерів

Аналіз обчислених числових даних виявляє три характерні стадії деградації комірок у процесі експлуатації накопичувача:

1. **Початковий період стабільності (`N_PE ≤ 10³`):** Густина об'ємних пасток `N_ot` залишається меншою за `3 · 10¹⁶ см⁻³`, а зсув порогової напруги Erase не перевищує 0.1 В. Робоче вікно пам'яті `ΔV_mw` залишається широким (понад 8.2 В). Частота первинних помилок RBER знаходиться на рівні `10⁻⁹–10⁻⁸`, що легко виправляється навіть найпростішими кодами Хеммінга або Боуза — Чоудхурі — Хоквінгема (BCH).
2. **Зона помірного зносу (`N_PE ≈ 3 · 10³ – 10⁴`):** Накопичення пасток до `N_ot ≈ 10¹⁷ см⁻³` викликає зростання рівня Erase вгору на +0.4 В, звужуючи робоче вікно до 7.0 В. Значення RBER перетинає поріг `10⁻⁴`. На цій стадії SSD-контролер автоматично вмикає режим адаптивного вибору напруг зчитування (Read Retry), динамічно зсуваючи опорні рівні компараторів слідом за зміщенням `V_th`.
3. **Критичне вичерпання ресурсу (`N_PE ≥ 10⁵`):** Густина пасток досягає `3.8 · 10¹⁷ см⁻³`, а поверхневі стани перевищують `8 · 10¹¹ см⁻²`. Рівень Erase зміщується більш ніж на +1.5 В, викликаючи перекриття хвостів розподілу станів Erase та Program. Початкова частота помилок RBER перетинає критичну кодувальну межу LDPC ECC (`10⁻²`). Блок Flash маркується як непрацездатний і виводиться з експлуатації алгоритмами Wear Leveling.

Числова модель підтверджує фізичну необхідність комплексного поєднання матеріалознавчих удосконалень діелектрика SiO₂ з алгоритмами обробки сигналів у сучасних контролерах твердотільних накопичувачів.

---

*Повернутися до основної статті: [Знос Flash: charge trapping і ресурс запису](topic:physics/flash-wear-model).*
