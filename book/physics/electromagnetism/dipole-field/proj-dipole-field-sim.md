# ⚙️ Чисельне моделювання поля та потенціалу електричного диполя

Чисельне моделювання електростатичних полів є базовим інструментом при розрахунку молекулярних систем, мікрофлюїдних пристроїв діелектрофорезу, проектуванні антенних масивів та аналізі медичних електрокардіограм (ЕКГ). Оскільки аналітичне розв'язання рівнянь Максвелла можливе лише для найпростіших симетричних конфігурацій, обчислювальний аналіз поля довільної сукупності диполів спирається на дискретизацію простору, паралельне обчислення сіток та чисельне інтегрування силових ліній.

У цій практичній вставці розглядається математичний алгоритм, архітектура обчислювального ядра та готова реалізація програми двома мовами (C та C++) для розрахунку тривимірного векторного поля напруженості, скалярного потенціалу, обертального моменту, втягуючої сили та трасування силових ліній методом Рунге — Кутти 4-го порядку.

## 1. Математична та алгоритмічна модель

Розглянемо диполь з моментом `p = (p_x, p_y, p_z)`, розташований у точці з радіус-вектором `r₀ = (x₀, y₀, z₀)`. Для довільної точки спостереження у просторі `r = (x, y, z)` обчислюється вектор відносного зміщення `R = r − r₀` та його модуль `R = |R|`.

Скалярний потенціал та вектор напруженості електричного поля у декартових координатах описуються виразами:

```
φ(R) = (1 / (4·π·ε₀)) · (p · R) / R³                      [скалярний потенціал у точці R]
E(R) = (1 / (4·π·ε₀)) · [ 3 · (p · R) · R / R⁵ − p / R³ ] [вектор напруженості у точці R]
```

### Проблема чисельної сингулярності та згладжування (Cutoff)

При обчисленні поля безпосередньо поблизу центру диполя (`R -> 0`) модуль відстані `R` прямує до нуля, що призводить до ділення на нуль, генеруючи числові значення `NaN` (Not a Number) або переповнення реєстрів процесора (`Infinity`). Для усунення цієї обчислювальної сингулярності у чисельному аналізі застосовується метод регуляризації ядра Поассона шляхом введення параметра згладжування (near-field cutoff parameter) `ε_cut`:

```
R_eff = √(R_x² + R_y² + R_z² + ε_cut²)                    [ефективний модуль відстані зі згладжуванням]
```

Вибір значення `ε_cut` залежить від фізичного масштабу задачі: для молекулярної динаміки `ε_cut ≈ 10⁻¹₀ m` (порядок радіуса атома), для макроскопічних антенних задач `ε_cut ≈ 10⁻⁴ m`.

### Алгоритм трасування силових ліній (метод Рунге — Кутти 4-го порядку)

Силова лінія електричного поля є кривою, дотична до якої в кожній точці збігається з вектором напруженості електричного поля `E`. Диференціальне рівняння силової лінії записується у вигляді:

```
dr / ds = E(r) / |E(r)|                                   [диференціальне рівняння силової лінії]
```

де `s` — натуральний параметр довжини вздовж лінії. Простий метод Ейлера `r_{k+1} = r_k + h · (E / |E|)` має локальну похибку першого порядку `O(h)`, що призводить до систематичного нагромадження числового дрейфу — силові лінії відхиляються від справжньої траєкторії, утворюючи штучні спіралі.

Для досягнення високої точності застосовується класичний чисельний метод Рунге — Кутти 4-го порядку (RK4) з локальною похибкою `O(h⁵)`. Обчислення проміжних векторів напруженості на кожному кроці виконується за алгоритмом:

```
k₁ = h · ( E(r_k) / |E(r_k)| )                            [перший проміжний вектор зміщення]
k₂ = h · ( E(r_k + k₁/2) / |E(r_k + k₁/2)| )              [другий проміжний вектор зміщення]
k₃ = h · ( E(r_k + k₂/2) / |E(r_k + k₂/2)| )              [третій проміжний вектор зміщення]
k₄ = h · ( E(r_k + k₃) / |E(r_k + k₃)| )                  [четвертий проміжний вектор зміщення]

r_{k+1} = r_k + (1/6) · (k₁ + 2·k₂ + 2·k₃ + k₄)           [новий крок траєкторії силової лінії]
```

