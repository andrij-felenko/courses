# ⚙️ Чисельне моделювання кривих намагнічування та поверхні енергії анізотропії

Чисельне моделювання процесів намагнічування монокристалів дозволяє розраховувати петлі магнітного гістерезису, криві намагнічування `M(H)`, знаходити орієнтацію вектора намагніченості у довільно орієнтованих зовнішніх полях та будувати тривимірні кутові поверхні енергії анізотропії `E_A(θ, φ)`. В основі обчислювального алгоритму лежить знаходження конфігурації локального або глобального мінімуму повної вільної енергії системи при кожному послідовному кроці зміни зовнішнього магнітного поля.

## Алгоритм мінімізації енергії та математична модель

Повна густина вільної енергії `E(θ, φ)` однодоменного кристала у зовнішньому магнітному полі `H` складається з двох основних внесків: енергії магнітокристалічної анізотропії `E_A(θ, φ)` та зеєманівської енергії взаємодії намагніченості з полем `E_Z(θ, φ)`:

```
E(θ, φ) = E_A(θ, φ) - μ₀·M_s · (m · H)
```

де `m = (sin θ · cos φ, sin θ · sin φ, cos θ)` — одиничний вектор намагніченості, а `μ₀ = 1.2566×10⁻⁶ Гн/м` — магнітна стала.

Для одноосьового кристала, коли вектор поля `H` прикладено у площині, що містить легку вісь під кутом `ψ`, енергія залежить лише від одного полярного кута `θ`:

```
E(θ) = K₁·sin²θ + K₂·sin⁴θ - μ₀·M_s·H · cos(ψ - θ)
```

Для кубічних кристалів (наприклад, заліза чи нікелю) енергія є тривимірною функцією двох кутів `(θ, φ)`:

```
E_A(θ, φ) = K₁·(sin⁴θ · cos²φ · sin²φ + sin²θ · cos²θ) + K₂·sin⁴θ · cos²θ · cos²φ · sin²φ
```

Алгоритм чисельної симуляції кривої намагнічування реалізує таку послідовність кроків:
1. **Ініціалізація матеріальних параметрів.** Задаються намагніченість насичення `M_s`, феноменологічні константи анізотропії `K₁, K₂`, тип симетрії кристала (одноосьова чи кубічна), а також напрямок зовнішнього поля `ψ` відносно легкої осі.
2. **Дискретизація поля.** Зовнішнє поле `H` змінюється від `-H_max` до `+H_max` із фіксованим кроком `ΔH`.
3. **Локальна оптимізація.** На кожному кроці за полем шукається кут `θ_min`, який мінімізує енергію `E(θ)`. Для відтворення магнітного гістерезису пошук починається з кута `θ`, знайденого на попередньому кроці поля (принцип квазістатичної еволюції локального мінімуму). Мінімізація здійснюється методом золотого перетину (1D) або методом модифікованого градієнтного спуску (2D).
4. **Проекція намагніченості.** Проекція вектора намагніченості на напрямок вимірювального поля обчислюється за формулою `M_H = M_s · cos(ψ - θ_min)`.

Нижче подано повну програмну реалізацію чисельного моделятора мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PI 3.14159265358979323846
#define MU_0 1.2566370614359173e-6

typedef enum {
    ANISOTROPY_UNIAXIAL,
    ANISOTROPY_CUBIC
} AnisotropyType;

typedef struct {
    double Ms;              /* Saturation magnetization (A/m) */
    double K1;              /* First anisotropy constant (J/m^3) */
    double K2;              /* Second anisotropy constant (J/m^3) */
    AnisotropyType type;
} MagneticMaterial;

typedef struct {
    double H_amp;           /* Field amplitude (A/m) */
    double psi_deg;         /* Field angle in degrees relative to z-axis */
} AppliedField;

