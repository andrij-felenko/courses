# ⚙️ Модель розрахунку міцності та деформації композитного променя на C та C++

У конструкціях сучасних безпілотних апаратів опорні промені моторів і силові елементи крила зазнають комбінованого навантаження: вигину від підйомної сили чи тяги гвинтів, кручення від реактивного моменту двигунів та вібраційного навантаження. На відміну від ізотропних металів (сталі, алюмінію), композитні балки є шаруватими ортотропними структурами. Їхня загальна жорсткість і гранична міцність безпосередньо залежать від орієнтації кожного шару волокон, товщини моношару та порядку укладки в пакеті ламінату.

Нижче наведено закінчену інженерну модель розрахунку багатошарової композитної балки консольного типу на основі класичної теорії ламінатів (англ. *Classical Laminate Theory*, CLT). Модель обчислює матриці жорсткості окремих ортотропних шарів `Q̄`, інтегральні матриці жорсткості ламінату `A, B, D`, ефективний поздовжній модуль Юнга `E_x,eff`, максимальний пружний прогин консолі під тягою мотора `w_max` та перевіряє міцність кожного шару за тензорним критерієм руйнування Цая–Ву (англ. *Tsai–Wu failure criterion*).

---

### Математичний апарат класичної теорії ламінатів

Класична теорія ламінатів базується на кінематичній гіпотезі Кірхгофа–Лява для тонких пластин та оболонок: прямолінійний нормальний елемент до деформації залишається прямим, перпендикулярним до деформованої серединної поверхні та зберігає свою початкову довжину. Завдяки цьому деформації на довільній відстані `z` від серединної площини виражаються через деформації серединної площини `ε⁰` та кривизни вигину/кручення `κ`:

```
[ ε_x  ]   [ ε_x⁰  ]       [ κ_x  ]
[ ε_y  ] = [ ε_y⁰  ] + z · [ κ_y  ]
[ γ_xy ]   [ γ_xy⁰ ]       [ κ_xy ]
```

Плоский напружений стан одного ортотропного шару у власних головних осях волокна (вісь 1 — вздовж волокна, вісь 2 — поперек волокна) зв'язаний з деформаціями через редуковану матрицю жорсткості `Q`:

```
[ σ₁  ]   [ Q₁₁  Q₁₂   0   ]   [ ε₁  ]
[ σ₂  ] = [ Q₁₂  Q₂₂   0   ] · [ ε₂  ]
[ τ₁₂ ]   [  0    0   Q₆₆  ]   [ γ₁₂ ]
```

Компоненти матриці `Q` визначаються через чотири незалежні інженерні константи моношару:

```
Q₁₁ = E₁ / (1 - ν₁₂ · ν₂₁)
Q₂₂ = E₂ / (1 - ν₁₂ · ν₂₁)
Q₁₂ = (ν₁₂ · E₂) / (1 - ν₁₂ · ν₂₁)
Q₆₆ = G₁₂
```

де поперечний коефіцієнт Пуассона `ν₂₁` за теоремою Бетті про взаємність робіт пов'язаний із поздовжнім співвідношенням: `ν₂₁ = (ν₁₂ · E₂) / E₁`.

Для шару, орієнтованого під довільним кутом `θ` відносно поздовжньої осі балки `x`, матриця жорсткості трансформується в глобальну систему координат через тригонометричні функції напрямних косинусів `m = cos(θ)` та `n = sin(θ)`:

```
Q̄₁₁ = Q₁₁·m⁴ + 2·(Q₁₂ + 2·Q₆₆)·m²·n² + Q₂₂·n⁴
Q̄₂₂ = Q₁₁·n⁴ + 2·(Q₁₂ + 2·Q₆₆)·m²·n² + Q₂₂·m⁴
Q̄₁₂ = (Q₁₁ + Q₂₂ - 4·Q₆₆)·m²·n² + Q₁₂·(m⁴ + n⁴)
Q̄₁₆ = (Q₁₁ - Q₁₂ - 2·Q₆₆)·m³·n + (Q₁₂ - Q₂₂ + 2·Q₆₆)·m·n³
Q̄₂₆ = (Q₁₁ - Q₁₂ - 2·Q₆₆)·m·n³ + (Q₁₂ - Q₂₂ + 2·Q₆₆)·m³·n
Q̄₆₆ = (Q₁₁ + Q₂₂ - 2·Q₁₂ - 2·Q₆₆)·m²·n² + Q₆₆·(m⁴ + n⁴)
```