Трасування припиняється за справдження однієї з трьох умов:
1. Силова лінія наблизилася до негативного заряду на відстань `R < ε_cut`.
2. Силова лінія вийшла за межі розрахункової області `|r| > R_max`.
3. Досягнуто максимальну кількість кроків інтегрування `N_max`.

### Дискретизація просторової сітки та 3D-масиви

Для побудови карток потенціалу у розрахунковому об'ємі `[X_min, X_max] × [Y_min, Y_max] × [Z_min, Z_max]` створюється регулярна прямокутна сітка з кроками `dx, dy, dz`. Точки сітки індексуються як `(i, j, k)`, де `x_i = X_min + i·dx`, `y_j = Y_min + j·dy`, `z_k = Z_min + k·dz`.

Одновимірне лінійне представлення тривимірного масиву (row-major order) гарантує послідовне розташування даних у оперативній пам'яті, що максимально ефективно використовує кеш-пам'ять L1/L2 процесора:

```
index = i · (N_y · N_z) + j · N_z + k                      [лінійний індекс вузла 3D сітки]
```

Для оптимізації розрахунків великих молекулярних систем із мільйонами диполів застосовуються ієрархічні дерева (Octree) або просторове впорядкування за кривою Мортона (Morton Z-order curve). Це дозволяє відсікати далекі диполі за допомогою методу Евальда (Particle Mesh Ewald, PME), зменшуючи обчислювальну складність із `O(N²)` до `O(N log N)`.

### Граничні умови та дзеркальні відображення

При моделюванні диполя поблизу провідних або діелектричних поверхонь застосовується метод дзеркальних зображень. Якщо провідна площина розташована при `z = 0`, вплив індукованих поверхневих зарядів еквівалентний додаванню дзеркального диполя `p_img` у точці `(x₀, y₀, −z₀)` із вектором моменту `p_img = (−p_x, −p_y, +p_z)`.

### Розрахунок чисельних градієнтів та сил взаємодії

Для розрахунку діелектрофоретичної сили `F = (p · ∇)E` в умовах, коли аналітичний вираз для градієнта поля невідомий (наприклад, при обчисленні полів від складної геометричної сітки зчитувальних електродів), застосовується чисельне диференціювання методом центральних різниць 2-го порядку точності:

```
∂E_x / ∂x = ( E_x(x + dx, y, z) − E_x(x − dx, y, z) ) / (2 · dx)  [чисельна похідна по X]
∂E_x / ∂y = ( E_x(x, y + dy, z) − E_x(x, y − dy, z) ) / (2 · dy)  [чисельна похідна по Y]
∂E_x / ∂z = ( E_x(x, y, z + dz) − E_x(x, y, z − dz) ) / (2 · dz)  [чисельна похідна по Z]
```

Вибір кроку диференціювання `dx = 10⁻⁶ m` забезпечує мінімізацію сумарної чисельної похибки (баланс між похибкою усічення Тейлора та похибкою округлення чисел з плаваючою комою подвійної точності `double`).

При симуляції системи з багатьма диполями обчислюється матриця парних взаємодій. Сумарний потенціал у точці `P` від `M` диполів обчислюється шляхом векторного підсумовування внесків від кожного джерела `φ_tot = ∑ φ_m`.

## 2. Реалізація обчислювального ядра на C та C++

Нижче наведено вихідний код програми. У відповідності до канону написання коду (§5 AUTHORING), приклад реалізовано двома мовами у вигляді вкладок `:::tabs`. Реалізація на мові C++ є повністю ідіоматичною: вона не використовує макроси, C-масиви або `malloc/free`, а спирається на строго типізовані структури, методи об'єктно-орієнтованого проектування, семантику переміщення, векторні контейнери `std::vector` та константні вирази `constexpr`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define VACUUM_EPSILON0 8.8541878128e-12
#define CUTOFF_EPSILON  1e-9
#define RK4_STEPS       500
#define RK4_STEP_SIZE   1e-10