/* Calculate anisotropy energy density E_A */
double calc_anisotropy_energy(const MagneticMaterial* mat, double theta, double phi) {
    if (mat->type == ANISOTROPY_UNIAXIAL) {
        double sin_t = sin(theta);
        double sin2_t = sin_t * sin_t;
        double sin4_t = sin2_t * sin4_t;
        return mat->K1 * sin2_t + mat->K2 * sin4_t;
    } else {
        /* Cubic anisotropy */
        double a1 = sin(theta) * cos(phi);
        double a2 = sin(theta) * sin(phi);
        double a3 = cos(theta);
        double a1_2 = a1 * a1, a2_2 = a2 * a2, a3_2 = a3 * a3;
        return mat->K1 * (a1_2 * a2_2 + a2_2 * a3_2 + a3_2 * a1_2) + mat->K2 * (a1_2 * a2_2 * a3_2);
    }
}

/* Calculate total free energy density E = E_A + E_Zeeman */
double calc_total_energy_uniaxial(const MagneticMaterial* mat, double H, double psi, double theta) {
    double E_A = mat->K1 * sin(theta) * sin(theta) + mat->K2 * pow(sin(theta), 4);
    double E_Z = -MU_0 * mat->Ms * H * cos(psi - theta);
    return E_A + E_Z;
}

/* Golden section search for local minimum of 1D energy function */
double find_energy_minimum_1d(const MagneticMaterial* mat, double H, double psi, double theta_start) {
    double a = theta_start - PI / 4.0;
    double b = theta_start + PI / 4.0;
    const double phi_gold = (1.0 + sqrt(5.0)) / 2.0;
    const double resphi = 2.0 - phi_gold;
    
    double x1 = a + resphi * (b - a);
    double x2 = b - resphi * (b - a);
    double f1 = calc_total_energy_uniaxial(mat, H, psi, x1);
    double f2 = calc_total_energy_uniaxial(mat, H, psi, x2);
    
    for (int iter = 0; iter < 60; ++iter) {
        if (f1 < f2) {
            b = x2;
            x2 = x1;
            f2 = f1;
            x1 = a + resphi * (b - a);
            f1 = calc_total_energy_uniaxial(mat, H, psi, x1);
        } else {
            a = x1;
            x1 = x2;
            f1 = f2;
            x2 = b - resphi * (b - a);
            f2 = calc_total_energy_uniaxial(mat, H, psi, x2);
        }
        if (fabs(b - a) < 1e-7) break;
    }
    return (a + b) / 2.0;
}

/* Simulate M(H) magnetization curve */
void simulate_magnetization_curve(const MagneticMaterial* mat, double psi_deg, double H_max, int steps) {
    double psi = psi_deg * PI / 180.0;
    double theta_curr = (cos(psi) >= 0) ? 0.0 : PI;
    double H_step = 2.0 * H_max / steps;

    printf("# H (A/m)\tM_parallel / M_s\tTheta (deg)\n");
    for (int i = 0; i <= steps; ++i) {
        double H = -H_max + i * H_step;
        theta_curr = find_energy_minimum_1d(mat, H, psi, theta_curr);
        double m_parallel = cos(psi - theta_curr);
        printf("%.2f\t%.6f\t%.2f\n", H, m_parallel, theta_curr * 180.0 / PI);
    }
}

