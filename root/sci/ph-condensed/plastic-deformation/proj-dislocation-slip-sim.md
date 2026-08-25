# ⚙️ Моделювання фактора Шміда та деформаційного зміцнення полікристалу

Обчислювальна фізика твердого тіла та чисельне моделювання механізмів кристалічної пластичності охоплює алгоритм обчислення фактора Шміда для 12 систем ковзання граньоцентрованої кубічної (ГЦК) ґратки `{111}<110>`, визначення первинної та вторинних систем ковзання при довільній кристалографічній орієнтації вісі розтягу, а також чисельну реалізацію моделі деформаційного зміцнення Кокса — Мекінга на основі диференціального рівняння еволюції щільності дислокацій.

---

### 1. Фізична та алгоритмічна модель розрахунку систем ковзання

У кристалфізиці орієнтація кристаліта відносно зовнішньої осі навантаження задається напрямним вектором розтягу `n = (n_x, n_y, n_z)` у декартовій кристалографічній системі координат. Дія макроскопічного розтягувального напруження `σ` викликає у кожній із 12 кристалографічних систем ковзання ГЦК-структури проектоване зсувне напруження `τ_k = σ · m_k`, де `m_k` — фактор Шміда `k`-ї системи.

#### Структура 12 ГЦК систем ковзання `{111}<110>`

Граньоцентрована кубічна ґратка має чотири октаедричні площини найщільнішої упаковки атомів `{111}`. У кожній із цих площин лежать три напрямки найщільнішої упаковки `<110>`, що утворює 12 незалежних систем ковзання:

1. **Площина (1, 1, 1):** напрямки `[0, 1, -1]`, `[1, 0, -1]`, `[1, -1, 0]`.
2. **Площина (-1, 1, 1):** напрямки `[0, 1, -1]`, `[1, 0, 1]`, `[1, 1, 0]`.
3. **Площина (1, -1, 1):** напрямки `[0, 1, 1]`, `[1, 0, -1]`, `[1, 1, 0]`.
4. **Площина (1, 1, -1):** напрямки `[0, 1, 1]`, `[1, 0, 1]`, `[1, -1, 0]`.

Для кожного вектора нормалі `n_s` та вектора ковзання `s` алгоритм виконує такі математичні обчислення:

- **Нормалізація векторів у просторі R³:** вектор нормалі `n_s` та вектор напрямку ковзання `s` приводяться до одиничної довжини: `n_s_norm = n_s / |n_s|`, `s_norm = s / |s|`. Для октаедричної площини `(1,1,1)` довжина нормалі дорівнює `|n_s| = √(1² + 1² + 1²) = √3`. Для напрямку ковзання `[0,1,-1]` довжина вектора дорівнює `|s| = √(0² + 1² + (-1)²) = √2`.
- **Скалярне множення та обчислення косинусів кутів:** обчислюється абсолютне значення косинуса кута `φ` між напрямком розтягу `n` та нормаллю `n_s`: `cos φ = |n · n_s_norm|`. Аналогічно обчислюється косинус кута `λ` між напрямком розтягу `n` та напрямком ковзання `s`: `cos λ = |n · s_norm|`.
- **Розрахунок фактора Шміда:** для кожної системи `k` розраховується добуток `m_k = cos φ · cos λ`.
- **Вибір активної системи ковзання:** серед усіх 12 систем визначається максимальне значення `m_max = max(m_k)`. Система з `m_max` є первинно активною системою ковзання, яка першою досягає критичного зсувного напруження `τ_crss`.

---

### 2. Динаміка щільності дислокацій та феноменологічна модель Кокса — Мекінга

Для прогнозування зростання опору пластичному деформуванню (деформаційного зміцнення) у моделлю використовується феноменологічне диференціальне рівняння еволюції щільності дислокацій Кокса — Мекінга.

Зміна щільності дислокацій `ρ` з ростом пластичної деформації `ε_p` описується балансом двох фізичних процесів:

```
dρ / dε_p = k₁ · √ρ - k₂ · ρ
```

