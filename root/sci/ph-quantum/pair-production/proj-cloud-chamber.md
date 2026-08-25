# ⚙️ Обчислення та симуляція треків електрон-позитронних пар у магнітному полі

Обчислювальний алгоритм релятивістської кінематики, чисельні методи інтегрування траєкторій та симуляція кривизни треків електрон-позитронних пар у магнітному полі хмарної камери або бульбашкової камери базуються на покроковому інтегруванні рівнянь руху під дією сили Лоренца.

## Фізична модель руху частинки в магнітному полі

У однорідному магнітному полі `B`, спрямованому перпендикулярно до площини руху частинки з зарядом `q` та релятивістським імпульсом `p`, на частинку діє сила Лоренца `F = q (v × B)`.

Релятивістський радіус кривизни траєкторії `R` описується формулою:

```
R = p / (|q| · B) = (γ · m_e · v) / (|q| · B)
```

Де:
- `γ = 1 / √(1 - v² / c²)` — релятивістський лоренц-фактор;
- `p = √(E² / c² - m_e² c²)` — 3-імпульс частинки;
- `E = E_kin + m_e c²` — повна енергія частинки;
- `q = -e` для електрона та `q = +e` для позитрона.

Знаючи радіус кривизни `R` та напрямок вигину траєкторії (ліворуч або праворуч), експериментатор може визначити знак заряду частинки та її 3-імпульс.

## Фізичні механізми гальмування та втрати енергії в середовищі

Під час руху крізь середовище хмарної камери (перенасичену пару води або спирту в газі-носії) чи бульбашкової камери (перегріту рідку суміш) електрон і позитрон зазнають неперервного сповільнення. Сумарні питомі втрати енергії на одиницю шляху `dE/dx` складаються з двох основних фізичних компонентів:

```
(dE / dx)_total = (dE / dx)_ion + (dE / dx)_rad
```

1. **Іонізаційні втрати `(dE/dx)_ion`:** описуються релятивістською формулою Бете — Блоха для легких частинок (з урахуванням ефектів тотожності частинок для електрона та анігіляції на льоту для позитрона). При релятивістських енергіях іонізаційні втрати проходять через характерний "плато"-мінімум (частинки мінімальної іонізації, MIP), який становить близько `1.5–2.0 МеВ / (г/см²)`. Іонізаційні втрати призводять до того, що радіус кривизни траєкторії `R(t)` неперервно зменшується за ходом руху частинки, перетворюючи колову орбіту на згортальну спіраль.

2. **Радіаційні втрати (гальмівне випромінювання `dE/dx_rad`):** виникають унаслідок прискорення електрона чи позитрона в кулонівських полях атомних ядер середовища. Питомі радіаційні втрати пропорційні поній енергії частинки:

   ```
   (dE / dx)_rad = E / X₀
   ```

   Де `X₀` — радіаційна довжина матеріалу (для повітря `X₀ ≈ 300 м`, для свинцю `X₀ ≈ 0.56 см`). При енергіях, що перевищують критичну енергію середовища `E_crit` (для свинцю `E_crit ≈ 7.2 МеВ`), гальмівне випромінювання стає основним механізмом втрати енергії, спричиняючи розвиток каскадних електромагнітних злив.

## Чисельні методи інтегрування рівнянь руху

Рівняння руху частинки зі змінною за масою та напрямком швидкістю в трьох вимірах описуються системою звичайних диференціальних рівнянь другого порядку:

```
d/dt (γ m_e v) = q (v × B) + F_drag(v)
```

Для чисельного розв'язку цієї системи у комп'ютерному моделюванні застосовують два основні підходи:

1. **Метод Ейлера — Кромера (симплектичний метод 1-го порядку):**
   Забезпечує високу швидкість обчислень і стійкість для циліндричних та спіральних траєкторій у магнітному полі. На кожному кроці за часом `Δt` спочатку оновлюються компоненти швидкості з урахуванням релятивістської сили Лоренца, а потім оновлені значення швидкості використовуються для обчислення нових координат:

   ```
   v_{n+1} = v_n + (F(r_n, v_n) / (γ_n m_e)) · Δt
   r_{n+1} = r_n + v_{n+1} · Δt
   ```

