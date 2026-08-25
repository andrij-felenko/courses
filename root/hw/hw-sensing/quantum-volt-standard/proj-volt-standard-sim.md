# ⚙️ Симуляція фазового захоплення та сходинок Шапіро у перехіднику Джозефсона

Ця прикладна вставка містить концептуальне обґрунтування, математичний алгоритм чисельного інтегрування, аналіз стохастичних шумів та робочі реалізації мовами C та C++ для симуляції вольт-амперної характеристики контакту Джозефсона у присутності СВЧ випромінювання (модель RSJ) та автоматичного виявлення квантованих сходинок Шапіро.

### Фізико-математична модель RSJ та алгоритм інтегрування

Динаміка квантової фази `Δφ` у зашунтованому тунельному переході Джозефсона з урахуванням власної ємності `C` та нормального опору `R_N` описується звичайним диференціальним рівнянням другого порядку з нелінійним синусоїдальним членом (модель RSJ — *Resistively and Capacitively Shunted Junction*):

```
(ℏ · C / 2e) · d²(Δφ)/dt² + (ℏ / (2e · R_N)) · d(Δφ)/dt + I_c · sin(Δφ) = I_dc + I_rf · cos(2π · f · t) + I_n(t)
```

де `I_n(t)` — стохастичний член Ланжевена, що описує тепловий білий шум нормального опору `R_N` за формулою Найквіста з спектральною щільністю `S_I = 4k_B · T / R_N`.

Для проведення комп'ютерного моделювання зручно перейти до безрозмірних змінних. Зведемо це диференціальне рівняння другого порядку до системи двох зв'язаних диференціальних рівнянь першого порядку відносно квантової фази `φ = Δφ` та нормованої миттєвої напруги `v = V / (I_c · R_N)`:

```
dφ / dt = (2e · I_c · R_N / ℏ) · v
dv / dt = (1 / β_c) · [ i_bias + i_rf · cos(ω_norm · τ) - sin(φ) - v + i_noise(τ) ]
```

де `τ = t · (2e · I_c · R_N / ℏ)` — безрозмірний час, `β_c = 2e · I_c · R_N² · C / ℏ` — параметр Стюарта — Маккамбера, який визначає згасання коливань та ступінь гістерезису ВАХ, `ω_norm = 2π · f / (2e · I_c · R_N / ℏ)` — нормована частота СВЧ поля, а `i_bias = I_dc / I_c` — нормований струм зсуву від зовнішнього джерела живлення.

Чисельний алгоритм здійснює крокове інтегрування отриманої системи диференціальних рівнянь за допомогою класичного четвертопорядкового методу Рунге — Кутти (RK4). Метод RK4 забезпечує локальну похибку обчислень порядку `O(dt⁵)` і гарантує високу числову стабільність при моделюванні нелінійних фазових коливань.

Для кожного фіксованого значення струму зсуву `i_bias` у діапазоні від `0` до `3.0` алгоритм виконує двофакторне розщеплення обчислювального циклу:

1. **Релаксація перехідного стану:** Виконується `4000` кроків інтегрування без збереження результатів для повного затухання початкового перехідного процесу (релаксація кріогенного стану та фазове узгодження).
2. **Усереднення стаціонарного стану:** Здійснюється усереднення часового ряду напруги `v(τ)` за `10000` кроків (що відповідає багаторазовому проходженню періодів СВЧ випромінювання):

```
<v> = (1 / T_avg) · ∫ v(τ) dτ
```

Якщо середня нормована напруга `<v>` залишається абсолютно незмінною при збільшенні струму зсуву `i_bias`, це свідчить про утворення квантованої сходинки Шапіро `n = <v> / ω_norm`.

### Фазова дифузія та теплове округлення сходинок

У реальних експериментальних умовах при температурі вищій за абсолютний нуль (`T > 0` К) теплові флуктуації `i_noise(τ)` викликають спонтанні стрибки фази на `±2π` (фазову дифузію). Це призводить до часткового розмивання та згладжування кутів сходинок Шапіро на ВАХ. Зменшення параметра Стюарта — Маккамбера `β_c < 0.5` пригнічує гістерезис і розширює діапазон стабільності сходинок.

У реальному метрологічному програмному забезпеченні алгоритм автоматичного розпізнавання сходинок обчислює дискретну похідну `d<v>/di_bias`. Плато квантованої сходинки ідентифікується за умови, коли похідна падає нижче заданого метрологічного порогу `|d<v>/di_bias| < 10⁻⁸`. Метрологічний контролер автоматично фіксує діапазон струму зсуву, у якому напруга квантується з нульовою похибкою, і сигналізує інженеру про готовність квантового стандарту до проведення калібрувальних вимірювань.

### Зіставлення ідіоматики реалізацій C та C++