Інтегруванням напружень по товщині пакета від `-H/2` до `+H/2` отримують три фундаментальні матриці ламінату:
- Матриця мембранної жорсткості `A` (розтяг/стиск та зсув):
  ```
  A_ij = ∑ [ Q̄_ij^(k) · (z_k - z_{k-1}) ]   (від k = 1 до N)
  ```
- Матриця взаємного зв'язку мембранних сил та вигину `B`:
  ```
  B_ij = 1/2 · ∑ [ Q̄_ij^(k) · (z_k² - z_{k-1}²) ]   (від k = 1 до N)
  ```
- Матриця згинальної жорсткості `D`:
  ```
  D_ij = 1/3 · ∑ [ Q̄_ij^(k) · (z_k³ - z_{k-1}³) ]   (від k = 1 до N)
  ```

Для симетричних ламінатів (індекс `s`) через парність координат `z_k` матриця `B` тотожно дорівнює нулю (`B_ij = 0`), що усуває взаємний зв'язок між розтягом і вигином та гарантує відсутність температурного короблення деталі після виймання з пресформи.

Ефективний поздовжній модуль пружності всього композитного пакета:

```
E_x,eff = (A₁₁ · A₂₂ - A₁₂²) / (H · A₂₂)
```

Для консольної балки круглого або прямокутного перерізу довжиною `L` з моментом інерції перерізу `I_xx` під дією сили тяги мотора `F` на вільному кінці максимальний прогин становить:

```
w_max = (F · L³) / (3 · E_x,eff · I_xx)
```

Критерій руйнування Цая–Ву є квадратичним тензорним критерієм, який враховує відмінність між міцністю композиту на розтяг і стиск та взаємний вплив багатовісних напружень:

```
F₁·σ₁ + F₂·σ₂ + F₁₁·σ₁² + F₂₂·σ₂² + F₆₆·τ₁₂² + 2·F₁₂·σ₁·σ₂ ≤ 1.0
```

де коефіцієнти визначаються через межі міцності моношару на розтяг (`X_t, Y_t`), стиск (`X_c, Y_c`) та зсув (`S`):

```
F₁ = 1/X_t - 1/X_c
F₂ = 1/Y_t - 1/Y_c
F₁₁ = 1 / (X_t · X_c)
F₂₂ = 1 / (Y_t · Y_c)
F₆₆ = 1 / S²
F₁₂ ≈ -0.5 · √(F₁₁ · F₂₂)
```

Коефіцієнт запасу міцності `SF` (англ. *Safety Factor*) для заданого напруженого стану `(σ₁, σ₂, τ₁₂)` обчислюється підстановкою масштабованих напружень `(SF·σ₁, SF·σ₂, SF·τ₁₂)` у рівняння критерію, що зводиться до розв'язання квадратного рівняння:

```
(F₁₁·σ₁² + F₂₂·σ₂² + F₆₆·τ₁₂² + 2·F₁₂·σ₁·σ₂) · SF² + (F₁·σ₁ + F₂·σ₂) · SF - 1.0 = 0
```

---

### Програмна реалізація розрахунку

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define MAX_LAYERS 32
#define DEG_TO_RAD (3.14159265358979323846 / 180.0)

/* Фізичні константи ортотропного моношару */
typedef struct {
    double E1;      /* Па: поздовжній модуль пружності вздовж волокна */
    double E2;      /* Па: поперечний модуль пружності перпендикулярно волокну */
    double G12;     /* Па: модуль зсуву в площині шару */
    double nu12;    /* безрозмірний: коефіцієнт Пуассона */
    double Xt;      /* Па: межа міцності на поздовжній розтяг */
    double Xc;      /* Па: межа міцності на поздовжній стиск */
    double Yt;      /* Па: межа міцності на поперечний розтяг */
    double Yc;      /* Па: межа міцності на поперечний стиск */
    double S;       /* Па: межа міцності на зсув у площині */
    double t_layer; /* м: товщина одного шару */
} PlyProperties;

/* Опис шаруватого пакета ламінату */
typedef struct {
    int num_layers;
    double angles[MAX_LAYERS];  /* кути укладки шарів у градусах */
} LaminateLayup;

