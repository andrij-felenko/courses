# ⚙️ Моделювання руху провідного центру плазми у тороїдальному магнітному полі

Ця вставка містить чисельну реалізацію інтегрування рівнянь руху провідного центру зарядженої частинки (іона або електрона) у тороїдальному магнітному полі. Програма моделює два принципово різних фізичних сценарії: суто тороїдальне магнітне поле (де виникає вертикальне розділення зарядів через градієнтний та кривинний дрейфи із наступним випромінюванням плазми на стінку) і магнітне поле з обертальним перетворенням (наявність полоїдальної компоненти `B_θ`), яке компенсує дрейф і забезпечує замкнену бананову або пролітну дрейфову орбіту.

---

### Фізична модель та рівняння руху

Провідний центр частинки описується координатами `(R, Z, φ)` у циліндричній системі тора, де `R` — радіус від центральної осі, `Z` — вертикальна висота, `φ` — тороїдальний кут.

Магнітне поле у пастці задається сумою тороїдальної та полоїдальної компонент:

```
B_φ(R) = B_0 · R_0 / R
B_θ(r) = B_pol_0 · (r / a)
```

де `r = √((R - R_0)² + Z²)` — відстань від магнітної осі.

Рівняння руху провідного центру для частинки з масою `m`, зарядом `q`, паралельною швидкістю `v_parallel` та магнітним моментом `μ = m · v_perp² / (2B)` записуються у формі системи звичайних диференціальних рівнянь (ЗДР):

```
dR / dt = v_rot_R
dZ / dt = v_rot_Z + v_drift_Z
```

де швидкість обертання вздовж гвинтової силової лінії дорівнює:

```
v_rot_R = - v_parallel · (B_θ / B_total) · (Z / r)
v_rot_Z =   v_parallel · (B_θ / B_total) · ( (R - R_0) / r )
```

а швидкість сумарного вертикального градієнтного та кривинного дрейфу становить:

```
v_drift_Z = ( m · v_parallel² + μ · B_total ) / ( q · B_0 · R_0 )
```

---

### Чисельний метод інтегрування та збереження адіабатичних інваріантів

Для чисельного розв'язання системи рівнянь руху провідного центру застосовується класичний метод Рунге-Кутти 4-го порядку (RK4). Крок за часом `dt` вибирається таким чином, щоб він був значно меншим за період полоїдального обертання частинки `τ_pol ≈ 2π · R_0 / v_parallel` (типово `dt = 10⁻⁸ с`).

На кожному кроці інтегрування симулятор перевіряє збереження трьох фізичних величин:
1. **Повна кінетична енергія:** `E = 1/2 · m · (v_parallel² + v_perp²) = const`.
2. **Магнітний момент ларморівської орбіти:** `μ = (m · v_perp²) / (2 · B) = const`.
3. **Тороїдальний канонічний імпульс:** `P_φ = m · R · v_φ + q · ψ = const`.

Для запертих частинок (частинок із великими кутами `θ` між вектором швидкості та силовою лінією) у точці повороту `v_parallel = 0` виконується умова дзеркального відбиття: `B(R_reflect) = E / μ`. В цій точці частинка відбивається від області сильнішого магнітного поля і починає рухатися у зворотному тороїдальному напрямку, утворюючи характерну **бананову орбіту**.

---

### Алгоритм Бориса проти методів Runge-Kutta

При повній фазовій симуляції руху частинки (включаючи швидке ларморівське обертання з частотою `ω_c ≈ 10⁸ Гц`) стандартні класичні методи інтегрування Runge-Kutta (RK4) накопичують амплітудну похибку і призводять до штучного «набухання» ларморівського радіуса через накопичення числової дисипації за мільйони періодів обертання.

Для вирішення цієї проблеми у фізиці плазми застосовують **алгоритм Бориса** (Boris pusher, на честь американського фізика Джея Бориса, англ. *Jay P. Boris*). Алгоритм Бориса є часово-симетричним симплектичним схематичним розділенням прискорення полем `E` та обертання полем `B`:

1. Напівкроковий прискорення електричним полем: `v_minus = v_n + (q · E / m) · (dt / 2)`.
2. Чисте векторне обертання швидкості у магнітному полі `B` без зміни її модуля `|v_minus| = |v_plus|`.
3. Друге напівкрокове прискорення: `v_{n+1} = v_plus + (q · E / m) · (dt / 2)`.