- **Акумуляція та розмноження дислокацій (`k₁ · √ρ`):** під дією зовнішнього напруження джерела Франка — Рида генерально випромінюють нові дислокаційні петлі. Дислокації рухаються у площинах ковзання та застрягають на лісі дислокацій і точкових бар'єрах. Коефіцієнт `k₁` виражає інтенсивність розмноження дислокацій на одиницю пластичної деформації (для міді `k₁ ≈ 4.5·10⁸ м⁻¹`).
- **Динамічне повернення та анігіляція (`k₂ · ρ`):** при високій щільності дислокацій відбувається анігіляція протилежно орієнтованих дислокацій шляхом поперечного ковзання ґвинтових компонент та термічно активованого переповзання крайових компонент. Безрозмірний коефіцієнт `k₂` відповідає за швидкість самовідновлення кристалічної ґратки (для міді `k₂ ≈ 12.0`).

На кожному кроці за пластичною деформацією `Δε_p` чисельне інтегрування здійснюється методом Ейлера:

```
ρ_{i+1} = ρ_i + (k₁ · √ρ_i - k₂ · ρ_i) · Δε_p
```

Зсувне напруження `τ` на кожному кроці розраховується за фундаментальним рівнянням Тейлора:

```
τ(ρ) = τ₀ + α · G · b · √ρ
```

а макроскопічне одноксиальне розтягувальне напруження дорівнює `σ(ε_p) = τ(ρ) / m_max`.

---

### 3. Кристалографічний аналіз крайових випадків та симетрії

При чисельному розрахунку важливо враховувати крайові випадки високої кристалографічної симетрії:

- **Орієнтація розтягу [001]:** при розтягу вздовж ребра куба `[001]` 8 із 12 систем ковзання мають абсолютно однакові максимальні фактори Шміда `m = 0.4082`. У цьому випадку відбувається множинне ковзання (Multiple Slip), що викликає надзвичайно інтенсивне деформаційне зміцнення.
- **Орієнтація розтягу [111]:** при розтягу вздовж головної діагоналі куба 6 систем ковзання мають `m = 0.2722`.
- **Орієнтація поблизу центру стереографічного трикутника [123]:** діє строго одна первинна система ковзання з `m ≈ 0.4667` (одиночне ковзання / Single Slip), що забезпечує легке ковзання на початковій стадії деформації.

---

### 4. Детальний аналіз алгоритму та структури програмного коду

Програма складається з двох автономних реалізацій: мовою C (стандарт C99) та мовою C++ (стандарт C++20).

Обчислювальний процес складається з наступних послідовних кроків:
1. **Ініціалізація фізичних констант матеріалу:** модуль зсуву `G`, вектор Бюргерса `b`, початкова щільність дислокацій `ρ₀`, Паєрлсівський опір ґратки `τ₀` та коефіцієнти Кокса — Мекінга `k₁`, `k₂`.
2. **Визначення вектора розтягу:** завдання кристалографічного напрямку осі розтягу (наприклад, `[1, 2, 3]`).
3. **Обчислення фактора Шміда:** цикл по всіх 12 ГЦК системах ковзання з розрахунком скалярних добутків `(n · n_s)` та `(n · s)`.
4. **Покрокове інтегрування:** виконання циклу за деформацією від `ε_p = 0` до `ε_p_max = 0.20` із фіксацією поточного розтягувального напруження `σ(ε_p)` та щільності дислокацій `ρ`.

---

### 5. Особливості реалізації мовою C та C++

- **Реалізація мовою C:** розроблена за стандартами системного програмування C99. Використовує процедурний підхід, стаційні структури даних `SlipSystem` та `MaterialParams`, прямолінійну векторну алгебру без виділення динамічної пам'яті у купі.
- **Реалізація мовою C++:** розроблена за сучасними стандартами C++20. Використовує сувору інкапсуляцію у просторі імен `plasticity`, стабілізовані носії даних `std::array` та `std::vector`, методи із атрибутом `[[nodiscard]]`, обробку помилок векторної норми через винятки `std::invalid_argument` та форматований вивід за допомогою `std::iomanip`.

