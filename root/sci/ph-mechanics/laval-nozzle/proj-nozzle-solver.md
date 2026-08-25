# ⚙️ Чисельний розрахунок геометрії та газодинамічного профілю сопла Лаваля

Алгоритмічна вставка містить детальний опис чисельного модуля розв'язання нелінійних газодинамічних рівнянь для 1D-симуляції течії газу у соплі Лаваля. У тексті розглянуто обчислювальні алгоритми, математичні методом ітерацій Ньютона — Рафсона та наведено виробничі реалізації мовами C та C++ з урахуванням ідіоматичних вимог обох мов.

## 1. Постановка обчислювальної задачі та математичний метод

Розглянемо задачу одновимірного чисельного моделювання квазіодновимірної ізоентропійної течії стисливого газу у соплі змінного перерізу. Сопло задано дискретною розрахунковою сіткою точок уздовж поздовжньої осі `x ∈ [0, L]`, для кожної з яких відома площа поперечного перерізу `A(x)`.

На вхід чисельного модуля подаються такі початкові термодинамічні та геометричні дані:

- Показник адіабати газу `γ = C_p / C_v` (наприклад, `γ = 1.4` для повітря).
- Питома газова стала `R` (наприклад, `R = 287.05` Дж/(кг·К) для повітря).
- Повний тиск гальмування на вході `P₀` (Па).
- Повна температура гальмування на вході `T₀` (К).
- Протитиск довкілля на зрізі `P_amb` (Па).
- Масив координат `x` та відповідних площ `A(x)`.
- Індекс критичного перерізу `throat_idx`, у якому площа є мінімальною `A(throat_idx) = A*`.

Обчислювальний модуль має розрахувати для кожної точки сітки:
1. Місцеве число Маха `M(x)`.
2. Статичний тиск `P(x)` (Па).
3. Статичну температуру `T(x)` (К).
4. Густину газу `ρ(x)` (кг/м³).
5. Швидкість потоку `u(x)` (м/с).

### 1.1 Математичний метод розв'язання трансцендентного рівняння

Рівняння зв'язку геометричного відношення площ `A / A*` та числа Маха `M` має трансцендентний вигляд:

```
A / A* = (1 / M) · [ (2 / (γ + 1)) · (1 + ((γ - 1) / 2) · M²) ]^( (γ + 1) / (2 · (γ - 1)) )
```

Для знаходження числа Маха `M` за відомим `A / A*` розв'язується рівняння нев'язки `F(M) = 0`:

```
F(M) = (1 / M) · [ (2 / (γ + 1)) · (1 + ((γ - 1) / 2) · M²) ]^( (γ + 1) / (2 · (γ - 1)) ) - (A / A*)
```

Похідна функції нев'язки за числом Маха `F'(M) = dF / dM` виражається аналітично:

```
F'(M) = (A / A*) · [ (M² - 1) / (M · (1 + ((γ - 1) / 2) · M²)) ]
```

Ітераційна формула Ньютона — Рафсона на кроці `k + 1` має вигляд:

```
M_{k+1} = M_k - F(M_k) / F'(M_k)
```

Завдяки використанню аналітичної похідної `F'(M)` метод Ньютона — Рафсона демонструє квадратичну швидкість збіжності (`||e_{k+1}|| ~ ||e_k||²`), що вимагає всього 4–6 ітерацій для досягнення машинного точності `10⁻¹²`.

### 1.2 Вибір початкового наближення та затискання гілок

Оскільки рівняння `F(M) = 0` має два математичні корені (дозвуковий `M < 1` та надзвуковий `M > 1`), вирішальне значення має вибір початкового наближення `M₀`:

- **До горловини (конфузорна частина, `x < x_throat`):** початкове наближення обирається на дозвуковій вітці `M₀ = 0.2`. Під час ітерацій діє обмеження `M < 1.0`.
- **У горловині (`x = x_throat`):** за визначенням `A = A*`, тому число Маха встановлюється строго `M = 1.0` без виконання ітерацій (щоб уникнути ділення на нуль в `F'(1) = 0`).
- **Після горловини (дифузорна частина, `x > x_throat`):** для розрахункового надзвукового режиму початкове наближення обирається на надзвуковій вітці `M₀ = 2.0`. Під час ітерацій діє обмеження `M > 1.0`.

Ітераційний процес зупиняється при досягненні точності `|F(M)| < 10⁻⁷` або при досягненні максимальної кількості ітерацій `MAX_ITER = 100`.

### 1.3 Алгоритм локалізації скачка ущільнення у перерозширеному режимі

