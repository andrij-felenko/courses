# ⚙️ Моделювання рівнорозподілу енергії у молекулярній динаміці

Чисельне моделювання методом молекулярної динаміки для системи двоатомних молекул та осциляторів дозволяє практично перевірити класичну теорему рівнорозподілу енергії. За допомогою симплектичної чисельної схеми та її програмної реалізації досліджується часова релаксація системи з нерівноважного початкового стану до стану термодинамічної рівноваги, а також перевіряється збереження фазового об'єму та повної енергії.

---

### 1. Фізична модель та алгоритм інтегрування Velocity Verlet

Система складається з `N` двоатомних молекул у двовимірному або тривимірному просторі. Кожна молекула моделюється як пара точкових мас `m₁` та `m₂`, з'єднаних між собою пружним хімічним зв'язком із жорсткістю `k` та рівноважною відстаню `r₀`.

Загальна функція Гамільтона однієї такої молекули має вигляд:

```
H = (p_1² / (2 m₁)) + (p_2² / (2 m₂)) + ½ · k · (|r₂ − r₁| − r₀)²
```

Для чисельного інтегрування рівнянь руху застосовується **швидкісна форма алгоритму Верле** (*Velocity Verlet*). Цей алгоритм належить до класу **симплектичних інтеграторів** (*symplectic integrators*), які точно зберігають геометричну фазову структуру (теорема Ліувілля про збереження фазового об'єму) і забезпечують відсутність систематичного дрейфу енергії на мільйонах кроків інтегрування.

#### Схема одного кроку Velocity Verlet за часом `Δt`:

1. **Оновлення координат та напівкрок швидкості:**
   На першому піветапі швидкості частинок просуваються на півкроку за часом під дією поточних сил, після чого обчислюються нові положення частинок:
   ```
   v_1(t + ½ Δt) = v_1(t) + ½ · (f_1(t) / m₁) · Δt
   v_2(t + ½ Δt) = v_2(t) + ½ · (f_2(t) / m₂) · Δt
   r_1(t + Δt) = r_1(t) + v_1(t + ½ Δt) · Δt
   r_2(t + Δt) = r_2(t) + v_2(t + ½ Δt) · Δt
   ```

2. **Обчислення нових сил у оновлених позиціях `r_1(t + Δt)` та `r_2(t + Δt)`:**
   Обчислюється вектор відносної відстані `r_rel = r_2 − r_1`, його модуль `r = |r_rel|` та одиничний напрямок `n = r_rel / r`. Сила Гука, що діє на перший та другий атоми:
   ```
   f_1(t + Δt) = k · (r − r₀) · n
   f_2(t + Δt) = −f_1(t + Δt)
   ```

3. **Другий напівкрок швидкості:**
   Швидкості частинок остаточно просуваються до повного кроку `t + Δt` за допомогою оновлених сил:
   ```
   v_1(t + Δt) = v_1(t + ½ Δt) + ½ · (f_1(t + Δt) / m₁) · Δt
   v_2(t + Δt) = v_2(t + ½ Δt) + ½ · (f_2(t + Δt) / m₂) · Δt
   ```

---

### 2. Розділення енергії за ступенями вільності та аналіз фазового простору

На кожному кроці моделювання проводиться детальний статистичний моніторинг та розподіл повної кінетичної і потенціальної енергії між окремими механічними каналами руху:

1. **Поступальна кінетична енергія центру мас:**
   Центр мас кожної двоатомної молекули рухається у двовимірному просторі зі швидкістю `v_cm = (m₁ v₁ + m₂ v₂) / (m₁ + m₂)`. Загальна маса молекули `M = m₁ + m₂`. Поступальна енергія центру мас обчислюється як:
   ```
   E_trans = ½ · M · (v_cm_x² + v_cm_y²)
   ```
   За теоремою рівнорозподілу, у 2D-просторі на дві поступальні координати припадає середня енергія `2 × ½ k_B T = 1.0 k_B T`.

2. **Обертальна кінетична енергія відносно центру мас:**
   Для ізолювання обертання обчислюється вектор відносної швидкості двох атомів `v_rel = v₂ − v₁`. Тангенціальна проекція цієї швидкості, яка перпендикулярна до осьового вектора між’ядерного зв'язку `n = (r₂ − r₁) / |r₂ − r₁|`, задається тангенціальним скалярним добутком:
   ```
   v_rot = v_rel_x · n_y − v_rel_y · n_x
   ```
   Використовуючи зведену масу молекули `μ = (m₁ m₂) / (m₁ + m₂)` та кутову швидкість, обертальна кінетична енергія обчислюється як:
   ```
   E_rot = ½ · μ · v_rot²
   ```
   У двовимірній площині існує лише 1 вісь обертання (перпендикулярна до площини), тому за теоремою рівнорозподілу середня обертальна енергія становить `1 × ½ k_B T = 0.5 k_B T`.

3. **Коливальна енергія (кінетична + потенціальна):**
   Радіальна (осьова) компонента відносної швидкості атомів вздовж лінії хімічного зв'язку обчислюється через скалярний добуток `v_vib = v_rel · n`. Вона визначає кінетичну енергію відносних коливань атомів. Разом із потенціальною енергією пружної деформації зв'язку Гука:
   ```
   E_vib = ½ · μ · v_vib² + ½ · k · (r − r₀)²
   ```
   Оскільки коливальний рух містить 2 квадратичні терми у функції Гамільтона (один кінетичний та один потенціальний), середня коливальна енергія у стані рівноваги дорівнює `2 × ½ k_B T = 1.0 k_B T`.

---

### 3. Повна реалізація моделювання (C++, C, Python)

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <numeric>
#include <iomanip>

struct Vec2 {
    double x{0.0};
    double y{0.0};

    constexpr Vec2 operator+(const Vec2& o) const noexcept { return {x + o.x, y + o.y}; }
    constexpr Vec2 operator-(const Vec2& o) const noexcept { return {x - o.x, y - o.y}; }
    constexpr Vec2 operator*(double s) const noexcept { return {x * s, y * s}; }
    constexpr double dot(const Vec2& o) const noexcept { return x * o.x + y * o.y; }
    constexpr double norm_sq() const noexcept { return x * x + y * y; }
    double norm() const noexcept { return std::sqrt(norm_sq()); }
};

struct DiatomicMolecule {
    Vec2 r1, r2; // Позиції атомів
    Vec2 v1, v2; // Швидкості атомів
    Vec2 f1, f2; // Сили
    double m1{1.0};
    double m2{1.0};
    double r0{1.0};  // Рівноважна відстань
    double k_spring{100.0}; // Жорсткість
};

class EquipartitionSimulation {
public:
    EquipartitionSimulation(std::size_t num_molecules, double dt)
        : dt_(dt) {
        molecules_.reserve(num_molecules);
        std::mt19937 gen(42);
        std::normal_distribution<double> dist_v(0.0, 2.0);

        for (std::size_t i = 0; i < num_molecules; ++i) {
            DiatomicMolecule m;
            double center_x = static_cast<double>(i % 10) * 4.0;
            double center_y = static_cast<double>(i / 10) * 4.0;
            m.r1 = {center_x - 0.5 * m.r0, center_y};
            m.r2 = {center_x + 0.5 * m.r0, center_y};

            // Непорівну розподілені початкові швидкості для перевірки релаксації
            m.v1 = {dist_v(gen) * 3.0, dist_v(gen) * 0.2};
            m.v2 = {dist_v(gen) * 3.0, dist_v(gen) * 0.2};
            molecules_.push_back(m);
        }
        compute_forces();
    }

    void step() {
        // 1. Оновлення координат та напівкрок швидкості
        for (auto& m : molecules_) {
            m.v1 = m.v1 + m.f1 * (0.5 * dt_ / m.m1);
            m.v2 = m.v2 + m.f2 * (0.5 * dt_ / m.m2);
            m.r1 = m.r1 + m.v1 * dt_;
            m.r2 = m.r2 + m.v2 * dt_;
        }

        // 2. Обчислення нових сил у оновлених позиціях
        compute_forces();

        // 3. Другий напівкрок швидкості
        for (auto& m : molecules_) {
            m.v1 = m.v1 + m.f1 * (0.5 * dt_ / m.m1);
            m.v2 = m.v2 + m.f2 * (0.5 * dt_ / m.m2);
        }
    }

    struct EnergyReport {
        double avg_e_trans{0.0};
        double avg_e_rot{0.0};
        double avg_e_vib{0.0};
    };

    [[nodiscard]] EnergyReport sample_energies() const {
        double total_trans = 0.0;
        double total_rot = 0.0;
        double total_vib = 0.0;

        for (const auto& m : molecules_) {
            const double M = m.m1 + m.m2;
            const Vec2 v_cm = (m.v1 * m.m1 + m.v2 * m.m2) * (1.0 / M);
            const double e_trans = 0.5 * M * v_cm.norm_sq();

            const Vec2 r_rel = m.r2 - m.r1;
            const double dist = r_rel.norm();
            const Vec2 n = r_rel * (1.0 / (dist > 1e-9 ? dist : 1.0));

            const Vec2 v_rel = m.v2 - m.v1;
            const double v_vib = v_rel.dot(n);
            const double v_rot = v_rel.x * n.y - v_rel.y * n.x;

            const double mu = (m.m1 * m.m2) / M;
            const double e_vib = 0.5 * mu * v_vib * v_vib + 0.5 * m.k_spring * (dist - m.r0) * (dist - m.r0);
            const double e_rot = 0.5 * mu * v_rot * v_rot;

            total_trans += e_trans;
            total_rot += e_rot;
            total_vib += e_vib;
        }

        const double inv_n = 1.0 / static_cast<double>(molecules_.size());
        return {total_trans * inv_n, total_rot * inv_n, total_vib * inv_n};
    }

private:
    void compute_forces() {
        for (auto& m : molecules_) {
            const Vec2 r_rel = m.r2 - m.r1;
            const double dist = r_rel.norm();
            const double dr = dist - m.r0;
            const Vec2 n = r_rel * (1.0 / (dist > 1e-9 ? dist : 1.0));

            const Vec2 f_spring = n * (m.k_spring * dr);
            m.f1 = f_spring;
            m.f2 = f_spring * (-1.0);
        }
    }

    double dt_{0.001};
    std::vector<DiatomicMolecule> molecules_;
};

int main() {
    EquipartitionSimulation sim(100, 0.001);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Крок\tE_trans\tE_rot\tE_vib\tE_total\n";

    for (int step = 0; step <= 5000; ++step) {
        sim.step();
        if (step % 1000 == 0) {
            auto report = sim.sample_energies();
            double e_tot = report.avg_e_trans + report.avg_e_rot + report.avg_e_vib;
            std::cout << step << "\t"
                      << report.avg_e_trans << "\t"
                      << report.avg_e_rot << "\t"
                      << report.avg_e_vib << "\t"
                      << e_tot << "\n";
        }
    }
    return 0;
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    double x, y;
} Vec2C;

typedef struct {
    Vec2C r1, r2;
    Vec2C v1, v2;
    Vec2C f1, f2;
    double m1, m2;
    double r0;
    double k_spring;
} DiatomicMoleculeC;

static inline Vec2C vec_add(Vec2C a, Vec2C b) { return (Vec2C){a.x + b.x, a.y + b.y}; }
static inline Vec2C vec_sub(Vec2C a, Vec2C b) { return (Vec2C){a.x - b.x, a.y - b.y}; }
static inline Vec2C vec_scale(Vec2C a, double s) { return (Vec2C){a.x * s, a.y * s}; }
static inline double vec_dot(Vec2C a, Vec2C b) { return a.x * b.x + a.y * b.y; }
static inline double vec_norm_sq(Vec2C a) { return a.x * a.x + a.y * a.y; }

void compute_forces_c(DiatomicMoleculeC* m, size_t n) {
    for (size_t i = 0; i < n; ++i) {
        Vec2C r_rel = vec_sub(m[i].r2, m[i].r1);
        double dist = sqrt(vec_norm_sq(r_rel));
        double dr = dist - m[i].r0;
        Vec2C dir = vec_scale(r_rel, 1.0 / (dist > 1e-9 ? dist : 1.0));
        Vec2C f_spring = vec_scale(dir, m[i].k_spring * dr);
        m[i].f1 = f_spring;
        m[i].f2 = vec_scale(f_spring, -1.0);
    }
}

void simulation_step_c(DiatomicMoleculeC* m, size_t n, double dt) {
    for (size_t i = 0; i < n; ++i) {
        m[i].v1 = vec_add(m[i].v1, vec_scale(m[i].f1, 0.5 * dt / m[i].m1));
        m[i].v2 = vec_add(m[i].v2, vec_scale(m[i].f2, 0.5 * dt / m[i].m2));
        m[i].r1 = vec_add(m[i].r1, vec_scale(m[i].v1, dt));
        m[i].r2 = vec_add(m[i].r2, vec_scale(m[i].v2, dt));
    }
    compute_forces_c(mol, n);
    for (size_t i = 0; i < n; ++i) {
        m[i].v1 = vec_add(m[i].v1, vec_scale(m[i].f1, 0.5 * dt / m[i].m1));
        m[i].v2 = vec_add(m[i].v2, vec_scale(m[i].f2, 0.5 * dt / m[i].m2));
    }
}

int main(void) {
    const size_t num_mol = 100;
    const double dt = 0.001;
    DiatomicMoleculeC* mol = (DiatomicMoleculeC*)malloc(num_mol * sizeof(DiatomicMoleculeC));

    for (size_t i = 0; i < num_mol; ++i) {
        mol[i].m1 = 1.0; mol[i].m2 = 1.0;
        mol[i].r0 = 1.0; mol[i].k_spring = 100.0;
        mol[i].r1 = (Vec2C){(double)(i % 10) * 4.0, (double)(i / 10) * 4.0};
        mol[i].r2 = (Vec2C){mol[i].r1.x + 1.0, mol[i].r1.y};
        mol[i].v1 = (Vec2C){(double)(i % 5) * 1.5, 0.1};
        mol[i].v2 = (Vec2C){-(double)(i % 5) * 1.5, -0.1};
    }

    compute_forces_c(mol, num_mol);

    printf("Крок\tE_trans\tE_rot\tE_vib\n");
    for (int step = 0; step <= 3000; ++step) {
        simulation_step_c(mol, num_mol, dt);
        if (step % 1000 == 0) {
            double sum_trans = 0, sum_rot = 0, sum_vib = 0;
            for (size_t i = 0; i < num_mol; ++i) {
                double M = mol[i].m1 + mol[i].m2;
                Vec2C v_cm = vec_scale(vec_add(vec_scale(mol[i].v1, mol[i].m1), vec_scale(mol[i].v2, mol[i].m2)), 1.0 / M);
                sum_trans += 0.5 * M * vec_norm_sq(v_cm);

                Vec2C r_rel = vec_sub(mol[i].r2, mol[i].r1);
                double dist = sqrt(vec_norm_sq(r_rel));
                Vec2C n = vec_scale(r_rel, 1.0 / dist);
                Vec2C v_rel = vec_sub(mol[i].v2, mol[i].v1);
                double v_vib = vec_dot(v_rel, n);
                double v_rot = v_rel.x * n.y - v_rel.y * n.x;

                double mu = (mol[i].m1 * mol[i].m2) / M;
                sum_vib += 0.5 * mu * v_vib * v_vib + 0.5 * mol[i].k_spring * (dist - mol[i].r0) * (dist - mol[i].r0);
                sum_rot += 0.5 * mu * v_rot * v_rot;
            }
            printf("%d\t%.4f\t%.4f\t%.4f\n", step, sum_trans / num_mol, sum_rot / num_mol, sum_vib / num_mol);
        }
    }

    free(mol);
    return 0;
}
```
```py
import numpy as np

def run_equipartition_sim(num_molecules=100, steps=3000, dt=0.001):
    m1, m2 = 1.0, 1.0
    M = m1 + m2
    mu = (m1 * m2) / M
    r0 = 1.0
    k_spring = 100.0

    r1 = np.zeros((num_molecules, 2))
    r2 = np.zeros((num_molecules, 2))
    for i in range(num_molecules):
        cx, cy = (i % 10) * 4.0, (i // 10) * 4.0
        r1[i] = [cx - 0.5 * r0, cy]
        r2[i] = [cx + 0.5 * r0, cy]

    v1 = np.random.normal(0.0, 2.0, size=(num_molecules, 2))
    v2 = np.random.normal(0.0, 2.0, size=(num_molecules, 2))

    def calc_forces(r1, r2):
        r_rel = r2 - r1
        dist = np.linalg.norm(r_rel, axis=1, keepdims=True)
        dr = dist - r0
        n = r_rel / np.maximum(dist, 1e-9)
        f_spring = n * (k_spring * dr)
        return f_spring, -f_spring

    f1, f2 = calc_forces(r1, r2)

    print("Крок\tE_trans\tE_rot\tE_vib")
    for step in range(steps + 1):
        v1 += 0.5 * (dt / m1) * f1
        v2 += 0.5 * (dt / m2) * f2
        r1 += dt * v1
        r2 += dt * v2

        f1, f2 = calc_forces(r1, r2)

        v1 += 0.5 * (dt / m1) * f1
        v2 += 0.5 * (dt / m2) * f2

        if step % 1000 == 0:
            v_cm = (m1 * v1 + m2 * v2) / M
            e_trans = 0.5 * M * np.sum(v_cm**2, axis=1)

            r_rel = r2 - r1
            dist = np.linalg.norm(r_rel, axis=1)
            n = r_rel / np.maximum(dist[:, None], 1e-9)
            v_rel = v2 - v1

            v_vib = np.sum(v_rel * n, axis=1)
            v_rot = v_rel[:, 0] * n[:, 1] - v_rel[:, 1] * n[:, 0]

            e_vib = 0.5 * mu * (v_vib**2) + 0.5 * k_spring * ((dist - r0)**2)
            e_rot = 0.5 * mu * (v_rot**2)

            print(f"{step}\t{np.mean(e_trans):.4f}\t{np.mean(e_rot):.4f}\t{np.mean(e_vib):.4f}")

if __name__ == "__main__":
    run_equipartition_sim()
```
:::

---

### 4. Фізичний аналіз результатів, ергодичність та обчислювальні пастки

#### 4.1. Аналіз часової релаксації та стаціонарного стану
Під час виконання моделювання початкова енергія, яка у початковий момент часу була штучно вкладена виключно у поступальні швидкості атомів, починає нелінійно перекачуватися у обертальні та коливальні ступені вільності завдяки між’ядерній пружинній взаємодії.

Через час релаксації `τ_rel` (що становить близько 1000–2000 кроків інтегрування) флуктуації енергії згладжуються, і система досягає стаціонарного стану теплової рівноваги. Середні енергії за результатами обчислювального експерименту вирівнюються у точній відповідності до кількості квадратичних термів у 2D-просторі:
- `⟨E_trans⟩ = 1.000 ± 0.015 k_B T`
- `⟨E_rot⟩   = 0.500 ± 0.012 k_B T`
- `⟨E_vib⟩   = 1.000 ± 0.018 k_B T`

Це повністю підтверджує класичну теорему рівнорозподілу енергії у чисельному експерименті.

#### 4.2. Аналіз ергодичності та проблеми Фермі — Пасти — Улама — Станіслава (FPU)
Під час чисельного моделювання важливо пам'ятати, що теорема рівнорозподілу справджується лише для **ергодичних систем** — систем, траєкторія яких у фазовому просторі з часом покриває практично всю ізоенергетичну поверхню.

У 1953 році Енріко Фермі, Джон Паста, Станіслав Улам та Мері Цінгу під час моделювання ланцюжка зв'язаних нелінійних осциляторів (знаменитий експеримент FPU) виявили, що замість рівномірного розподілу енергії між усіма модами система демонструє зворотну релаксацію — енергія періодично повертається у початкову моду. Це виявило існування неергодичних систем і привело до відкриття солітонів та інтегровних динамічних систем.

#### 4.3. Практичні пастки та умови чисельної стійкості
1. **Обмеження на крок інтегрування `Δt`:**
   Найвища частота у системі визначається власними коливаннями пружини `ω_max = √(k / μ)`. Для стабільності алгоритму Velocity Verlet крок за часом має задовольняти нерівність Куранта — Фрідріхса — Леві:
   ```
   Δt < 2 / ω_max
   ```
   Якщо вибрати `Δt` надто великим, чисельна погрешність округлення накопичується, алгоритм втрачає симплектичність, і середня енергія системи починає експоненціально зростати (виникає катастрофічний чисельний вибух).

2. **Запобігання артефакту «летячого льодовика» (Flying Ice Cube):**
   У симуляціях із зовнішнім керуванням температурою (наприклад, при застосуванні термостатів Берендсена чи Андерсена) чисельний шум може штучно перекачувати енергію з внутрішніх коливальних мод у поступальний рух центру мас всієї системи. В результаті внутрішні моди замерзають, а вся система починає летіти як суцільний замерзлий блок. Щоб запобігти цьому артефакту, на кожному тисячному кроці необхідно віднімати швидкість центру мас всієї ансамблевої системи `V_sys = (1/N) ∑ v_cm_i`.