int main(void) {
    /* Cobalt parameters: Ms = 1.4e6 A/m, K1 = 4.1e5 J/m^3, K2 = 1.0e5 J/m^3 */
    MagneticMaterial cobalt = {
        .Ms = 1.4e6,
        .K1 = 4.1e5,
        .K2 = 1.0e5,
        .type = ANISOTROPY_UNIAXIAL
    };

    printf("=== Симуляція намагнічування Co уздовж важкої осі (90 град) ===\n");
    simulate_magnetization_curve(&cobalt, 90.0, 1.2e6, 50);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <algorithm>

enum class AnisotropySymmetry {
    Uniaxial,
    Cubic
};

struct MagneticParameters {
    double Ms{1.4e6};              // A/m
    double K1{4.1e5};              // J/m^3
    double K2{1.0e5};              // J/m^3
    AnisotropySymmetry symmetry{AnisotropySymmetry::Uniaxial};
};

class MagnetizationSimulator {
public:
    static constexpr double Mu0 = 1.2566370614359173e-6;

    explicit MagnetizationSimulator(MagneticParameters params) 
        : params_(params) {}

    [[nodiscard]] double anisotropyEnergy(double theta, double phi = 0.0) const noexcept {
        if (params_.symmetry == AnisotropySymmetry::Uniaxial) {
            const double sinT = std::sin(theta);
            const double sin2T = sinT * sinT;
            return params_.K1 * sin2T + params_.K2 * sin2T * sin2T;
        } else {
            const double a1 = std::sin(theta) * std::cos(phi);
            const double a2 = std::sin(theta) * std::sin(phi);
            const double a3 = std::cos(theta);
            const double a1_2 = a1 * a1, a2_2 = a2 * a2, a3_2 = a3 * a3;
            return params_.K1 * (a1_2 * a2_2 + a2_2 * a3_2 + a3_2 * a1_2) 
                 + params_.K2 * (a1_2 * a2_2 * a3_2);
        }
    }

    [[nodiscard]] double totalEnergy(double H, double psi, double theta) const noexcept {
        const double E_A = anisotropyEnergy(theta);
        const double E_Z = -Mu0 * params_.Ms * H * std::cos(psi - theta);
        return E_A + E_Z;
    }

    struct SimulationPoint {
        double H_field;
        double m_normalized;
        double theta_rad;
    };

    [[nodiscard]] std::vector<SimulationPoint> runHysteresisLoop(
        double psiDegrees, double maxHField, std::size_t steps) const 
    {
        std::vector<SimulationPoint> curve;
        curve.reserve(steps + 1);

        const double psi = psiDegrees * std::numbers::pi / 180.0;
        double thetaCurrent = (std::cos(psi) >= 0.0) ? 0.0 : std::numbers::pi;
        const double stepH = 2.0 * maxHField / static_cast<double>(steps);

        for (std::size_t i = 0; i <= steps; ++i) {
            const double H = -maxHField + static_cast<double>(i) * stepH;
            thetaCurrent = minimizeEnergy1D(H, psi, thetaCurrent);
            const double mParallel = std::cos(psi - thetaCurrent);
            curve.push_back({H, mParallel, thetaCurrent});
        }
        return curve;
    }

private:
    MagneticParameters params_;

    [[nodiscard]] double minimizeEnergy1D(double H, double psi, double thetaGuess) const {
        double a = thetaGuess - std::numbers::pi / 4.0;
        double b = thetaGuess + std::numbers::pi / 4.0;
        constexpr double GoldenRatio = 1.618033988749895;
        constexpr double ResPhi = 2.0 - GoldenRatio;

        double x1 = a + ResPhi * (b - a);
        double x2 = b - ResPhi * (b - a);
        double f1 = totalEnergy(H, psi, x1);
        double f2 = totalEnergy(H, psi, x2);

        for (int iter = 0; iter < 80; ++iter) {
            if (f1 < f2) {
                b = x2;
                x2 = x1;
                f2 = f1;
                x1 = a + ResPhi * (b - a);
                f1 = totalEnergy(H, psi, x1);
            } else {
                a = x1;
                x1 = x2;
                f1 = f2;
                x2 = b - ResPhi * (b - a);
                f2 = totalEnergy(H, psi, x2);
            }
            if (std::abs(b - a) < 1e-8) break;
        }
        return (a + b) / 2.0;
    }
};

int main() {
    MagneticParameters feParams{
        .Ms = 1.71e6,
        .K1 = 4.8e4,
        .K2 = 0.5e4,
        .symmetry = AnisotropySymmetry::Uniaxial
    };

    MagnetizationSimulator simulator(feParams);
    auto results = simulator.runHysteresisLoop(45.0, 5e5, 20);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "H (A/m)\t\tM / Ms\t\tTheta (rad)\n";
    for (const auto& point : results) {
        std::cout << point.H_field << "\t\t" 
                  << point.m_normalized << "\t\t" 
                  << point.theta_rad << "\n";
    }
    return 0;
}
```
:::

## Фізичний аналіз та інженерні пастки моделювання

При реалізації обчислювальних пакетів мікромагнетизму (включаючи комерційні та відкриті рішення, такі як Mumax3 чи OOMMF) виникає низка критичних питань, пов'язаних із чисельною стійкістю та фізичною коректністю.

### 1. Застрягання у метастабільних мінімумах

Повна енергетична поверхня `E(θ, φ)` у присутності анізотропії має декілька потенціальних ям. При використанні локальних методів оптимізації (таких як метод золотого перетину чи градієнтний спуск) алгоритм залишається у початковій потенціальній ямі доти, доки енергетичний бар'єр між станами не зникне під дією зовнішнього поля. 

Для симуляції магнітного гістерезису це є фізично правильним: метастабільний стан відповідає затриманню перемагнічування та утворенню коерцитивної сили. Проте, якщо метою розрахунку є визначення глобального основного стану при даній температурі, локальні алгоритми дають помилковий результат, і необхідно застосовувати методи стохастичної оптимізації (моделювання відпалу або алгоритми Монте-Карло).

### 2. Усунення координатних сингулярностей

При розрахунку 3D-динаміки намагніченості у сферичних координатах `(θ, φ)` виникає сингулярність полярної осі: при `θ = 0` та `θ = π` градієнт енергії за азимутальним кутом `∂E / ∂φ` прямує до нуля незалежно від орієнтації флуктуації. Це призводить до чисельної нестабільності при інтегруванні рівняння Ландау — Ліфшиця — Ґільберта (LLG).

Щоб уникнути полярних сингулярностей, у сучасних мікромагнітних симуляторах використовують декартові компоненти нормалізованого вектора намагніченості `m = (m_x, m_y, m_z)` зі строгою умовою збереження норми `|m| = 1` на кожному часовому кроці, або кватерніонне представлення обертань.

### 3. Роль кроку за полем та теплових флуктуацій

При чисельному розрахунку стрибка Стонера — Вольфарта занадто великий крок за полем `ΔH` призводить до завищення обчисленої коерцитивної сили, оскільки алгоритм «перелітає» точку втрати стійкості. У реальних матеріалах наявність теплових флуктуацій при `T > 0 K` допомагає вектору намагніченості подолати низький енергетичний бар'єр ще до досягнення чисто адіабатичного поля переключення (термоактивоване перемагнічування за законом Неєля — Брауна).

### 4. Динаміка релаксації за рівнянням Ландау — Ліфшиця — Ґільберта (LLG)

У динамічних симуляторах замість прямого квазістатичного пошуку мінімуму енергії розв'язують диференціальне рівняння Ландау — Ліфшиця — Ґільберта:

```
dm/dt = - γ · (m × H_eff) + α · (m × dm/dt)             [рівняння прецесії та релаксації LLG]
```

де `γ` — гіромагнітне відношення, `α` — безрозмірний коефіцієнт затухання Ґільберта, а `H_eff = H_зовн + H_A + H_обмін + H_демаг` — сумарне ефективне поле. Перший член описує консервативну прецесію вектора намагніченості навколо ефективного поля анізотропії, а другий член — дисипативне затухання, яке спірально спирає вектор намагніченості на дно потенціальної ями анізотропії.

### 5. Обчислювальна складність та оптимізація 2D-пошуку

Часова складність знаходження квазістатичної кривої намагнічування для `N` кроків зовнішнього поля становить `O(N · K)`, де `K` — кількість ітерацій одновимірного алгоритму пошуку мінімуму (для методу золотого перетину `K ≈ 60` забезпечує точність `10⁻⁷ rad`). 

Для тривимірних матеріалів із кубічною анізотропією 2D-пошук на сітці `(θ, φ)` вимагає комбінації методу Ньютона — Рафсона з обчисленням гесіана (матриці Других похідних `∂²E / ∂θ²`, `∂²E / ∂φ²`, `∂²E / (∂θ ∂φ)`). Від'ємний визначник гесіана вказує на точкову сідловину, а додатний визначник із додатною першою діагональною компонентою гарантує локальний мінімум енергії.

### 6. Врахування розмагнічувальних полів форми (Форм-анізотропія)

У реальних зразках скінченного розміру окрім магнітокристалічної анізотропії виникає **анізотропія форми** (форм-анізотропія), спричинена магнітостатичними розмагнічувальними полями `H_демаг = - N_d · M`. Для тонкої плівки або видовженого циліндра форм-анізотропія додає ефективну константу анізотропії `K_shape = (1/2) · μ₀ · M_s² · (N_y - N_x)`. 

При чисельному моделюванні кристалів важливим є розмежування внесків: магнітокристалічна анізотропія є фундаментальною властивістю атомної ґратки матеріалу, тоді як форм-анізотропія залежить виключно від макроскопічних геометрії та пропорцій зразка.