При виборі мови програмування для метрологічного симулятора критичними є обчислювальна швидкість, об'єктна безпека та точність розрахунку:

- **Реалізація мовою C (C99):** Застосовує явне керування пам'яттю, чисті C-структури `JosephsonConfig` та `State`, функції з передачею за вказівником для уникнення накладних витрат стеків та класичні функції математичної бібліотеки `math.h`. Використання статичних чисельних функцій дозволяє компілятору здійснювати агресивну векторну оптимізацію циклу інтегрування.
- **Реалізація мовою C++ (C++20):** Використовує ідіому RAII для утримання стану фазового осцилятора, константні вирази `constexpr`, атрибути `[[nodiscard]]` та `noexcept` для максимальної оптимізації компілятором, типізований формат виводу `<iomanip>` та математичні константи стандарту C++20 `<numbers>`. Об'єктно-орієнтований клас `JosephsonSimulator` гарантує збереження квантової фазової неперервності між кроками зсуву струму та запобігає втраті фазового зсуву при перезапуску циклу.

### Реалізація симулятора мовами C та C++

Нижче наведено робочий код чисельного симулятора ВАХ переходу Джозефсона. Код обчислює напругу при лінійному скануванні струму зсуву та виявляє перші квантовані сходинки Шапіро.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double beta_c;     /* Параметр Стюарта-Маккамбера (0.1 для overdamped) */
    double omega_rf;   /* Нормована частота СВЧ (f_rf / f_J0) */
    double i_rf;       /* Нормована амплітуда СВЧ струму */
    double dt;         /* Крок інтегрування по безрозмірному часу */
    int trans_steps;   /* Кількість кроків для затухання переходного процесу */
    int avg_steps;     /* Кількість кроків для усереднення напруги */
} JosephsonConfig;

typedef struct {
    double phi;
    double v;
} State;

static State derivatives(State s, double t, double i_bias, const JosephsonConfig *cfg) {
    State d;
    d.phi = s.v;
    double i_total = i_bias + cfg->i_rf * cos(cfg->omega_rf * t);
    d.v = (i_total - sin(s.phi) - s.v) / cfg->beta_c;
    return d;
}

static State rk4_step(State s, double t, double i_bias, const JosephsonConfig *cfg) {
    double dt = cfg->dt;
    
    State k1 = derivatives(s, t, i_bias, cfg);
    
    State s2 = { s.phi + 0.5 * dt * k1.phi, s.v + 0.5 * dt * k1.v };
    State k2 = derivatives(s2, t + 0.5 * dt, i_bias, cfg);
    
    State s3 = { s.phi + 0.5 * dt * k2.phi, s.v + 0.5 * dt * k2.v };
    State k3 = derivatives(s3, t + 0.5 * dt, i_bias, cfg);
    
    State s4 = { s.phi + dt * k3.phi, s.v + dt * k3.v };
    State k4 = derivatives(s4, t + dt, i_bias, cfg);
    
    State res;
    res.phi = s.phi + (dt / 6.0) * (k1.phi + 2.0 * k2.phi + 2.0 * k3.phi + k4.phi);
    res.v   = s.v   + (dt / 6.0) * (k1.v   + 2.0 * k2.v   + 2.0 * k3.v   + k4.v);
    return res;
}