typedef struct {
    double x;
    double y;
    double z;
} Vector3;

typedef struct {
    Vector3 pos;
    Vector3 p;
} Dipole;

static Vector3 vec3_add(Vector3 a, Vector3 b) {
    Vector3 r = {a.x + b.x, a.y + b.y, a.z + b.z};
    return r;
}

static Vector3 vec3_sub(Vector3 a, Vector3 b) {
    Vector3 r = {a.x - b.x, a.y - b.y, a.z - b.z};
    return r;
}

static Vector3 vec3_scale(Vector3 a, double s) {
    Vector3 r = {a.x * s, a.y * s, a.z * s};
    return r;
}

static double vec3_dot(Vector3 a, Vector3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

static Vector3 vec3_cross(Vector3 a, Vector3 b) {
    Vector3 r = {
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
    return r;
}

static double vec3_norm(Vector3 a) {
    return sqrt(vec3_dot(a, a));
}

static Vector3 vec3_normalize(Vector3 a) {
    double len = vec3_norm(a);
    if (len < 1e-18) {
        Vector3 zero = {0.0, 0.0, 0.0};
        return zero;
    }
    return vec3_scale(a, 1.0 / len);
}

double dipole_potential(const Dipole* d, Vector3 point) {
    Vector3 R = vec3_sub(point, d->pos);
    double r_sq = vec3_dot(R, R) + CUTOFF_EPSILON * CUTOFF_EPSILON;
    double r_len = sqrt(r_sq);
    double k_e = 1.0 / (4.0 * M_PI * VACUUM_EPSILON0);
    double dot_pR = vec3_dot(d->p, R);
    return k_e * dot_pR / (r_len * r_len * r_len);
}

Vector3 dipole_electric_field(const Dipole* d, Vector3 point) {
    Vector3 R = vec3_sub(point, d->pos);
    double r_sq = vec3_dot(R, R) + CUTOFF_EPSILON * CUTOFF_EPSILON;
    double r_len = sqrt(r_sq);
    double r_pow3 = r_len * r_len * r_len;
    double r_pow5 = r_pow3 * r_sq;
    double k_e = 1.0 / (4.0 * M_PI * VACUUM_EPSILON0);

    double dot_pR = vec3_dot(d->p, R);
    Vector3 term1 = vec3_scale(R, 3.0 * dot_pR / r_pow5);
    Vector3 term2 = vec3_scale(d->p, 1.0 / r_pow3);
    Vector3 diff = vec3_sub(term1, term2);

    return vec3_scale(diff, k_e);
}

Vector3 dipole_torque(const Dipole* d, Vector3 external_e) {
    return vec3_cross(d->p, external_e);
}

double dipole_potential_energy(const Dipole* d, Vector3 external_e) {
    return -vec3_dot(d->p, external_e);
}

int trace_field_line_rk4(const Dipole* d, Vector3 start_pt, Vector3* out_path, int max_points) {
    if (!d || !out_path || max_points <= 0) return 0;

    out_path[0] = start_pt;
    int count = 1;
    double h = RK4_STEP_SIZE;

    for (int i = 1; i < max_points; ++i) {
        Vector3 curr = out_path[i - 1];

        Vector3 E1 = dipole_electric_field(d, curr);
        Vector3 k1 = vec3_scale(vec3_normalize(E1), h);

        Vector3 p2 = vec3_add(curr, vec3_scale(k1, 0.5));
        Vector3 E2 = dipole_electric_field(d, p2);
        Vector3 k2 = vec3_scale(vec3_normalize(E2), h);

        Vector3 p3 = vec3_add(curr, vec3_scale(k2, 0.5));
        Vector3 E3 = dipole_electric_field(d, p3);
        Vector3 k3 = vec3_scale(vec3_normalize(E3), h);

        Vector3 p4 = vec3_add(curr, k3);
        Vector3 E4 = dipole_electric_field(d, p4);
        Vector3 k4 = vec3_scale(vec3_normalize(E4), h);

        Vector3 step = vec3_scale(
            vec3_add(vec3_add(k1, vec3_scale(k2, 2.0)), vec3_add(vec3_scale(k3, 2.0), k4)),
            1.0 / 6.0
        );

        Vector3 next_pt = vec3_add(curr, step);
        out_path[i] = next_pt;
        count++;

        if (vec3_norm(vec3_sub(next_pt, d->pos)) > 1e-7) {
            break; // Вихід за область аналізу
        }
    }
    return count;
}

int main(void) {
    Dipole d = {
        .pos = {0.0, 0.0, 0.0},
        .p = {0.0, 0.0, 1e-29} // 1 e·Å ≈ 1.6e-29 C·m
    };

    Vector3 eval_pt = {0.0, 0.0, 1e-9}; // 1 нм по осі z
    double phi = dipole_potential(&d, eval_pt);
    Vector3 E = dipole_electric_field(&d, eval_pt);

    printf("=== Симуляція диполя (C API) ===\n");
    printf("Потенціал phi(1nm) = %.6e V\n", phi);
    printf("Поле E(1nm) = (%.6e, %.6e, %.6e) V/m\n", E.x, E.y, E.z);

    Vector3 ext_E = {1e5, 0.0, 0.0};
    Vector3 torque = dipole_torque(&d, ext_E);
    double energy = dipole_potential_energy(&d, ext_E);

    printf("Обертальний момент torque = (%.6e, %.6e, %.6e) N·m\n", torque.x, torque.y, torque.z);
    printf("Потенціальна енергія U = %.6e J\n", energy);

    Vector3 line_pts[100];
    int n_pts = trace_field_line_rk4(&d, eval_pt, line_pts, 100);
    printf("Прораховано %d точок силової лінії RK4.\n", n_pts);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <stdexcept>
#include <span>

namespace physics {

constexpr double vacuum_epsilon0 = 8.8541878128e-12;
constexpr double default_cutoff = 1e-9;

struct Vector3 {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    constexpr Vector3 operator+(const Vector3& o) const noexcept {
        return {x + o.x, y + o.y, z + o.z};
    }
    constexpr Vector3 operator-(const Vector3& o) const noexcept {
        return {x - o.x, y - o.y, z - o.z};
    }
    constexpr Vector3 operator*(double s) const noexcept {
        return {x * s, y * s, z * s};
    }
    constexpr double dot(const Vector3& o) const noexcept {
        return x * o.x + y * o.y + z * o.z;
    }
    constexpr Vector3 cross(const Vector3& o) const noexcept {
        return {
            y * o.z - z * o.y,
            z * o.x - x * o.z,
            x * o.y - y * o.x
        };
    }
    [[nodiscard]] double norm() const noexcept {
        return std::sqrt(dot(*this));
    }
    [[nodiscard]] Vector3 normalized() const noexcept {
        double len = norm();
        if (len < 1e-18) return {0.0, 0.0, 0.0};
        return *this * (1.0 / len);
    }
};

class Dipole {
private:
    Vector3 position_{};
    Vector3 moment_{};

public:
    constexpr Dipole(Vector3 pos, Vector3 p) noexcept : position_(pos), moment_(p) {}

    [[nodiscard]] constexpr Vector3 position() const noexcept { return position_; }
    [[nodiscard]] constexpr Vector3 moment() const noexcept { return moment_; }

    [[nodiscard]] double potential(Vector3 point, double cutoff = default_cutoff) const noexcept {
        Vector3 R = point - position_;
        double r_sq = R.dot(R) + cutoff * cutoff;
        double r_len = std::sqrt(r_sq);
        double k_e = 1.0 / (4.0 * std::numbers::pi * vacuum_epsilon0);
        return k_e * moment_.dot(R) / (r_len * r_len * r_len);
    }

    [[nodiscard]] Vector3 electric_field(Vector3 point, double cutoff = default_cutoff) const noexcept {
        Vector3 R = point - position_;
        double r_sq = R.dot(R) + cutoff * cutoff;
        double r_len = std::sqrt(r_sq);
        double r_pow3 = r_len * r_len * r_len;
        double r_pow5 = r_pow3 * r_sq;
        double k_e = 1.0 / (4.0 * std::numbers::pi * vacuum_epsilon0);

        double dot_pR = moment_.dot(R);
        Vector3 term1 = R * (3.0 * dot_pR / r_pow5);
        Vector3 term2 = moment_ * (1.0 / r_pow3);
        return (term1 - term2) * k_e;
    }

    [[nodiscard]] constexpr Vector3 torque(Vector3 ext_field) const noexcept {
        return moment_.cross(ext_field);
    }

    [[nodiscard]] constexpr double potential_energy(Vector3 ext_field) const noexcept {
        return -moment_.dot(ext_field);
    }
};

class FieldLineTracerRK4 {
private:
    Dipole dipole_;
    double step_size_{1e-10};

public:
    explicit FieldLineTracerRK4(Dipole d, double step_size = 1e-10)
        : dipole_(d), step_size_(step_size) {}

    [[nodiscard]] std::vector<Vector3> trace(Vector3 start_point, std::size_t max_steps = 500) const {
        std::vector<Vector3> path;
        path.reserve(max_steps);
        path.push_back(start_point);

        for (std::size_t i = 1; i < max_steps; ++i) {
            Vector3 curr = path.back();

            Vector3 k1 = dipole_.electric_field(curr).normalized() * step_size_;
            Vector3 k2 = dipole_.electric_field(curr + k1 * 0.5).normalized() * step_size_;
            Vector3 k3 = dipole_.electric_field(curr + k2 * 0.5).normalized() * step_size_;
            Vector3 k4 = dipole_.electric_field(curr + k3).normalized() * step_size_;

            Vector3 step = (k1 + k2 * 2.0 + k3 * 2.0 + k4) * (1.0 / 6.0);
            Vector3 next_pt = curr + step;

            path.push_back(next_pt);

            if ((next_pt - dipole_.position()).norm() > 1e-7) {
                break; // Траєкторія вийшла за межі розгляду
            }
        }
        return path;
    }
};

} // namespace physics

int main() {
    using namespace physics;

    Dipole d({0.0, 0.0, 0.0}, {0.0, 0.0, 1e-29});
    Vector3 eval_pt{0.0, 0.0, 1e-9};

    std::cout << "=== Симуляція диполя (C++20 API) ===\n";
    std::cout << "Потенціал phi(1nm) = " << d.potential(eval_pt) << " V\n";

    Vector3 E = d.electric_field(eval_pt);
    std::cout << "Поле E(1nm) = (" << E.x << ", " << E.y << ", " << E.z << ") V/m\n";

    Vector3 ext_E{1e5, 0.0, 0.0};
    Vector3 torque = d.torque(ext_E);
    std::cout << "Момент torque = (" << torque.x << ", " << torque.y << ", " << torque.z << ") N·m\n";

    FieldLineTracerRK4 tracer(d, 1e-10);
    auto path = tracer.trace(eval_pt, 100);
    std::cout << "Успішно побудовано силову лінію RK4 з " << path.size() << " точок.\n";

    return 0;
}
```
:::

## 3. Аналіз обчислювальної складності та оптимізації

- **Складність прямого обчислення**: Розрахунок поля однієї точки вимагає `14` операцій множення, `9` додавань/віднімань та `1` операцію обчислення квадратного кореня (`std::sqrt`). Алгоритм має складність `O(1)` для однієї точки та `O(N)` для сітки з `N` вузлів.
- **Векторизація SIMD**: Оскільки розрахунок вузлів сітки є повністю незалежним, код ідеально векторизується за допомогою інструкцій AVX2 / AVX-512 або розпаралелюється через OpenMP `#pragma omp parallel for`.
- **Точність трасування RK4**: Використання методу Рунге — Кутти 4-го порядку замість простого методу Ейлера забезпечує локальну похибку `O(h⁵)`, що дозволяє будувати гладкі силові лінії без накопичення систематичного дрейфу радіуса.