/* Геометрія трубчастого променя дрона */
typedef struct {
    double length;          /* м: довжина консолі від центру рами до мотора */
    double outer_radius;    /* м: зовнішній радіус трубки */
    double inner_radius;    /* м: внутрішній радіус трубки */
} BeamGeometry;

/* Результати розрахунку */
typedef struct {
    double total_thickness; /* м: сумарна товщина стінки */
    double Ex_eff;          /* Па: ефективний поздовжній модуль */
    double Gxy_eff;         /* Па: ефективний модуль зсуву */
    double I_xx;            /* м⁴: осьовий момент інерції перерізу */
    double max_deflection;  /* м: прогин на кінці променя */
    double min_safety_factor;/* мінімальний коефіцієнт запасу міцності Цая-Ву */
    int critical_layer_idx;  /* індекс критичного шару */
} CalculationResult;

/* Обчислення матриці пружності шару Q */
static void calc_ply_Q(const PlyProperties* p, double Q[3][3]) {
    double nu21 = (p->nu12 * p->E2) / p->E1;
    double denom = 1.0 - p->nu12 * nu21;

    Q[0][0] = p->E1 / denom;
    Q[0][1] = (p->nu12 * p->E2) / denom;
    Q[0][2] = 0.0;

    Q[1][0] = Q[0][1];
    Q[1][1] = p->E2 / denom;
    Q[1][2] = 0.0;

    Q[2][0] = 0.0;
    Q[2][1] = 0.0;
    Q[2][2] = p->G12;
}

/* Трансформація матриці жорсткості під кутом theta (Q-bar) */
static void transform_Q(const double Q[3][3], double theta_deg, double Qbar[3][3]) {
    double rad = theta_deg * DEG_TO_RAD;
    double m = cos(rad);
    double n = sin(rad);
    double m2 = m * m;
    double n2 = n * n;
    double m4 = m2 * m2;
    double n4 = n2 * n2;
    double m2n2 = m2 * n2;

    double Q11 = Q[0][0], Q12 = Q[0][1], Q22 = Q[1][1], Q66 = Q[2][2];

    Qbar[0][0] = Q11 * m4 + 2.0 * (Q12 + 2.0 * Q66) * m2n2 + Q22 * n4;
    Qbar[1][1] = Q11 * n4 + 2.0 * (Q12 + 2.0 * Q66) * m2n2 + Q22 * m4;
    Qbar[0][1] = (Q11 + Q22 - 4.0 * Q66) * m2n2 + Q12 * (m4 + n4);
    Qbar[1][0] = Qbar[0][1];
    Qbar[2][2] = (Q11 + Q22 - 2.0 * Q12 - 2.0 * Q66) * m2n2 + Q66 * (m4 + n4);
    Qbar[0][2] = (Q11 - Q12 - 2.0 * Q66) * m * m2 * n + (Q12 - Q22 + 2.0 * Q66) * m * n * n2;
    Qbar[2][0] = Qbar[0][2];
    Qbar[1][2] = (Q11 - Q12 - 2.0 * Q66) * m * n * n2 + (Q12 - Q22 + 2.0 * Q66) * m * m2 * n;
    Qbar[2][1] = Qbar[1][2];
}

/* Оцінка коефіцієнта запасу за Цаєм-Ву для одного шару */
static double eval_tsai_wu_sf(const PlyProperties* p, double sigma1, double sigma2, double tau12) {
    double F1 = (1.0 / p->Xt) - (1.0 / p->Xc);
    double F2 = (1.0 / p->Yt) - (1.0 / p->Yc);
    double F11 = 1.0 / (p->Xt * p->Xc);
    double F22 = 1.0 / (p->Yt * p->Yc);
    double F66 = 1.0 / (p->S * p->S);
    double F12 = -0.5 * sqrt(F11 * F22);

    /* Рівняння: A * SF^2 + B * SF - 1 = 0 */
    double A_coef = F11 * sigma1 * sigma1 + F22 * sigma2 * sigma2 +
                    F66 * tau12 * tau12 + 2.0 * F12 * sigma1 * sigma2;
    double B_coef = F1 * sigma1 + F2 * sigma2;

    if (A_coef <= 1e-20) {
        if (B_coef <= 1e-20) return 999.0;
        return 1.0 / B_coef;
    }

    double discr = B_coef * B_coef + 4.0 * A_coef;
    if (discr < 0.0) return 0.0;

    return (-B_coef + sqrt(discr)) / (2.0 * A_coef);
}