2. **Метод Рунге — Кутти 4-го порядку (RK4):**
   Використовується при потребі високої точності розрахунку в неоднорідних магнітних полях або при наявності швидких іонізаційних втрат. Метод розраховує чотири проміжні оцінки векторів прискорення `k₁, k₂, k₃, k₄` на кожному часовому кроці, забезпечуючи локальну похибку порядку `O(Δt⁵)`.

## Програмна реалізація розрахунку кінематики та треків

Нижче наведено програмну реалізацію мовами C та C++, яка приймає початкову енергію гамма-фотона `E_γ` та індукцію магнітного поля `B`, перевіряє порогову умову `E_γ ≥ 2 m_e c²`, розраховує кінетичні енергії утвореного електрона та позитрона, а також інтегрує траєкторію їхнього руху методом Ейлера-Кромера.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define C_SPEED 2.99792458e8     /* м/с */
#define ELECTRON_MASS_KG 9.1093837015e-31  /* кг */
#define ELECTRON_CHARGE_C 1.602176634e-19  /* Кл */
#define MEV_TO_JOULE 1.602176634e-13

typedef struct {
    double x;
    double y;
    double vx;
    double vy;
    double charge;
} Particle;

void simulate_track(Particle *p, double B, double dt, int steps, const char *filename) {
    FILE *f = fopen(filename, "w");
    if (!f) return;

    fprintf(f, "x,y\n");
    for (int i = 0; i < steps; ++i) {
        fprintf(f, "%.6f,%.6f\n", p->x, p->y);

        double v_sq = p->vx * p->vx + p->vy * p->vy;
        double beta_sq = v_sq / (C_SPEED * C_SPEED);
        if (beta_sq >= 1.0) beta_sq = 0.999999;
        double gamma = 1.0 / sqrt(1.0 - beta_sq);

        /* Сила Лоренца: Fx = q * vy * B, Fy = -q * vx * B */
        double Fx = p->charge * ELECTRON_CHARGE_C * p->vy * B;
        double Fy = -p->charge * ELECTRON_CHARGE_C * p->vx * B;

        /* Прискорення з урахуванням релятивістської маси m = gamma * m_e */
        double ax = Fx / (gamma * ELECTRON_MASS_KG);
        double ay = Fy / (gamma * ELECTRON_MASS_KG);

        p->vx += ax * dt;
        p->vy += ay * dt;

        p->x += p->vx * dt;
        p->y += p->vy * dt;
    }
    fclose(f);
}