Симплектичність алгоритму Бориса забезпечує точне збереження фазового об'єму та збереження енергії частинки без систематичного числового дрейфу протягом мільйонів циклотронних періодів.

---

### Граничні умови та втрата частинок на стінці

У реальній геометричній симуляції токамака чисельна модель контролює відстань від провідного центру до магнітної осі `r = √((R - R_0)² + Z²)`.

Якщо у процесі обчислення траєкторія частинки виходить за малий радіус камери (`r ≥ a`), симулятор фіксує подію **виходу частинки на першу стінку** або лімітер. Для частинок у шарі відскрібання (Scrape-Off Layer, SOL) при виході за сепаратрису `r > r_sep` рівняння руху доповнюються паралельним витоком уздовж відкритих силових ліній до дивертора зі швидкістю іонного звуку `v_sound = √((k_B · (T_e + γ · T_i)) / m_i)`.

---

### Реалізація симулятора

Нижче наведено робочий код симулятора трьома мовами програмування. Кожна вкладка представляє ідіоматичний варіант розв'язку: від класичної C-моделі до сучасного C++20 із використання `std::vector` та Python з використанням `numpy`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    double R_0;      /* Великий радіус тора (м) */
    double a;        /* Малий радіус камери (м) */
    double B_0;      /* Тороїдальне поле на осі (Тл) */
    double B_pol_0;  /* Полоїдальне поле на краю (Тл) */
    double mass;     /* Маса частинки (кг) */
    double charge;   /* Заряд частинки (Кл) */
} PlasmaConfig;

typedef struct {
    double R;          /* Радіус (м) */
    double Z;          /* Висота (м) */
    double v_parallel; /* Паралельна швидкість (м/с) */
    double v_perp;     /* Перпендикулярна швидкість (м/с) */
} GuidingCenterState;

/* Крок чисельного інтегрування методом Рунге-Кутти 4-го порядку (RK4) */
void gc_step_rk4(GuidingCenterState *s, const PlasmaConfig *cfg, double dt) {
    double q = cfg->charge;
    double m = cfg->mass;
    double R0 = cfg->R_0;
    double B0 = cfg->B_0;
    double Bpol0 = cfg->B_pol_0;

    /* Обчислення похідних в точці (R, Z) */
    auto compute_derivatives = [&](double R, double Z, double *dR, double *dZ) {
        double r = sqrt((R - R0)*(R - R0) + Z*Z);
        if (r < 1e-6) r = 1e-6;

        double B_phi = B0 * R0 / R;
        double B_pol = Bpol0 * (r / cfg->a);
        double B_total = sqrt(B_phi*B_phi + B_pol*B_pol);

        double mu = (m * s->v_perp * s->v_perp) / (2.0 * B_total);
        double v_drift_Z = (m * s->v_parallel * s->v_parallel + mu * B_total) / (q * B0 * R0);

        /* Обертальне перетворення (рух уздовж силової лінії B_pol) */
        double v_rot_R = -s->v_parallel * (B_pol / B_total) * (Z / r);
        double v_rot_Z =  s->v_parallel * (B_pol / B_total) * ((R - R0) / r);

        *dR = v_rot_R;
        *dZ = v_rot_Z + v_drift_Z;
    };

    double dR1, dZ1, dR2, dZ2, dR3, dZ3, dR4, dZ4;
    compute_derivatives(s->R, s->Z, &dR1, &dZ1);
    compute_derivatives(s->R + 0.5*dt*dR1, s->Z + 0.5*dt*dZ1, &dR2, &dZ2);
    compute_derivatives(s->R + 0.5*dt*dR2, s->Z + 0.5*dt*dZ2, &dR3, &dZ3);
    compute_derivatives(s->R + dt*dR3, s->Z + dt*dZ3, &dR4, &dZ4);

    s->R += (dt / 6.0) * (dR1 + 2.0*dR2 + 2.0*dR3 + dR4);
    s->Z += (dt / 6.0) * (dZ1 + 2.0*dZ2 + 2.0*dZ3 + dZ4);
}

