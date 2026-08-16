# ⚙️ Моделювання теплового розширення методом молекулярної динаміки

Для числового підтвердження зв'язку між ангармонізмом міжатомного потенціалу та макроскопічним теплом розширенням розробимо симулятор молекулярної динаміки (MD) одновимірного кристала. Програма інтегрує рівняння руху Ланжевена для одновимірного ланцюжка з `N` атомів, що взаємодіють через асиметричний потенціал Леннард-Джонса, і обчислює середню довжину ланцюжка залежно від заданої температури термостата.

---

### Фізична модель, потенціал взаємодії та термостатування

Класична молекулярна динаміка без термостата зберігає повну механічну енергію системи (NVE-мікроканонічний ансамбль), що не дозволяє підтримувати строго постійну температуру при розширенні кристала, оскільки частина кінетичної енергії неминуче переходить у потенціальну енергію деформованих міжатомних зв'язків. Щоб моделювати систему при заданій термодинамічній температурі `T` (канонічний NVT- або ізобарно-ізотермічний NPT-ансамбль), використовується стохастичний термостат Ланжевена, який імітує занурення кристала у тепловий резервуар (в'язке середовище з хаотичними молекулярними поштовхами).

Міжатомна взаємодія сусідніх частинок описується парним асиметричним потенціалом Леннард-Джонса 12-6:

```
U(r) = 4 · ε · [ (σ / r)¹² - (σ / r)⁶ ]
```