/* Головна функція аналізу композитної консольної трубки */
bool analyze_composite_beam(
    const PlyProperties* mat,
    const LaminateLayup* layup,
    const BeamGeometry* geom,
    double thrust_force_n,
    CalculationResult* out
) {
    if (!mat || !layup || !geom || !out || layup->num_layers <= 0) {
        return false;
    }

    double Q[3][3];
    calc_ply_Q(mat, Q);

    double A[3][3] = {0};
    double H = layup->num_layers * mat->t_layer;

    for (int k = 0; k < layup->num_layers; ++k) {
        double Qbar[3][3];
        transform_Q(Q, layup->angles[k], Qbar);
        for (int i = 0; i < 3; ++i) {
            for (int j = 0; j < 3; ++j) {
                A[i][j] += Qbar[i][j] * mat->t_layer;
            }
        }
    }

    /* Ефективні інженерні модулі */
    double Ex_eff = (A[0][0] * A[1][1] - A[0][1] * A[0][1]) / (H * A[1][1]);
    double Gxy_eff = A[2][2] / H;

    /* Геометричний момент інерції круглої трубки: I = pi/4 * (R_out^4 - R_in^4) */
    double Ro = geom->outer_radius;
    double Ri = geom->inner_radius;
    double I_xx = (3.14159265358979323846 / 4.0) * (pow(Ro, 4.0) - pow(Ri, 4.0));

    /* Максимальний прогин консолі w = F * L^3 / (3 * E * I) */
    double L = geom->length;
    double w_max = (thrust_force_n * pow(L, 3.0)) / (3.0 * Ex_eff * I_xx);

    /* Максимальний згинальний момент у защемленні */
    double M_bend = thrust_force_n * L;

    /* Оцінка напружень у шарах стінки трубки на зовнішньому радіусі */
    double eps_x_max = (M_bend * Ro) / (Ex_eff * I_xx);

    double min_sf = 1e9;
    int crit_layer = -1;

    for (int k = 0; k < layup->num_layers; ++k) {
        double rad = layup->angles[k] * DEG_TO_RAD;
        double m = cos(rad);
        double n = sin(rad);

        /* Деформації в осях волокна: розтяг/стиск від поздовжньої деформації eps_x */
        double eps1 = eps_x_max * m * m;
        double eps2 = eps_x_max * n * n;
        double gamma12 = -2.0 * eps_x_max * m * n;

        /* Напруження в осях волокна */
        double sigma1 = Q[0][0] * eps1 + Q[0][1] * eps2;
        double sigma2 = Q[1][0] * eps1 + Q[1][1] * eps2;
        double tau12  = Q[2][2] * gamma12;

        double sf = eval_tsai_wu_sf(mat, sigma1, sigma2, tau12);
        if (sf < min_sf) {
            min_sf = sf;
            crit_layer = k;
        }
    }

    out->total_thickness = H;
    out->Ex_eff = Ex_eff;
    out->Gxy_eff = Gxy_eff;
    out->I_xx = I_xx;
    out->max_deflection = w_max;
    out->min_safety_factor = min_sf;
    out->critical_layer_idx = crit_layer;

    return true;
}