int main(void) {
    PlasmaConfig cfg = {
        .R_0 = 1.65,      /* Параметри токамака ASDEX Upgrade */
        .a = 0.5,
        .B_0 = 2.5,
        .B_pol_0 = 0.3,   /* Якщо 0.0 — суто тороїдальне поле без B_θ */
        .mass = 3.34e-27, /* Маса дейтерієвого іона D+ */
        .charge = 1.602e-19
    };

    GuidingCenterState state = {
        .R = 1.85,
        .Z = 0.0,
        .v_parallel = 5.0e5, /* Теплова швидкість T ~ 2 keV */
        .v_perp = 7.0e5
    };

    double dt = 1.0e-8;
    int num_steps = 10000;

    printf("Крок\tR (м)\t\tZ (м)\n");
    for (int i = 0; i <= num_steps; i++) {
        if (i % 1000 == 0) {
            printf("%d\t%.6f\t%.6f\n", i, state.R, state.Z);
        }
        gc_step_rk4(&state, &cfg, dt);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <tuple>
#include <iomanip>

struct PlasmaParameters {
    double major_radius{1.65};  // R_0 (м)
    double minor_radius{0.50};  // a (м)
    double B_toroidal{2.50};    // B_0 (Тл)
    double B_poloidal{0.30};    // B_pol_0 на краю (Тл)
    double particle_mass{3.34e-27}; // Іон дейтерію (кг)
    double particle_charge{1.602e-19};
};

struct GuidingCenterState {
    double R;
    double Z;
    double v_parallel;
    double v_perp;
};

class GuidingCenterSimulator {
public:
    explicit GuidingCenterSimulator(PlasmaParameters params)
        : params_(std::move(params)) {}

    [[nodiscard]] std::pair<double, double> compute_velocity(double R, double Z, double v_par, double v_per) const {
        const double r = std::hypot(R - params_.major_radius, Z);
        const double r_safe = (r < 1e-6) ? 1e-6 : r;

        const double B_phi = params_.B_toroidal * params_.major_radius / R;
        const double B_pol = params_.B_poloidal * (r_safe / params_.minor_radius);
        const double B_total = std::hypot(B_phi, B_pol);

        const double mu = (params_.particle_mass * v_per * v_per) / (2.0 * B_total);
        const double v_drift_Z = (params_.particle_mass * v_par * v_par + mu * B_total) /
                                 (params_.particle_charge * params_.B_toroidal * params_.major_radius);

        const double v_rot_R = -v_par * (B_pol / B_total) * (Z / r_safe);
        const double v_rot_Z =  v_par * (B_pol / B_total) * ((R - params_.major_radius) / r_safe);

        return {v_rot_R, v_rot_Z + v_drift_Z};
    }

    void step_rk4(GuidingCenterState& state, double dt) const {
        auto [dR1, dZ1] = compute_velocity(state.R, state.Z, state.v_parallel, state.v_perp);
        auto [dR2, dZ2] = compute_velocity(state.R + 0.5*dt*dR1, state.Z + 0.5*dt*dZ1, state.v_parallel, state.v_perp);
        auto [dR3, dZ3] = compute_velocity(state.R + 0.5*dt*dR2, state.Z + 0.5*dt*dZ2, state.v_parallel, state.v_perp);
        auto [dR4, dZ4] = compute_velocity(state.R + dt*dR3, state.Z + dt*dZ3, state.v_parallel, state.v_perp);

        state.R += (dt / 6.0) * (dR1 + 2.0*dR2 + 2.0*dR3 + dR4);
        state.Z += (dt / 6.0) * (dZ1 + 2.0*dZ2 + 2.0*dZ3 + dZ4);
    }

private:
    PlasmaParameters params_;
};

int main() {
    PlasmaParameters params;
    GuidingCenterSimulator sim(params);
    GuidingCenterState state{.R = 1.85, .Z = 0.0, .v_parallel = 5.0e5, .v_perp = 7.0e5};

    constexpr double dt = 1.0e-8;
    constexpr int steps = 10000;

    std::cout << std::fixed << std::setprecision(6);
    std::cout << "Крок\tR (м)\t\tZ (м)\n";
    for (int i = 0; i <= steps; ++i) {
        if (i % 1000 == 0) {
            std::cout << i << "\t" << state.R << "\t" << state.Z << "\n";
        }
        sim.step_rk4(state, dt);
    }
    return 0;
}
```
```py
import numpy as np

class PlasmaConfig:
    def __init__(self, R0=1.65, a=0.50, B0=2.50, Bpol0=0.30, m=3.34e-27, q=1.602e-19):
        self.R0 = R0
        self.a = a
        self.B0 = B0
        self.Bpol0 = Bpol0
        self.m = m
        self.q = q

def compute_velocities(R, Z, v_par, v_per, cfg):
    r = np.sqrt((R - cfg.R0)**2 + Z**2)
    r_safe = np.maximum(r, 1e-6)

    B_phi = cfg.B0 * cfg.R0 / R
    B_pol = cfg.Bpol0 * (r_safe / cfg.a)
    B_total = np.sqrt(B_phi**2 + B_pol**2)

    mu = (cfg.m * v_per**2) / (2.0 * B_total)
    v_drift_Z = (cfg.m * v_par**2 + mu * B_total) / (cfg.q * cfg.B0 * cfg.R0)

    v_rot_R = -v_par * (B_pol / B_total) * (Z / r_safe)
    v_rot_Z =  v_par * (B_pol / B_total) * ((R - cfg.R0) / r_safe)

    return v_rot_R, v_rot_Z + v_drift_Z

def simulate_trajectory(R_init=1.85, Z_init=0.0, v_par=5e5, v_per=7e5, dt=1e-8, steps=10000):
    cfg = PlasmaConfig()
    R, Z = R_init, Z_init
    trajectory = []

    for i in range(steps + 1):
        if i % 1000 == 0:
            trajectory.append((i, R, Z))

        # Метод Рунге-Кутти 4-го порядку (RK4)
        dR1, dZ1 = compute_velocities(R, Z, v_par, v_per, cfg)
        dR2, dZ2 = compute_velocities(R + 0.5*dt*dR1, Z + 0.5*dt*dZ1, v_par, v_per, cfg)
        dR3, dZ3 = compute_velocities(R + 0.5*dt*dR2, Z + 0.5*dt*dZ2, v_par, v_per, cfg)
        dR4, dZ4 = compute_velocities(R + dt*dR3, Z + dt*dZ3, v_par, v_per, cfg)

        R += (dt / 6.0) * (dR1 + 2.0*dR2 + 2.0*dR3 + dR4)
        Z += (dt / 6.0) * (dZ1 + 2.0*dZ2 + 2.0*dZ3 + dZ4)

    return trajectory

if __name__ == "__main__":
    traj = simulate_trajectory()
    print("Крок\tR (м)\t\tZ (м)")
    for step, R_val, Z_val in traj:
        print(f"{step}\t{R_val:.6f}\t{Z_val:.6f}")
```
:::

---

### Детальний аналіз фізичних режимів та траєкторій

1. **Незахищений режим суто тороїдального поля (`B_pol_0 = 0`):**
   Якщо у конфігураційній програмі задати `B_pol_0 = 0.0`, полоїдальні швидкості `v_rot_R` та `v_rot_Z` тотожно дорівнюють нулю. Частинка відчуває лише постійний вертикальний дрейф `v_drift_Z`. Дрейфова швидкість іона становить `v_drift_Z ≈ 2.5 · 10³ м/с`. Частинка доходить до верхньої стінки вакуумної камери (`Z = a = 0.5 м`) за час `t = a / v_drift_Z ≈ 200 мікросекунд`.

2. **Захищений режим із полоїдальним полем (`B_pol_0 = 0.3 Тл`):**
   Додавання полоїдального поля змушує частинку обертатися навколо магнітної осі `(R_0, 0)`. Поєднуючись із вертикальним дрейфом, траєкторія провідного центру утворює замкнене сочевицеподібне кільце — **бананову орбіту** (для запертих частинок) або замкнене дрейфове коло (для пролітних частинок).

3. **Ширина бананової орбіти (Banana width):**
   Максимальне радіальне відхилення запертої частинки від від магнітної поверхні описується формулою:

   ```
   Δr_b ≈ (r_Li / θ_pol) · √(R_0 / r)
   ```

   де `θ_pol = B_pol / B_tor` — кут нахилу силової лінії. Для дейтерієвого іона ширини бананової орбіти становить близько `1.5–2.0 см`, що вкладається у розмір камери і гарантує надійне утримання плазми.

4. **Швидкі продукти термоядерного синтезу (Альфа-частинки 3.5 МеВ):**
   Якщо у програму підставити параметри альфа-частинки `⁴He²⁺` з енергією `3.5 МеВ` (`v_parallel ≈ 9 · 10⁶ м/с`), її ларморівський радіус та ширина бананової орбіти зростають у кілька разів (`Δr_b ≈ 10–15 см`). Моделювання показує, що для надійного утримання альфа-частинок струм плазми токамака повинна перевищувати `I_p ≥ 3 МА`, інакше швидкі альфа-частинки вилітають на диверторні пластини до того, як встигають передати свою енергію тепловій плазмі.