де `ε` — глибина потенціальної ями (енергія зв'язку), `σ` — характерний діаметр відштовхування електронних оболонок. Рівноважна відстань між двома атомами при `T = 0 K` відповідає мінімуму потенціалу і дорівнює `r₀ = 2¹/⁶ · σ ≈ 1.12246 · σ`.

Рівняння руху для `i`-го атома масою `m` у термостаті Ланжевена має вигляд стохастичного диференціального рівняння:

```
m · (d²x_i / dt²) = F_i^потенціал - γ · v_i + R_i(t)
```

Тут:
- `F_i^потенціал = - ∂U / ∂x_i` — консервативна міжчастинкова сила, що діє на атом з боку його сусідів;
- `- γ · v_i` — сила в'язкого тертя (з коефіцієнтом дисипації `γ`), яка відбирає кінетичну енергію у частинки;
- `R_i(t)` — випадкова гауссова сила теплового шуму, яка накачує кінетичну енергію від термостата.

Згідно з флуктуаційно-дисипаційною теоремою, амплітуда випадкових поштовхів `R_i(t)` строго узгоджена з коефіцієнтом тертя `γ` та температурою `T`:

```
⟨R_i(t)⟩ = 0
⟨R_i(t) · R_j(t')⟩ = 2 · γ · m · k_B · T · δ_ij · δ(t - t')
```

Завдяки цьому балансу між тертям та випадковими поштовхами середня кінетична енергія атомів у стаціонарному стані строго відповідає теоремі рівнорозподілу `⟨½ m v²⟩ = ½ k_B T`.

---

### Термодинамічні ансамблі та віріальне рівняння тиску

У чисельному моделюванні теплового розширення фундаментальним є вибір термодинамічного ансамблю. Термостат Ланжевена за наявності вільних границях 1D кристала автоматично створює умови ізобарно-ізотермічного ансамблю при нульовому зовнішньому тиску (`P = 0`).

Для перевірки макроскопічного тиску у системі використовують термодинамічне рівняння віріалу Клаузіуса для 1D середовища:

```
P · L = N · k_B · T + ⟨ ∑_i x_i · F_i ⟩
```

де другий член у дужках являє собою середній віріал міжчастинкових сил. При вільних граничних умовах середня сума віріалу точно врівноважує кінетичний член `N k_B T`, забезпечуючи `P = 0` та вільне розширення кристала до рівноважної довжини `L(T)`. 

У разі використання альтернативних термостатів (таких як термостат Берендсена чи Нозе — Гувера), термостатування здійснюється масштабуванням швидкостей або введенням додаткової динамічної змінної маси термостата, проте стохастичний метод Ланжевена забезпечує найбільш стійку релаксацію у малих 1D системах.

---

### Модифікований алгоритм Штьормера — Верле (Velocity Verlet)

Чисельне інтегрування рівнянь Ланжевена здійснюється двокроковим алгоритмом Штьормера — Верле з розщепленням швидкостей. На кожному кроці часу `dt`:

1. Оновлення швидкості на півкроку з урахуванням поточних сил та стохастичного поштовху:
   `v_i(t + dt/2) = v_i(t) + ½ dt · [F_i(t) - γ v_i(t) + R_i(t)] / m`
2. Оновлення координати на повний крок:
   `x_i(t + dt) = x_i(t) + dt · v_i(t + dt/2)`
3. Перерахунок консервативних сил `F_i(t + dt)` за новими координатами `x_i(t + dt)`.
4. Остаточне оновлення швидкості на другий півкроку з новим випадковим поштовхом `R_i'(t + dt)`:
   `v_i(t + dt) = v_i(t + dt/2) + ½ dt · [F_i(t + dt) - γ v_i(t + dt/2) + R_i'(t + dt)] / m`

Дисперсія випадкової сили для чисельного алгоритму дорівнює `σ_R = √(2 · γ · m · k_B · T / dt)`.

---

### Програмна реалізація

:::tabs
```c
/* thermal_expansion_sim.c - Симуляція теплового розширення 1D кристала (C11) */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define N_ATOMS 50
#define DT 0.002
#define TOTAL_STEPS 200000
#define THERMALIZATION_STEPS 50000

typedef struct {
    double x[N_ATOMS];
    double v[N_ATOMS];
    double f[N_ATOMS];
    double mass;
    double epsilon;
    double sigma;
    double gamma;
} Crystal;

/* Генератор нормального розподілу Бокса-Мюллера */
double rand_gaussian(double stddev) {
    double u1 = (double)rand() / RAND_MAX;
    double u2 = (double)rand() / RAND_MAX;
    if (u1 < 1e-12) u1 = 1e-12;
    return stddev * sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2);
}

void compute_forces(Crystal *c) {
    for (int i = 0; i < N_ATOMS; i++) c->f[i] = 0.0;
    
    /* Сили взаємодії між сусідніми атомами */
    for (int i = 0; i < N_ATOMS - 1; i++) {
        double r = c->x[i+1] - c->x[i];
        if (r < 0.1) r = 0.1;
        double sr = c->sigma / r;
        double sr6 = sr * sr * sr * sr * sr * sr;
        double sr12 = sr6 * sr6;
        /* F = -dU/dr = 24*eps/r * (2*(sigma/r)^12 - (sigma/r)^6) */
        double force = (24.0 * c->epsilon / r) * (2.0 * sr12 - sr6);
        c->f[i] -= force;
        c->f[i+1] += force;
    }
}

double simulate_temperature(double target_temp) {
    Crystal c;
    c.mass = 1.0;
    c.epsilon = 1.0;
    c.sigma = 1.0;
    c.gamma = 1.0;
    
    double r0 = pow(2.0, 1.0 / 6.0) * c.sigma;
    for (int i = 0; i < N_ATOMS; i++) {
        c.x[i] = i * r0;
        c.v[i] = 0.0;
    }
    
    double noise_std = sqrt(2.0 * c.gamma * c.mass * target_temp / DT);
    compute_forces(&c);
    
    double sum_length = 0.0;
    int count = 0;
    
    for (int step = 0; step < TOTAL_STEPS; step++) {
        /* Velocity Verlet 1-й крок */
        for (int i = 0; i < N_ATOMS; i++) {
            c.v[i] += 0.5 * DT * (c.f[i] - c.gamma * c.v[i] + rand_gaussian(noise_std)) / c.mass;
            c.x[i] += DT * c.v[i];
        }
        
        compute_forces(&c);
        
        /* Velocity Verlet 2-й крок */
        for (int i = 0; i < N_ATOMS; i++) {
            c.v[i] += 0.5 * DT * (c.f[i] - c.gamma * c.v[i] + rand_gaussian(noise_std)) / c.mass;
        }
        
        if (step >= THERMALIZATION_STEPS) {
            double current_length = c.x[N_ATOMS - 1] - c.x[0];
            sum_length += current_length;
            count++;
        }
    }
    
    return sum_length / count;
}

int main(void) {
    srand(12345);
    printf("Temperature,Average_Length,Delta_L_Percent\n");
    
    double temps[] = {0.01, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30};
    int num_t = sizeof(temps) / sizeof(temps[0]);
    
    double L0 = (N_ATOMS - 1) * pow(2.0, 1.0 / 6.0);
    
    for (int i = 0; i < num_t; i++) {
        double avg_l = simulate_temperature(temps[i]);
        double delta_pct = ((avg_l - L0) / L0) * 100.0;
        printf("%.2f,%.5f,%.3f%%\n", temps[i], avg_l, delta_pct);
    }
    
    return 0;
}
```
```cpp
// thermal_expansion_sim.cpp — Моделювання теплового розширення 1D кристала (C++20)
#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <iomanip>
#include <numbers>

class CrystalSimulator {
public:
    struct Config {
        std::size_t num_atoms{50};
        double dt{0.002};
        std::size_t total_steps{200000};
        std::size_t thermalization_steps{50000};
        double mass{1.0};
        double epsilon{1.0};
        double sigma{1.0};
        double gamma{1.0};
    };

    explicit CrystalSimulator(Config cfg) 
        : cfg_(cfg),
          r0_(std::pow(2.0, 1.0 / 6.0) * cfg_.sigma),
          positions_(cfg_.num_atoms),
          velocities_(cfg_.num_atoms, 0.0),
          forces_(cfg_.num_atoms, 0.0),
          gen_(12345)
    {
        for (std::size_t i = 0; i < cfg_.num_atoms; ++i) {
            positions_[i] = i * r0_;
        }
    }

    double run_temperature(double target_temp) {
        std::normal_distribution<double> gaussian{0.0, 1.0};
        double noise_std = std::sqrt(2.0 * cfg_.gamma * cfg_.mass * target_temp / cfg_.dt);

        compute_forces();

        double sum_length = 0.0;
        std::size_t count = 0;

        for (std::size_t step = 0; step < cfg_.total_steps; ++step) {
            for (std::size_t i = 0; i < cfg_.num_atoms; ++i) {
                double R_i = noise_std * gaussian(gen_);
                velocities_[i] += 0.5 * cfg_.dt * (forces_[i] - cfg_.gamma * velocities_[i] + R_i) / cfg_.mass;
                positions_[i] += cfg_.dt * velocities_[i];
            }

            compute_forces();

            for (std::size_t i = 0; i < cfg_.num_atoms; ++i) {
                double R_i = noise_std * gaussian(gen_);
                velocities_[i] += 0.5 * cfg_.dt * (forces_[i] - cfg_.gamma * velocities_[i] + R_i) / cfg_.mass;
            }

            if (step >= cfg_.thermalization_steps) {
                double current_len = positions_.back() - positions_.front();
                sum_length += current_len;
                count++;
            }
        }

        return sum_length / static_cast<double>(count);
    }

    [[nodiscard]] double initial_length() const noexcept {
        return (cfg_.num_atoms - 1) * r0_;
    }

private:
    void compute_forces() {
        std::fill(forces_.begin(), forces_.end(), 0.0);
        for (std::size_t i = 0; i < cfg_.num_atoms - 1; ++i) {
            double r = positions_[i+1] - positions_[i];
            if (r < 0.1) r = 0.1;
            double sr = cfg_.sigma / r;
            double sr6 = std::pow(sr, 6);
            double sr12 = sr6 * sr6;
            double force = (24.0 * cfg_.epsilon / r) * (2.0 * sr12 - sr6);
            forces_[i] -= force;
            forces_[i+1] += force;
        }
    }

    Config cfg_;
    double r0_;
    std::vector<double> positions_;
    std::vector<double> velocities_;
    std::vector<double> forces_;
    std::mt19937 gen_;
};

int main() {
    CrystalSimulator::Config cfg;
    CrystalSimulator sim(cfg);
    double L0 = sim.initial_length();

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Т, К (безрозмірні) | Середня довжина | ΔL / L₀ (%)\n";
    std::cout << "-----------------------------------------------\n";

    const std::vector<double> temperatures{0.01, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30};
    for (double T : temperatures) {
        double avg_l = sim.run_temperature(T);
        double pct = ((avg_l - L0) / L0) * 100.0;
        std::cout << "      " << T << "        |    " << avg_l << "     |   +" << pct << " %\n";
    }

    return 0;
}
```
```python
# thermal_expansion_sim.py — Python чисельне моделювання
import numpy as np

def simulate_lj_chain(temp, num_atoms=50, dt=0.002, steps=200000, therm_steps=50000):
    r0 = 2.0 ** (1.0 / 6.0)
    x = np.arange(num_atoms) * r0
    v = np.zeros(num_atoms)
    gamma = 1.0
    mass = 1.0
    noise_std = np.sqrt(2.0 * gamma * mass * temp / dt)
    
    def get_forces(pos):
        f = np.zeros(num_atoms)
        dr = pos[1:] - pos[:-1]
        dr = np.maximum(dr, 0.1)
        sr6 = (1.0 / dr) ** 6
        force = (24.0 / dr) * (2.0 * sr6**2 - sr6)
        f[:-1] -= force
        f[1:] += force
        return f

    f = get_forces(x)
    lengths = []
    
    for step in range(steps):
        R = np.random.normal(0, noise_std, num_atoms)
        v += 0.5 * dt * (f - gamma * v + R) / mass
        x += dt * v
        f = get_forces(x)
        R = np.random.normal(0, noise_std, num_atoms)
        v += 0.5 * dt * (f - gamma * v + R) / mass
        
        if step >= therm_steps:
            lengths.append(x[-1] - x[0])
            
    return np.mean(lengths)

if __name__ == "__main__":
    L0 = (50 - 1) * (2.0 ** (1.0 / 6.0))
    print(f"L0 (0 K) = {L0:.4f}")
    for T in [0.01, 0.05, 0.10, 0.20, 0.30]:
        L_avg = simulate_lj_chain(T)
        delta_pct = ((L_avg - L0) / L0) * 100.0;
        print(f"T = {T:.2f} -> L = {L_avg:.4f} (+{delta_pct:.3f}%)")
```
:::

---

### Збирання, виконання та аналіз результатів

Для компіляції та запуску розробленого C та C++ коду у середовищі Linux чи Windows (GCC / Clang) використовуйте наступні команди:

```bash
# Компіляція C версії
gcc -O3 -std=c11 thermal_expansion_sim.c -o sim_c -lm
./sim_c

# Компіляція C++20 версії
g++ -O3 -std=c++20 thermal_expansion_sim.cpp -o sim_cpp
./sim_cpp
```

Залежність середньої довжини ланцюжка `L(T)` від температури показує чітке зростання, практично лінійне при низьких та помірних температурах `T ≤ 0.20`, що узгоджується з теорією першого порядку `ΔL ∝ T`. 

При вищих температурах (`T > 0.25`) спостерігається нелінійне прискорення розширення, викликане внеском квартечного члену `f x⁴` та наближенням системи до температури плавлення 1D кристала.

---

### Основні інженерно-обчислювальні пастки при розробці симулятора

1. **Вибір кроку інтегрування `DT`:**
   Крок `DT` повинен бути у 50–100 разів меншим за найменший період власних коливань решітки `τ_vib ≈ 2π √(m / c) ≈ 0.2`. Якщо обрати `DT > 0.005`, чисельна похибка інтегрування призведе до катастрофічного накопичення енергії («вибуху» симулятора), при якому атоми розлетяться на нескінченність.

2. **Забезпечення вільних граничних умов:**
   Для безпосереднього спостереження розширення кристал повинен мати вільні кінці (крайні атоми `x[0]` та `x[N-1]` не затиснуті в жорстких лещатах і рухаються під дією односторонніх сил). Якщо використати періодичні граничні умови з фіксованим об'ємом комірки, кристал не зможе розширюватися, а замість розширення в ньому виникне макроскопічний внутрішній тиск `P(T)`.

3. **Тривалість релаксації `THERMALIZATION_STEPS`:**
   Початковий стан (ідеальна решітка з `v_i = 0`) є нерівноважним для `T > 0`. Перші 50 000 кроків система витрачає на перерозподіл енергії між кінетичними та потенціальними ступенями вільностей. Усереднення довжини `L(T)` слід розпочинати строго після досягнення термодинамічної рівноваги, інакше початкові перехідні коливання спотворять обчислене значення КТР.

4. **Ефекти малого числа частинок (Finite-size scaling):**
   У 1D ланцюжку з малою кількістю атомів (`N < 10`) флуктуації довжини порівнянні з самим теплом розширенням. Для отримання гладких лінійних залежностей необхідно використовувати `N ≥ 50` та проводити усереднення по не менш ніж 150 000 рівноважних конфігурацій.

5. **Генерація псевдовипадкових чисел:**
   У багатопотокових симуляціях молекулярної динаміки стандартний генератор `rand()` мови C може викликати блокування потоків через спільний внутрішній стан. Рекомендується використовувати сучасні генератори C++11 `std::mt19937` з індивідуальними зернами (*seeds*) для кожного потоку.