---

### 6. Повний вихідний код реалізацій

:::tabs
```c
/* Simulation of Schmid factor and dislocation strain hardening in C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NUM_SLIP_SYSTEMS 12

typedef struct {
    double n[3]; /* Нормаль до площини ковзання */
    double s[3]; /* Напрямок ковзання */
} SlipSystem;

typedef struct {
    double G_GPa;      /* Модуль зсуву (ГПа) */
    double b_nm;       /* Вектор Бюргерса (нм) */
    double tau_0_MPa;  /* Паєрлсівське напруження (МПа) */
    double alpha;      /* Коефіцієнт зміцнення Тейлора */
    double k1;         /* Коефіцієнт накопичення дислокацій (м^-1) */
    double k2;         /* Коефіцієнт анігіляції дислокацій */
    double rho_0;      /* Початкова щільність дислокацій (м^-2) */
} MaterialParams;

/* 12 систем ковзання ГЦК кристала {111}<110> */
static const SlipSystem FCC_SLIP_SYSTEMS[NUM_SLIP_SYSTEMS] = {
    /* Площина (1, 1, 1) */
    {{ 1.0,  1.0,  1.0}, { 0.0,  1.0, -1.0}},
    {{ 1.0,  1.0,  1.0}, { 1.0,  0.0, -1.0}},
    {{ 1.0,  1.0,  1.0}, { 1.0, -1.0,  0.0}},
    /* Площина (-1, 1, 1) */
    {{-1.0,  1.0,  1.0}, { 0.0,  1.0, -1.0}},
    {{-1.0,  1.0,  1.0}, { 1.0,  0.0,  1.0}},
    {{-1.0,  1.0,  1.0}, { 1.0,  1.0,  0.0}},
    /* Площина (1, -1, 1) */
    {{ 1.0, -1.0,  1.0}, { 0.0,  1.0,  1.0}},
    {{ 1.0, -1.0,  1.0}, { 1.0,  0.0, -1.0}},
    {{ 1.0, -1.0,  1.0}, { 1.0,  1.0,  0.0}},
    /* Площина (1, 1, -1) */
    {{ 1.0,  1.0, -1.0}, { 0.0,  1.0,  1.0}},
    {{ 1.0,  1.0, -1.0}, { 1.0,  0.0,  1.0}},
    {{ 1.0,  1.0, -1.0}, { 1.0, -1.0,  0.0}}
};

static double dot_product(const double v1[3], const double v2[3]) {
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2];
}

static double vector_norm(const double v[3]) {
    return sqrt(dot_product(v, v));
}

/* Обчислення максимального фактора Шміда */
double calculate_max_schmid_factor(const double tensile_axis[3], int *best_system_idx) {
    double norm_axis = vector_norm(tensile_axis);
    if (norm_axis < 1e-9) return 0.0;

    double n_dir[3] = {
        tensile_axis[0] / norm_axis,
        tensile_axis[1] / norm_axis,
        tensile_axis[2] / norm_axis
    };

    double max_m = 0.0;
    int best_idx = 0;

    for (int i = 0; i < NUM_SLIP_SYSTEMS; ++i) {
        double n_norm = vector_norm(FCC_SLIP_SYSTEMS[i].n);
        double s_norm = vector_norm(FCC_SLIP_SYSTEMS[i].s);

        double cos_phi = fabs(dot_product(n_dir, FCC_SLIP_SYSTEMS[i].n)) / n_norm;
        double cos_lambda = fabs(dot_product(n_dir, FCC_SLIP_SYSTEMS[i].s)) / s_norm;

        double m = cos_phi * cos_lambda;
        if (m > max_m) {
            max_m = m;
            best_idx = i;
        }
    }

    if (best_system_idx) *best_system_idx = best_idx;
    return max_m;
}

/* Симуляція кривої розтягу σ(ε_p) */
void simulate_strain_hardening(const MaterialParams *mat, double max_strain, int steps) {
    double tensile_axis[3] = {1.0, 2.0, 3.0}; /* Орієнтація напрямку розтягу */
    int active_system = 0;
    double m_max = calculate_max_schmid_factor(tensile_axis, &active_system);

    printf("Орієнтація вісі розтягу: [1, 2, 3]\n");
    printf("Максимальний фактор Шміда m_max = %.4f (Система #%d)\n", m_max, active_system + 1);
    printf("--------------------------------------------------\n");
    printf("Деформація ε_p | Щільність ρ (м^-2) | Напруження σ (МПа)\n");
    printf("--------------------------------------------------\n");

    double rho = mat->rho_0;
    double d_eps = max_strain / steps;
    double G_Pa = mat->G_GPa * 1e9;
    double b_m = mat->b_nm * 1e-9;

    for (int step = 0; step <= steps; ++step) {
        double eps_p = step * d_eps;

        /* Формула Тейлора для зсувного напруження τ */
        double tau = (mat->tau_0_MPa * 1e6) + mat->alpha * G_Pa * b_m * sqrt(rho);
        double sigma_MPa = (tau / 1e6) / m_max;

        if (step % (steps / 5) == 0) {
            printf("%14.3f | %17.3e | %19.2f\n", eps_p, rho, sigma_MPa);
        }

        /* Крок інтегрування методом Ейлера: dρ/dε_p = k1*sqrt(ρ) - k2*ρ */
        double drho_deps = mat->k1 * sqrt(rho) - mat->k2 * rho;
        rho += drho_deps * d_eps;
    }
}

int main(void) {
    MaterialParams copper = {
        .G_GPa = 48.0,
        .b_nm = 0.256,
        .tau_0_MPa = 1.5,
        .alpha = 0.3,
        .k1 = 4.5e8,
        .k2 = 12.0,
        .rho_0 = 1.0e11
    };

    simulate_strain_hardening(&copper, 0.20, 100);
    return 0;
}
```