У випадках, коли зовнішній протитиск `P_amb` є більшим за розрахунковий тиск на зрізі `P_exit`, але меншим за критичний тиск збігу дозвукового режиму, у дифузорі виникає прямий скачок ущільнення.

Алгоритм пошуку координат скачка `x_shock`:

1. Проводиться тестовий розрахунок повністю надзвукового розширення дифузора для всіх точок `i > throat_idx`.
2. Для кожного вузла сітки `i_s` у дифузорі гіпотетично припускається наявність скачка:
   - Обчислюються доскачкові параметри `M1 = M[i_s]`, `P1 = P[i_s]`.
   - Обчислюється стрибок параметрів за рівняннями Ренкіна — Гюгоньо:
     ```
     M2 = √[ ((γ - 1)·M1² + 2) / (2·γ·M1² - (γ - 1)) ]
     P2 = P1 · [ 1 + (2·γ / (γ + 1))·(M1² - 1) ]
     ```
   - За скачком потік продовжує рух як дозвуковий. Обчислюється ефективна критична площа `A*₂ > A*₁` для нового значення повного тиску `P0₂ < P0₁`.
   - Проводиться дозвуковий розрахунок від вузла `i_s` до зрізу `x_exit`.
3. Визначений тиск на зрізі `P_exit_calc(i_s)` порівнюється з протитиском `P_amb`.
4. Точка скачка `i_shock` відповідає кореню нев'язки `P_exit_calc(i_shock) = P_amb`, який знаходиться методом половинного ділення (дихотомії).

## 2. Реалізація симулятора течії (C та C++)

Нижче наведено паралельні реалізації газодинамічного симулятора мовами C та C++. 

У версії C висвітлено класичний процедурний підхід із явним управлінням пам'яттю, передачею структур за вказівниками та перевіркою кодів помилок. 

У версії C++ застосовано сучасні стандарти C++20: концепцію об'єктно-орієнтованого модуля, безпечні контейнери `std::vector`, обгортки `std::optional` та `std::span` для передачі неволодіючих зрізів масивів без накладних витрат на копіювання.