int main(void) {
    JosephsonConfig cfg = {
        .beta_c = 0.2,
        .omega_rf = 1.0,
        .i_rf = 1.2,
        .dt = 0.05,
        .trans_steps = 4000,
        .avg_steps = 10000
    };

    printf("Simulating Shapiro steps for overdamped Josephson Junction (C)\n");
    printf("i_bias\t\t<v>\t\tStep Index (n = <v>/w_rf)\n");

    State current_state = { 0.0, 0.0 };

    for (double i_bias = 0.0; i_bias <= 3.0; i_bias += 0.05) {
        double t = 0.0;
        
        /* Пропуск перехідного процесу */
        for (int step = 0; step < cfg.trans_steps; ++step) {
            current_state = rk4_step(current_state, t, i_bias, &cfg);
            t += cfg.dt;
        }

        /* Усереднення напруги */
        double v_sum = 0.0;
        for (int step = 0; step < cfg.avg_steps; ++step) {
            current_state = rk4_step(current_state, t, i_bias, &cfg);
            v_sum += current_state.v;
            t += cfg.dt;
        }

        double v_avg = v_sum / cfg.avg_steps;
        double step_index = v_avg / cfg.omega_rf;

        printf("%.3f\t\t%.5f\t\t%.2f\n", i_bias, v_avg, step_index);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <numbers>

struct JosephsonParams {
    double beta_c{0.2};      // Parameter Stewart-McCumber
    double omega_rf{1.0};    // Normalized RF frequency
    double i_rf{1.2};        // RF current amplitude
    double dt{0.05};         // Integration time step
    int trans_steps{4000};   // Transient relaxation steps
    int avg_steps{10000};    // Averaging steps
};

struct PhaseState {
    double phi{0.0};
    double v{0.0};
};

class JosephsonSimulator {
public:
    explicit JosephsonSimulator(JosephsonParams params) : params_(params) {}

    [[nodiscard]] double simulate_average_voltage(double i_bias) {
        PhaseState state = current_state_;
        double t = 0.0;

        // Pass transient response using RK4
        for (int step = 0; step < params_.trans_steps; ++step) {
            state = rk4_step(state, t, i_bias);
            t += params_.dt;
        }

        // Accumulate average voltage
        double v_sum = 0.0;
        for (int step = 0; step < params_.avg_steps; ++step) {
            state = rk4_step(state, t, i_bias);
            v_sum += state.v;
            t += params_.dt;
        }

        current_state_ = state; // Preserve state for phase continuity
        return v_sum / params_.avg_steps;
    }

private:
    JosephsonParams params_;
    PhaseState current_state_{};

    [[nodiscard]] PhaseState derivatives(const PhaseState& s, double t, double i_bias) const noexcept {
        double i_total = i_bias + params_.i_rf * std::cos(params_.omega_rf * t);
        double dv_dt = (i_total - std::sin(s.phi) - s.v) / params_.beta_c;
        return PhaseState{ .phi = s.v, .v = dv_dt };
    }

    [[nodiscard]] PhaseState rk4_step(const PhaseState& s, double t, double i_bias) const noexcept {
        const double dt = params_.dt;
        
        auto k1 = derivatives(s, t, i_bias);
        auto k2 = derivatives(PhaseState{s.phi + 0.5 * dt * k1.phi, s.v + 0.5 * dt * k1.v}, t + 0.5 * dt, i_bias);
        auto k3 = derivatives(PhaseState{s.phi + 0.5 * dt * k2.phi, s.v + 0.5 * dt * k2.v}, t + 0.5 * dt, i_bias);
        auto k4 = derivatives(PhaseState{s.phi + dt * k3.phi, s.v + dt * k3.v}, t + dt, i_bias);

        return PhaseState{
            .phi = s.phi + (dt / 6.0) * (k1.phi + 2.0 * k2.phi + 2.0 * k3.phi + k4.phi),
            .v   = s.v   + (dt / 6.0) * (k1.v   + 2.0 * k2.v   + 2.0 * k3.v   + k4.v)
        };
    }
};

int main() {
    JosephsonParams params;
    JosephsonSimulator simulator(params);

    std::cout << "Simulating Shapiro steps for overdamped Josephson Junction (C++20)\n";
    std::cout << std::setw(10) << "i_bias" << std::setw(15) << "<v>" << std::setw(20) << "Step Index (n)" << '\n';
    std::cout << std::string(45, '-') << '\n';

    for (double i_bias = 0.0; i_bias <= 3.0; i_bias += 0.05) {
        double v_avg = simulator.simulate_average_voltage(i_bias);
        double step_n = v_avg / params.omega_rf;

        std::cout << std::fixed << std::setprecision(3)
                  << std::setw(10) << i_bias
                  << std::setw(15) << std::setprecision(5) << v_avg
                  << std::setw(20) << std::setprecision(2) << step_n << '\n';
    }

    return 0;
}
```
:::

### Практичні висновки та фізична інтерпретація симуляції

Чисельне моделювання дозволяє продемонструвати декілька ключових фізичних аспектів функціонування квантового стандарту напруги:

1. **Формування плато квантування:** На графіку залежності нормованої напруги `<v>` від струму зсуву `i_bias` виникають чітко окреслені горизонтальні плато (сходинки Шапіро) точно при значеннях напруги `v = n · ω_rf`. Збільшення струму зсуву в межах плато зміщує фазову константу `Δφ_0`, але не змінює значення напруги навіть на частки відсотка.
2. **Вплив параметра Стюарта — Маккамбера (`β_c`):** При малому значенні `β_c < 0.5` (переходи типу SNS або SINIS з великим нормальним згасанням) сходинки є безгістерезисними та стабільними, що уможливлює швидке та однозначне програмування напруги у PJVS системах без ризику застрягання у метастабільних станах.
3. **Залежність ширини сходинок від амплітуди СВЧ (`i_rf`):** Зміна амплітуди СВЧ струму `i_rf` змінює ширину плато за законом функцій Бесселя `J_n(z)`. Для досягнення максимальної метрологічної стабільності еталона потужність СВЧ генератора налаштовують на перший максимум відповідної функції Бесселя.
4. **Обчислювальний алгоритм виявлення плато:** У реальному метрологічному програмному забезпеченні алгоритм аналізує похідну `d<v>/di_bias`: локальні мінімуми похідної, близькі до нуля, ідентифікують центр стабільної квантованої сходинки Шапіро.