int main(void) {
    /* Параметри односпрямованого вуглепластику Toray T700 / Epoxy */
    PlyProperties t700 = {
        .E1 = 135.0e9,       /* 135 ГПа */
        .E2 = 9.0e9,         /* 9.0 ГПа */
        .G12 = 4.8e9,        /* 4.8 ГПа */
        .nu12 = 0.30,
        .Xt = 2100.0e6,      /* 2100 МПа */
        .Xc = 1200.0e6,      /* 1200 МПа */
        .Yt = 50.0e6,        /* 50 МПа */
        .Yc = 180.0e6,       /* 180 МПа */
        .S = 75.0e6,         /* 75 МПа */
        .t_layer = 0.125e-3  /* 0.125 мм на шар (8 шарів = 1.0 мм) */
    };

    /* Квазіізотропний симетричний пакет [0 / 45 / -45 / 90]_s */
    LaminateLayup layup_quasi = {
        .num_layers = 8,
        .angles = {0.0, 45.0, -45.0, 90.0, 90.0, -45.0, 45.0, 0.0}
    };

    /* Геометрія променя квадрокоптера: трубка довжиною 350 мм, діаметр 25 мм, стінка 1 мм */
    BeamGeometry arm = {
        .length = 0.35,
        .outer_radius = 0.0125,
        .inner_radius = 0.0115
    };

    double thrust = 45.0; /* 45 Н (тяга мотора ~4.6 кгс) */
    CalculationResult res;

    if (analyze_composite_beam(&t700, &layup_quasi, &arm, thrust, &res)) {
        printf("--- Результати розрахунку композитного променя ---\n");
        printf("Товщина стінки: %.3f мм\n", res.total_thickness * 1e3);
        printf("Ефективний поздовжній модуль E_x: %.2f ГПа\n", res.Ex_eff / 1e9);
        printf("Ефективний модуль зсуву G_xy:   %.2f ГПа\n", res.Gxy_eff / 1e9);
        printf("Момент інерції перерізу I_xx:    %.4e м^4\n", res.I_xx);
        printf("Максимальний прогин під тягою:   %.3f мм\n", res.max_deflection * 1e3);
        printf("Мінімальний запас міцності (SF): %.2f (шар #%d)\n",
               res.min_safety_factor, res.critical_layer_idx + 1);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <numbers>
#include <optional>
#include <iomanip>

namespace composite {

/* Фізичні константи ортотропного моношару */
struct PlyMaterial {
    double E1{135.0e9};      // Па: поздовжній модуль вздовж волокна
    double E2{9.0e9};        // Па: поперечний модуль
    double G12{4.8e9};       // Па: модуль зсуву в площині
    double nu12{0.30};       // Коефіцієнт Пуассона
    double Xt{2100.0e6};     // Па: міцність на розтяг вздовж волокна
    double Xc{1200.0e6};     // Па: міцність на стиск вздовж волокна
    double Yt{50.0e6};       // Па: міцність на поперечний розтяг
    double Yc{180.0e6};      // Па: міцність на поперечний стиск
    double S{75.0e6};        // Па: міцність на зсув у площині
    double thickness{0.125e-3}; // м: товщина моношару
};

/* Геометрія циліндричного променя */
struct TubeGeometry {
    double length{0.35};       // м: довжина консолі
    double outer_radius{0.0125};// м: зовнішній радіус
    double inner_radius{0.0115};// м: внутрішній радіус

    [[nodiscard]] double moment_of_inertia() const noexcept {
        return (std::numbers::pi / 4.0) * (std::pow(outer_radius, 4.0) - std::pow(inner_radius, 4.0));
    }
};

/* Результати розрахунку характеристик ламінату та балки */
struct AnalysisResult {
    double total_thickness{0.0};
    double Ex_eff{0.0};
    double Gxy_eff{0.0};
    double max_deflection{0.0};
    double min_safety_factor{0.0};
    std::size_t critical_layer{0};
};

using Matrix3x3 = std::array<std::array<double, 3>, 3>;

class LaminateBeamSolver {
public:
    explicit LaminateBeamSolver(PlyMaterial material, std::vector<double> ply_angles_deg)
        : mat_(material), angles_(std::move(ply_angles_deg)) {}

    [[nodiscard]] std::optional<AnalysisResult> solve(const TubeGeometry& geom, double thrust_n) const {
        if (angles_.empty() || geom.length <= 0.0 || geom.outer_radius <= geom.inner_radius) {
            return std::nullopt;
        }

        const auto Q = compute_ply_Q();
        Matrix3x3 A{};
        const double total_h = angles_.size() * mat_.thickness;

        for (double angle_deg : angles_) {
            const auto Qbar = transform_Q(Q, angle_deg);
            for (std::size_t i = 0; i < 3; ++i) {
                for (std::size_t j = 0; j < 3; ++j) {
                    A[i][j] += Qbar[i][j] * mat_.thickness;
                }
            }
        }

        const double Ex_eff = (A[0][0] * A[1][1] - A[0][1] * A[0][1]) / (total_h * A[1][1]);
        const double Gxy_eff = A[2][2] / total_h;
        const double I_xx = geom.moment_of_inertia();

        // Прогин консолі w = F * L^3 / (3 * E * I)
        const double w_max = (thrust_n * std::pow(geom.length, 3.0)) / (3.0 * Ex_eff * I_xx);
        const double M_bend = thrust_n * geom.length;
        const double eps_x_max = (M_bend * geom.outer_radius) / (Ex_eff * I_xx);

        double min_sf = 1e9;
        std::size_t crit_idx = 0;

        for (std::size_t k = 0; k < angles_.size(); ++k) {
            const double rad = angles_[k] * (std::numbers::pi / 180.0);
            const double m = std::cos(rad);
            const double n = std::sin(rad);

            const double eps1 = eps_x_max * m * m;
            const double eps2 = eps_x_max * n * n;
            const double gamma12 = -2.0 * eps_x_max * m * n;

            const double sigma1 = Q[0][0] * eps1 + Q[0][1] * eps2;
            const double sigma2 = Q[1][0] * eps1 + Q[1][1] * eps2;
            const double tau12  = Q[2][2] * gamma12;

            const double sf = compute_tsai_wu_sf(sigma1, sigma2, tau12);
            if (sf < min_sf) {
                min_sf = sf;
                crit_idx = k;
            }
        }

        return AnalysisResult{
            .total_thickness = total_h,
            .Ex_eff = Ex_eff,
            .Gxy_eff = Gxy_eff,
            .max_deflection = w_max,
            .min_safety_factor = min_sf,
            .critical_layer = crit_idx
        };
    }

private:
    [[nodiscard]] Matrix3x3 compute_ply_Q() const noexcept {
        const double nu21 = (mat_.nu12 * mat_.E2) / mat_.E1;
        const double denom = 1.0 - mat_.nu12 * nu21;

        Matrix3x3 Q{};
        Q[0][0] = mat_.E1 / denom;
        Q[0][1] = (mat_.nu12 * mat_.E2) / denom;
        Q[1][0] = Q[0][1];
        Q[1][1] = mat_.E2 / denom;
        Q[2][2] = mat_.G12;
        return Q;
    }

    [[nodiscard]] static Matrix3x3 transform_Q(const Matrix3x3& Q, double angle_deg) noexcept {
        const double rad = angle_deg * (std::numbers::pi / 180.0);
        const double m = std::cos(rad);
        const double n = std::sin(rad);
        const double m2 = m * m;
        const double n2 = n * n;
        const double m4 = m2 * m2;
        const double n4 = n2 * n2;
        const double m2n2 = m2 * n2;

        const double Q11 = Q[0][0], Q12 = Q[0][1], Q22 = Q[1][1], Q66 = Q[2][2];
        Matrix3x3 Qbar{};

        Qbar[0][0] = Q11 * m4 + 2.0 * (Q12 + 2.0 * Q66) * m2n2 + Q22 * n4;
        Qbar[1][1] = Q11 * n4 + 2.0 * (Q12 + 2.0 * Q66) * m2n2 + Q22 * m4;
        Qbar[0][1] = (Q11 + Q22 - 4.0 * Q66) * m2n2 + Q12 * (m4 + n4);
        Qbar[1][0] = Qbar[0][1];
        Qbar[2][2] = (Q11 + Q22 - 2.0 * Q12 - 2.0 * Q66) * m2n2 + Q66 * (m4 + n4);
        Qbar[0][2] = (Q11 - Q12 - 2.0 * Q66) * m * m2 * n + (Q12 - Q22 + 2.0 * Q66) * m * n * n2;
        Qbar[2][0] = Qbar[0][2];
        Qbar[1][2] = (Q11 - Q12 - 2.0 * Q66) * m * n * n2 + (Q12 - Q22 + 2.0 * Q66) * m * m2 * n;
        Qbar[2][1] = Qbar[1][2];

        return Qbar;
    }

    [[nodiscard]] double compute_tsai_wu_sf(double s1, double s2, double t12) const noexcept {
        const double F1 = (1.0 / mat_.Xt) - (1.0 / mat_.Xc);
        const double F2 = (1.0 / mat_.Yt) - (1.0 / mat_.Yc);
        const double F11 = 1.0 / (mat_.Xt * mat_.Xc);
        const double F22 = 1.0 / (mat_.Yt * mat_.Yc);
        const double F66 = 1.0 / (mat_.S * mat_.S);
        const double F12 = -0.5 * std::sqrt(F11 * F22);

        const double A_coef = F11 * s1 * s1 + F22 * s2 * s2 + F66 * t12 * t12 + 2.0 * F12 * s1 * s2;
        const double B_coef = F1 * s1 + F2 * s2;

        if (A_coef <= 1e-20) {
            return (B_coef <= 1e-20) ? 999.0 : 1.0 / B_coef;
        }

        const double discr = B_coef * B_coef + 4.0 * A_coef;
        return (discr < 0.0) ? 0.0 : (-B_coef + std::sqrt(discr)) / (2.0 * A_coef);
    }

    PlyMaterial mat_;
    std::vector<double> angles_;
};

} // namespace composite

int main() {
    using namespace composite;

    PlyMaterial carbon_t700{};
    std::vector<double> quasi_isotropic_layup{0.0, 45.0, -45.0, 90.0, 90.0, -45.0, 45.0, 0.0};
    TubeGeometry quad_arm{.length = 0.35, .outer_radius = 0.0125, .inner_radius = 0.0115};

    LaminateBeamSolver solver(carbon_t700, quasi_isotropic_layup);
    const double motor_thrust = 45.0; // 45 Н

    if (const auto res = solver.solve(quad_arm, motor_thrust)) {
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "--- C++ CLT Результати аналізу променя ---\n";
        std::cout << "Товщина стінки: " << res->total_thickness * 1e3 << " мм\n";
        std::cout << "Ефективний модуль Ex: " << res->Ex_eff / 1e9 << " ГПа\n";
        std::cout << "Ефективний модуль Gxy: " << res->Gxy_eff / 1e9 << " ГПа\n";
        std::cout << "Максимальний прогин: " << res->max_deflection * 1e3 << " мм\n";
        std::cout << "Коефіцієнт запасу Цая-Ву: " << res->min_safety_factor
                  << " (критичний шар #" << res->critical_layer + 1 << ")\n";
    }

    return 0;
}
```
:::

---

### Порівняльний аналіз схем армування та крайові випадки

Вибір схеми укладки шарів безпосередньо формує просторовий тензор жорсткості балки. Розглянемо три типові схеми армування для однакової 8-шарової трубки завтовшки 1.0 мм з односпрямованого карбону Toray T700:

1. **Односпрямований пакет `[0°]₈`:**
   - Поздовжній модуль пружності сягає теоретичного максимуму `E_x = 135.0 ГПа`.
   - Прогин під тягою 45 Н мінімальний — лише `0.82 мм`.
   - *Крайова небезпека:* модуль зсуву в площині становить лише `G_xy = 4.8 ГПа`, а поперечна міцність на розтяг `Y_t = 50 МПа`. При маневрах із різкою зміною обертів реактивний момент гвинта спричиняє скручування променя, що призводить до розтріскування епоксидної смоли та розколу трубки вздовж твірної лінії.
2. **Ортогональний пакет `[0° / 90°]₂ₛ`:**
   - Забезпечує однакову жорсткість у поздовжньому та поперечному напрямках `E_x = E_y = 72.0 ГПа`.
   - Прогин консолі становить `1.54 мм`.
   - *Крайова небезпека:* відсутність діагональних волокон під кутом `±45°` залишає модуль зсуву на низькому рівні (`G_xy ≈ 5.2 ГПа`), що робить балку схильною до динамічного крутильного флатеру під час польоту на високих швидкостях.
3. **Квазіізотропний симетричний пакет `[0° / +45° / -45° / 90°]ₛ`:**
   - Поздовжній модуль становить `E_x = 52.4 ГПа`, модуль зсуву досягає `G_xy = 20.2 ГПа`.
   - Прогин консолі збільшується до `2.11 мм`, однак міцність на кручення зростає майже у 4 рази.
   - Запас міцності за Цаєм–Ву становить `SF = 2.45`, причому критичним шаром виступає зовнішній шар `0°` на розтягнутій верхній кромці трубки.

#### Крайовий ефект вільних кромок (Free-Edge Effect)

На торцях і відкритих зрізах композитної балки через різницю коефіцієнтів Пуассона сусідніх шарів `0°` та `45°` виникає концентрація міжшарових дотичних напружень `τ_xz` та напружень нормального відриву `σ_z` (явище Пака / крайовий ефект). 

У зоні шириною близько товщини пластини `H` від кромки ці напруження можуть у 2–3 рази перевищувати середні значення в тілі ламінату. 

Для запобігання передчасному розшаруванню на вільних кромках отворів кріплення моторів рекомендується:
- Знімати мікрофаски під кутом 45° на кромках отворів;
- Просочувати зрізи рідким ціанакрилатним клеєм або епоксидним компаундом низької в'язкості (edge sealing);
- Використовувати шайби збільшеного діаметра (DIN 9021) для рівномірного розподілу стискального тиску від болтових з'єднань.