:::tabs
```c
/* nozzle_solver.c — Чисельний модуль розрахунку сопла Лаваля мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define MAX_POINTS 500
#define EPSILON 1e-7
#define MAX_ITER 100

typedef struct {
    double gamma;       /* Показник адіабати (напр. 1.4) */
    double R;           /* Газова стала, Дж/(кг·К) (напр. 287.05) */
    double P0;          /* Повний тиск на вході, Па */
    double T0;          /* Повна температура на вході, К */
    double P_amb;       /* Протитиск навколишнього середовища, Па */
} gas_props_t;

typedef struct {
    double x;           /* Координата уздовж осі, м */
    double A;           /* Площа поперечного перерізу, м² */
    double M;           /* Число Маха */
    double P;           /* Статичний тиск, Па */
    double T;           /* Статична температура, К */
    double rho;         /* Густина, кг/м³ */
    double u;           /* Швидкість, м/с */
    bool is_shock;      /* Прапорець скачка ущільнення */
} flow_point_t;

/* Обчислення відношення A / A* за числом Маха */
double area_ratio_from_mach(double M, double gamma) {
    if (M <= 0.0) return 1e9;
    double g_term = (2.0 / (gamma + 1.0)) * (1.0 + 0.5 * (gamma - 1.0) * M * M);
    double exp_val = (gamma + 1.0) / (2.0 * (gamma - 1.0));
    return (1.0 / M) * pow(g_term, exp_val);
}

/* Чисельний розв'язок M за заданим A / A* методом Ньютона — Рафсона */
double solve_mach_from_area_ratio(double AR, double gamma, bool is_supersonic) {
    if (fabs(AR - 1.0) < 1e-6) return 1.0;
    
    double M = is_supersonic ? 2.5 : 0.2;
    for (int iter = 0; iter < MAX_ITER; iter++) {
        double current_AR = area_ratio_from_mach(M, gamma);
        double dAR_dM = current_AR * (M * M - 1.0) / (M * (1.0 + 0.5 * (gamma - 1.0) * M * M));
        
        double f = current_AR - AR;
        if (fabs(f) < EPSILON) break;
        
        M = M - f / dAR_dM;
        
        /* Затискання гілок */
        if (!is_supersonic && M >= 1.0) M = 0.9999;
        if (is_supersonic && M <= 1.0) M = 1.0001;
    }
    return M;
}

/* Обчислення термодинамічних параметрів за числом Маха */
void compute_point_state(flow_point_t *pt, double P0, double T0, double gamma, double R) {
    double M = pt->M;
    double temp_ratio = 1.0 / (1.0 + 0.5 * (gamma - 1.0) * M * M);
    double press_ratio = pow(temp_ratio, gamma / (gamma - 1.0));
    
    pt->T = T0 * temp_ratio;
    pt->P = P0 * press_ratio;
    pt->rho = pt->P / (R * pt->T);
    double a = sqrt(gamma * R * pt->T);
    pt->u = M * a;
}

/* Основний розрахунок 1D профілю сопла */
bool solve_nozzle_flow(const gas_props_t *gas, const double *x_arr, const double *A_arr, 
                       int num_pts, int throat_idx, flow_point_t *out_mesh) {
    if (!gas || !x_arr || !A_arr || !out_mesh || num_pts <= 0) return false;
    
    double A_throat = A_arr[throat_idx];
    
    for (int i = 0; i < num_pts; i++) {
        out_mesh[i].x = x_arr[i];
        out_mesh[i].A = A_arr[i];
        out_mesh[i].is_shock = false;
        
        double AR = A_arr[i] / A_throat;
        bool is_super = (i > throat_idx);
        
        out_mesh[i].M = solve_mach_from_area_ratio(AR, gas->gamma, is_super);
        compute_point_state(&out_mesh[i], gas->P0, gas->T0, gas->gamma, gas->R);
    }
    return true;
}

int main(void) {
    gas_props_t air = { .gamma = 1.4, .R = 287.05, .P0 = 1000000.0, .T0 = 300.0, .P_amb = 101325.0 };
    
    int n = 11;
    double x[11] = { 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0 };
    double A[11] = { 0.02, 0.015, 0.012, 0.01, 0.011, 0.014, 0.018, 0.023, 0.029, 0.035, 0.04 };
    int throat_index = 3; /* A = 0.01 в x = 0.3 */
    
    flow_point_t mesh[11];
    if (solve_nozzle_flow(&air, x, A, n, throat_index, mesh)) {
        printf("--- РОЗРАХУНОК СОПЛА ЛАВАЛЯ (C) ---\n");
        printf("x(m)\tA(m2)\tMach\tP(kPa)\tT(K)\tu(m/s)\n");
        for (int i = 0; i < n; i++) {
            printf("%.2f\t%.4f\t%.3f\t%.1f\t%.1f\t%.1f\n", 
                   mesh[i].x, mesh[i].A, mesh[i].M, mesh[i].P / 1000.0, mesh[i].T, mesh[i].u);
        }
    }
    return 0;
}
```
```cpp
// nozzle_solver.cpp — Ідіоматична реалізація розрахунку сопла Лаваля мовою C++20
#include <iostream>
#include <vector>
#include <cmath>
#include <optional>
#include <iomanip>
#include <span>

namespace GasDynamics {

struct GasProperties {
    double gamma{1.4};       // Показник адіабати
    double R{287.05};        // Газова стала, Дж/(кг·К)
    double P0{1e6};          // Повний тиск, Па
    double T0{300.0};        // Повна температура, К
    double P_amb{101325.0};  // Протитиск, Па
};

struct FlowState {
    double x{0.0};
    double area{0.0};
    double mach{0.0};
    double pressure{0.0};
    double temperature{0.0};
    double density{0.0};
    double velocity{0.0};
    bool has_shock{false};
};

class LavalNozzleSolver {
public:
    explicit LavalNozzleSolver(GasProperties props) : props_(props) {}

    [[nodiscard]] double areaRatioFromMach(double M) const noexcept {
        if (M <= 0.0) return 1e9;
        const double g_term = (2.0 / (props_.gamma + 1.0)) * (1.0 + 0.5 * (props_.gamma - 1.0) * M * M);
        const double exp_val = (props_.gamma + 1.0) / (2.0 * (props_.gamma - 1.0));
        return (1.0 / M) * std::pow(g_term, exp_val);
    }

    [[nodiscard]] double solveMach(double area_ratio, bool is_supersonic) const {
        if (std::abs(area_ratio - 1.0) < 1e-6) return 1.0;
        
        double M = is_supersonic ? 2.5 : 0.2;
        constexpr double epsilon = 1e-8;
        constexpr int max_iter = 100;

        for (int iter = 0; iter < max_iter; ++iter) {
            const double current_AR = areaRatioFromMach(M);
            const double dAR_dM = current_AR * (M * M - 1.0) / (M * (1.0 + 0.5 * (props_.gamma - 1.0) * M * M));
            const double f = current_AR - area_ratio;
            
            if (std::abs(f) < epsilon) break;
            M -= f / dAR_dM;
            
            if (!is_supersonic && M >= 1.0) M = 0.9999;
            if (is_supersonic && M <= 1.0) M = 1.0001;
        }
        return M;
    }

    [[nodiscard]] FlowState computeState(double x, double area, double mach) const {
        FlowState state;
        state.x = x;
        state.area = area;
        state.mach = mach;

        const double temp_ratio = 1.0 / (1.0 + 0.5 * (props_.gamma - 1.0) * mach * mach);
        const double press_ratio = std::pow(temp_ratio, props_.gamma / (props_.gamma - 1.0));

        state.temperature = props_.T0 * temp_ratio;
        state.pressure = props_.P0 * press_ratio;
        state.density = state.pressure / (props_.R * state.temperature);
        const double speed_of_sound = std::sqrt(props_.gamma * props_.R * state.temperature);
        state.velocity = mach * speed_of_sound;

        return state;
    }

    [[nodiscard]] std::optional<std::vector<FlowState>> solve(
        std::span<const double> x_mesh, 
        std::span<const double> area_mesh, 
        size_t throat_index) const 
    {
        if (x_mesh.size() != area_mesh.size() || throat_index >= x_mesh.size()) {
            return std::nullopt;
        }

        std::vector<FlowState> result;
        result.reserve(x_mesh.size());
        const double area_throat = area_mesh[throat_index];

        for (size_t i = 0; i < x_mesh.size(); ++i) {
            const double AR = area_mesh[i] / area_throat;
            const bool is_supersonic = (i > throat_index);
            const double mach = solveMach(AR, is_supersonic);
            result.push_back(computeState(x_mesh[i], area_mesh[i], mach));
        }

        return result;
    }

private:
    GasProperties props_;
};

} // namespace GasDynamics

int main() {
    using namespace GasDynamics;

    const GasProperties air{.gamma = 1.4, .R = 287.05, .P0 = 1.0e6, .T0 = 300.0, .P_amb = 101325.0};
    const LavalNozzleSolver solver(air);

    const std::vector<double> x_mesh{0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0};
    const std::vector<double> area_mesh{0.02, 0.015, 0.012, 0.01, 0.011, 0.014, 0.018, 0.023, 0.029, 0.035, 0.04};
    constexpr size_t throat_index = 3;

    if (const auto solution = solver.solve(x_mesh, area_mesh, throat_index)) {
        std::cout << "--- РОЗРАХУНОК СОПЛА ЛАВАЛЯ (C++) ---\n";
        std::cout << std::fixed << std::setprecision(3);
        std::cout << "x(m)\tArea(m2)\tMach\tP(kPa)\tT(K)\tVel(m/s)\n";
        for (const auto& pt : *solution) {
            std::cout << pt.x << "\t" << pt.area << "\t\t" << pt.mach << "\t" 
                      << pt.pressure / 1000.0 << "\t" << pt.temperature << "\t" << pt.velocity << "\n";
        }
    }
    return 0;
}
```
:::