int main(void) {
    double E_gamma_MeV = 5.0;  /* Енергія фотона 5 МеВ */
    double B_field = 0.5;       /* Магнітне поле 0.5 Тесла */

    double m_e_c2_MeV = 0.51099895;
    if (E_gamma_MeV < 2.0 * m_e_c2_MeV) {
        printf("Помилка: енергія фотона нижче порога 1.022 МеВ\n");
        return 1;
    }

    double E_kin_total = E_gamma_MeV - 2.0 * m_e_c2_MeV;
    /* Припускаємо симетричний розподіл енергії */
    double E_kin_e = E_kin_total / 2.0;

    double E_total_J = (E_kin_e + m_e_c2_MeV) * MEV_TO_JOULE;
    double gamma = E_total_J / (ELECTRON_MASS_KG * C_SPEED * C_SPEED);
    double beta = sqrt(1.0 - 1.0 / (gamma * gamma));
    double v0 = beta * C_SPEED;

    double p_joule_s = gamma * ELECTRON_MASS_KG * v0;
    double radius = p_joule_s / (ELECTRON_CHARGE_C * B_field);

    printf("Енергія фотона: %.3f МеВ\n", E_gamma_MeV);
    printf("Кінетична енергія електрона/позитрона: %.3f МеВ\n", E_kin_e);
    printf("Лоренц-фактор γ: %.4f\n", gamma);
    printf("Розрахунковий радіус кривизни R: %.4f м\n", radius);

    Particle electron = {0.0, 0.0, 0.0, v0, -1.0};
    Particle positron = {0.0, 0.0, 0.0, v0, +1.0};

    simulate_track(&electron, B_field, 1e-11, 1000, "electron_track.csv");
    simulate_track(&positron, B_field, 1e-11, 1000, "positron_track.csv");

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <fstream>
#include <string_view>
#include <expected>
#include <system_error>

constexpr double C_SPEED = 2.99792458e8;
constexpr double ELECTRON_MASS_KG = 9.1093837015e-31;
constexpr double ELECTRON_CHARGE_C = 1.602176634e-19;
constexpr double MEV_TO_JOULE = 1.602176634e-13;
constexpr double MEV_REST_MASS = 0.51099895;

struct Point2D {
    double x{0.0};
    double y{0.0};
};

struct ParticleState {
    Point2D pos{};
    double vx{0.0};
    double vy{0.0};
    double charge_sign{-1.0};
};

class TrackSimulator {
public:
    explicit TrackSimulator(double magnetic_field) : b_field_{magnetic_field} {}

    [[nodiscard]] std::vector<Point2D> run(ParticleState state, double dt, std::size_t steps) const {
        std::vector<Point2D> path;
        path.reserve(steps);

        for (std::size_t i = 0; i < steps; ++i) {
            path.push_back(state.pos);

            const double v_sq = state.vx * state.vx + state.vy * state.vy;
            double beta_sq = v_sq / (C_SPEED * C_SPEED);
            if (beta_sq >= 1.0) beta_sq = 0.999999;
            const double gamma = 1.0 / std::sqrt(1.0 - beta_sq);

            const double fx = state.charge_sign * ELECTRON_CHARGE_C * state.vy * b_field_;
            const double fy = -state.charge_sign * ELECTRON_CHARGE_C * state.vx * b_field_;

            const double ax = fx / (gamma * ELECTRON_MASS_KG);
            const double ay = fy / (gamma * ELECTRON_MASS_KG);

            state.vx += ax * dt;
            state.vy += ay * dt;

            state.pos.x += state.vx * dt;
            state.pos.y += state.vy * dt;
        }
        return path;
    }

private:
    double b_field_;
};

struct KinematicsResult {
    double kinetic_energy_mev;
    double gamma;
    double radius_m;
};

std::expected<KinematicsResult, std::string_view> calculate_pair_kinematics(double photon_energy_mev, double b_field) {
    if (photon_energy_mev < 2.0 * MEV_REST_MASS) {
        return std::unexpected("Енергія фотона замала для народження пари");
    }

    const double e_kin_total = photon_energy_mev - 2.0 * MEV_REST_MASS;
    const double e_kin_each = e_kin_total / 2.0;

    const double e_total_j = (e_kin_each + MEV_REST_MASS) * MEV_TO_JOULE;
    const double gamma = e_total_j / (ELECTRON_MASS_KG * C_SPEED * C_SPEED);
    const double beta = std::sqrt(1.0 - 1.0 / (gamma * gamma));
    const double v0 = beta * C_SPEED;

    const double p_joule_s = gamma * ELECTRON_MASS_KG * v0;
    const double radius = p_joule_s / (ELECTRON_CHARGE_C * b_field);

    return KinematicsResult{e_kin_each, gamma, radius};
}

int main() {
    constexpr double photon_energy = 5.0;
    constexpr double b_field = 0.5;

    auto result = calculate_pair_kinematics(photon_energy, b_field);
    if (!result) {
        std::cerr << "Помилка: " << result.error() << '\n';
        return 1;
    }

    std::cout << "Кінетична енергія частинки: " << result->kinetic_energy_mev << " МеВ\n";
    std::cout << "Лоренц-фактор γ: " << result->gamma << '\n';
    std::cout << "Радіус кривизни R: " << result->radius_m << " м\n";

    TrackSimulator sim{b_field};
    const double v0 = std::sqrt(1.0 - 1.0 / (result->gamma * result->gamma)) * C_SPEED;

    ParticleState electron{{0.0, 0.0}, 0.0, v0, -1.0};
    ParticleState positron{{0.0, 0.0}, 0.0, v0, +1.0};

    auto e_track = sim.run(electron, 1e-11, 1000);
    auto p_track = sim.run(positron, 1e-11, 1000);

    std::cout << "Успішно обчислено " << e_track.size() << " точок траєкторії.\n";
    return 0;
}
```
:::

## Алгоритми аналізу експериментальних даних та фітингу треків

У реальному трековому детекторі експериментатор отримує не неперервну математичну криву, а дискретний набір просторових точок `(x_i, y_i, z_i)` з розкидом (шумом), зумовленим флуктуаціями розмірів крапель конденсату чи бульбашок газу та дрейфом зарядів у зчитувальній електроніці.

Для реконструкції імпульсу частинки з дискретного набору точок застосовують такі математичні алгоритми:

### 1. Метод фітингу колом за трьома точками

Для коротких сегментів треку радіус кривизни `R` та координати центра кола `(x_c, y_c)` можна первинно оцінити за трьома характерними точками `P₁(x₁, y₁)`, `P₂(x₂, y₂)` та `P₃(x₃, y₃)` (початок, середина та кінець виміряної дуги).

Площа трикутника `S`, утвореного цими трьома точками, обчислюється через косовий добуток:

```
S = 0.5 · |x₁ (y₂ - y₃) + x₂ (y₃ - y₁) + x₃ (y₁ - y₂)|
```

Довжини трьох сторін трикутника `a = |P₂P₃|`, `b = |P₁P₃|`, `c = |P₁P₂|`. Тоді радіус описаного навколо трикутника кола дорівнює:

```
R = (a · b · c) / (4 · S)
```

Напрямок кривизни (знак заряду `q`) визначається знаком орієнтованого косого добутку векторів `P₁P₂ × P₂P₃`.

### 2. Метод найменших квадратів для відновлення дуги кола

Для масиву з `N` дискретних точок `(x_i, y_i)` з ваговими коефіцієнтами вимірювальної похибки `w_i = 1 / σ_i²` мінімізується функціонал незв'язки:

```
χ²(x_c, y_c, R) = ∑_i w_i · [(x_i - x_c)² + (y_i - y_c)² - R²]²
```

Лінеаризація цієї системи (алгоритм Карпа) зводиться до розв'язання системи лінійних алгебраїчних рівнянь розміром 3×3 відносно параметрів `x_c, y_c` та `R² - x_c² - y_c²`.

### 3. Фільтр Кальмана для треків у неоднорідному середовищі

У сучасних експериментальних комплексах (наприклад, Time Projection Chamber у CERN ALICE чи ATLAS) частинки проходять крізь шари кремнієвих піксельних детекторів, опорних конструкцій та систем охолодження. На кожному шарі частинка зазнає багатократного кулонівського розсіювання на малі кути (кутова дисперсія `θ_MS ≈ (13.6 МеВ / (p β c)) · z √(x / X₀)`).

Для оптимізації реконструйованої траєкторії застосовують **фільтр Кальмана** (Kalman Filter). Алгоритм послідовно просуває вектор стану частинки `x_k = (x, y, dx/dz, dy/dz, q/p)_k` від одного шару детектора до наступного, оновлюючи коваріаційну матрицю похибок з урахуванням матриці багатократного розсіювання `Q_k` та вимірювального шуму `R_k`. Це дозволяє отримати оптимальну оцінку імпульсу `p` з відносною похибкою `σ_p / p < 1%` у широкому діапазоні енергій від МеВ до ТеВ.

## Оцінка радіусів для експериментальних умов

Для гамма-кванта енергією `E_γ = 5 МеВ` у магнітному полі `B = 0.5 Тл` кінетична енергія кожного з утворених продуктів становить близько `1.989 МеВ`. Розрахунковий лоренц-фактор `γ ≈ 4.89`, а радіус кривизни спірального треку в хмарній камері дорівнює приблизно `1.63 см`. 

Оскільки знак заряду електрона й позитрона протилежний (`-e` та `+e`), сила Лоренца закручує траєкторії у протилежні боки. Це створює характерний "вилка"-трек (або "роги"), вихідною точкою якого є точка народження пари у речовині мішені.