```cpp
// Simulation of Schmid factor and dislocation strain hardening in modern C++20
#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <numeric>
#include <algorithm>
#include <iomanip>

namespace plasticity {

struct Vector3D {
    double x{0.0}, y{0.0}, z{0.0};

    [[nodiscard]] constexpr double dot(const Vector3D& other) const noexcept {
        return x * other.x + y * other.y + z * other.z;
    }

    [[nodiscard]] double norm() const noexcept {
        return std::sqrt(dot(*this));
    }

    [[nodiscard]] Vector3D normalized() const {
        double n = norm();
        if (n < 1e-9) throw std::invalid_argument("Cannot normalize zero vector");
        return {x / n, y / n, z / n};
    }
};

struct SlipSystem {
    Vector3D plane_normal;
    Vector3D slip_direction;
};

struct Material {
    double shear_modulus_GPa{48.0};
    double burgers_vector_nm{0.256};
    double tau_0_MPa{1.5};
    double taylor_alpha{0.3};
    double k1_accumulation{4.5e8};
    double k2_annihilation{12.0};
    double initial_dislocation_density{1.0e11};
};

class CrystalPlasticitySimulator {
public:
    static constexpr std::array<SlipSystem, 12> fcc_slip_systems{{
        /* (111) plane */
        {{ 1.0,  1.0,  1.0}, { 0.0,  1.0, -1.0}},
        {{ 1.0,  1.0,  1.0}, { 1.0,  0.0, -1.0}},
        {{ 1.0,  1.0,  1.0}, { 1.0, -1.0,  0.0}},
        /* (-111) plane */
        {{-1.0,  1.0,  1.0}, { 0.0,  1.0, -1.0}},
        {{-1.0,  1.0,  1.0}, { 1.0,  0.0,  1.0}},
        {{-1.0,  1.0,  1.0}, { 1.0,  1.0,  0.0}},
        /* (1-11) plane */
        {{ 1.0, -1.0,  1.0}, { 0.0,  1.0,  1.0}},
        {{ 1.0, -1.0,  1.0}, { 1.0,  0.0, -1.0}},
        {{ 1.0, -1.0,  1.0}, { 1.0,  1.0,  0.0}},
        /* (11-1) plane */
        {{ 1.0,  1.0, -1.0}, { 0.0,  1.0,  1.0}},
        {{ 1.0,  1.0, -1.0}, { 1.0,  0.0,  1.0}},
        {{ 1.0,  1.0, -1.0}, { 1.0, -1.0,  0.0}}
    }};

    struct SchmidResult {
        double max_schmid_factor;
        std::size_t active_system_index;
    };

    [[nodiscard]] static SchmidResult compute_schmid_factor(const Vector3D& tensile_axis) {
        const Vector3D n_dir = tensile_axis.normalized();
        double max_m = 0.0;
        std::size_t best_idx = 0;

        for (std::size_t i = 0; i < fcc_slip_systems.size(); ++i) {
            const auto& sys = fcc_slip_systems[i];
            double cos_phi = std::abs(n_dir.dot(sys.plane_normal)) / sys.plane_normal.norm();
            double cos_lambda = std::abs(n_dir.dot(sys.slip_direction)) / sys.slip_direction.norm();
            double m = cos_phi * cos_lambda;

            if (m > max_m) {
                max_m = m;
                best_idx = i;
            }
        }
        return {max_m, best_idx};
    }

    struct SimulationPoint {
        double plastic_strain;
        double dislocation_density;
        double yield_stress_MPa;
    };

    [[nodiscard]] static std::vector<SimulationPoint> run_simulation(
        const Material& mat, 
        const Vector3D& tensile_axis, 
        double max_strain, 
        std::size_t steps) 
    {
        const auto [m_max, active_idx] = compute_schmid_factor(tensile_axis);
        std::vector<SimulationPoint> results;
        results.reserve(steps + 1);

        double rho = mat.initial_dislocation_density;
        const double d_eps = max_strain / static_cast<double>(steps);
        const double G_Pa = mat.shear_modulus_GPa * 1e9;
        const double b_m = mat.burgers_vector_nm * 1e-9;

        for (std::size_t i = 0; i <= steps; ++i) {
            double eps_p = static_cast<double>(i) * d_eps;
            double tau_Pa = (mat.tau_0_MPa * 1e6) + mat.taylor_alpha * G_Pa * b_m * std::sqrt(rho);
            double sigma_MPa = (tau_Pa / 1e6) / m_max;

            results.push_back({eps_p, rho, sigma_MPa});

            // Kocks-Mecking evolution equation
            double drho_deps = mat.k1_accumulation * std::sqrt(rho) - mat.k2_annihilation * rho;
            rho += drho_deps * d_eps;
        }

        return results;
    }
};

} // namespace plasticity

int main() {
    using namespace plasticity;

    Material copper;
    Vector3D tension_axis{1.0, 2.0, 3.0};

    auto [m_max, sys_idx] = CrystalPlasticitySimulator::compute_schmid_factor(tension_axis);
    std::cout << "C++20 Sim: Tension axis [1, 2, 3]\n";
    std::cout << "Max Schmid factor m_max = " << std::fixed << std::setprecision(4) 
              << m_max << " (System #" << sys_idx + 1 << ")\n";

    auto curve = CrystalPlasticitySimulator::run_simulation(copper, tension_axis, 0.20, 100);

    std::cout << "--------------------------------------------------\n";
    std::cout << "Деформація ε_p | Щільність ρ (м^-2) | Напруження σ (МПа)\n";
    std::cout << "--------------------------------------------------\n";

    for (std::size_t i = 0; i < curve.size(); i += curve.size() / 5) {
        const auto& pt = curve[i];
        std::cout << std::setw(14) << std::setprecision(3) << pt.plastic_strain << " | "
                  << std::scientific << std::setw(17) << std::setprecision(3) << pt.dislocation_density << " | "
                  << std::fixed << std::setw(19) << std::setprecision(2) << pt.yield_stress_MPa << "\n";
    }

    return 0;
}
```
:::