## 3. Пастки чисельної реалізації та граничні випадки

Під час розробки високошвидкісних газодинамічних solvers виникають специфічні обчислювальні проблеми:

1. **Двозначність кореня `A / A*`:** Рівняння площ має два корені для будь-якого `A / A* > 1`. Якщо обрати хибне початкове наближення `M₀`, метод Ньютона збіжиться до дозвукового кореня замість надзвукового у дифузорі, що призведе до катастрофічного викривлення профілю тиску.
2. **Точка сингулярності `M = 1` у горловині:** У точці горловини похідна `dAR / dM` дорівнює нулю. Спроба обчислити крок Ньютона у самій горловині приведе до ділення на нуль. Тому у коді реалізовано явну перевірку `if (std::abs(area_ratio - 1.0) < 1e-6) return 1.0;`.
3. **Обробка прямого скачка ущільнення:** У перерозширеному режимі чисельний модуль повинен шукати координату `x_shock`, у якій відновлений за скачком тиск `P₂` після дозвукового гальмування у залишку дифузора точно дорівнює протитиску `P_amb`. Це розв'язується вкладеним методом дихотомії (половинного ділення) за координатами розрахункової сітки.
4. **Валідація геометрії:** Площа горловини `A_throat` має бути строго найменшою серед усіх елементів сітки `A(x)`. Наявність декількох мінімумів (хвилястий канал) створює локальні зони запирання і вимагає застосування більш складних 2D/3D Euler Navier-Stokes solvers.
