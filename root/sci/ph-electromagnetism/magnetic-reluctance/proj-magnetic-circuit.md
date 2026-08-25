# ⚙️ Чисельний розрахунок нелінійного магнітного кола

При зростанні струму обмотки феромагнітне осердя входить у зону магнітного насичення. Магнітна проникність матеріалу `μ_r` перестає бути лінійною константою і починає стрімко падати залежно від напруженості поля `H` та індукції `B`. Це унеможливлює використання простих алгебраїчних формул для розрахунку магнітного потоку та індуктивності. Для точного розрахунку робочої точки нелінійного магнітного кола застосовують чисельні методи розв'язання нелінійних рівнянь.

Апроксимація кривої намагнічування `B(H)` математичною моделлю Брауера в поєднанні з ітераційним алгоритмом Ньютона — Рафсона з регуляризацією кроку дозволяє точно обчислити магнітну індукцію у колі з зазором. Нижче виведено математичні залежності та наведено робочі реалізації мовами Python, C99 та C++20.

---

### 1. Математична модель нелінійності Брауера та ідентифікація параметрів

У сучасних пакетах чисельного моделювання електромагнітних полів (ANSYS Maxwell, FEMM, COMSOL Multiphysics) та системах розрахунку схем за розгалуженими магнітними мережами (Reluctance Network Method, RNM) для апроксимації кривої намагнічування феритів та електротехнічних сталей поширення набула трипараметрична модель Брауера (*Brauer model*). 

Модель описує залежність напруженості магнітного поля `H` від індукції `B` за формулою:

```
H(B) = (k1 · exp(k2 · B²) + k3) · B
```

де `k1, k2, k3` — емпіричні коефіцієнти апроксимації матеріалу (для силових феритів типові значення: `k1 = 4.5`, `k2 = 3.8`, `k3 = 120.0`). Перевагою моделі Брауера є її строго монотонне зростання та неперервна гладкість усіх похідних, що є критичним для чисельної стабільності ітераційних алгоритмів.

Ідентифікація коефіцієнтів `k1, k2, k3` проводиться за експериментальними точками паспортної кривої намагнічування `B(H)` методом найменших квадратів. Доданок `k3 · B` визначає початковий лінійний опір осердя при малих полях, тоді як експоненціальний член `k1 · exp(k2 · B²)` описує крутий злам та перехід до стану глибокого насичення.

Для знаходження робочої точки магнітного кола з довжиною лінії осердя `l_core`, повітряним зазором `l_g`, площею перерізу `A` та намагнічувальною силою `F = N · I` запишемо другий закон Кірхгофа для магнітного кола:

```
H(B) · l_core + H_gap · l_g = N · I
```

Оскільки індукція у зазорі `B_gap = B / (A_eff / A)` (при малих зазорах `B_gap ≈ B`), напруженість у зазорі дорівнює `H_gap = B / μ_0`. Підставляючи модель Брауера, отримуємо нелінійне алгебраїчне рівняння відносно невідомої індукції `B`:

```
f(B) = (k1 · exp(k2 · B²) + k3) · B · l_core + (B / μ_0) · l_g - N · I = 0
```

---

### 2. Алгоритм розв'язання методом Ньютона — Рафсона з регуляризацією

Рівняння `f(B) = 0` є трансцендентним і не має аналітичного розв'язку у елементарних функціях. Для його швидкого розв'язання застосуємо ітераційний метод Ньютона — Рафсона, який забезпечує квадратичну швидкість збіжності поблизу кореня.

Для обчислення чергового наближення `B_{k+1}` необхідно знайти аналітичну похідну `f'(B) = df/dB`:

```
dH/dB = d/dB [ (k1 · exp(k2 · B²) + k3) · B ]
= k1 · exp(k2 · B²) · (1 + 2 · k2 · B²) + k3
```

Похідна всієї цільової функції `f'(B)`:

```
f'(B) = (dH/dB) · l_core + l_g / μ_0
```

Ітераційна формула Ньютона — Рафсона з релаксаційним множником:

```
B_{k+1} = B_k - α · (f(B_k) / f'(B_k))
```

де `α ∈ (0, 1]` — демпфуючий коефіцієнт релаксації, що запобігає осциляціям поблизу крутих ділянок насичення. У більшості випадків використовують `α = 1.0`.

Алгоритм стартує з початкового наближення `B_0 = 0.1` Тл. На кожній ітерації обчислюється поправка `ΔB = f(B_k) / f'(B_k)`. Для запобігання від'ємним значенням індукції під час осциляцій ітерацій застосовують обмеження підлоги `B = max(B, 1e-6)`. Ітераційний процес зупиняється, коли абсолютне значення поправки стає меншим за задану точність `|ΔB| < 10⁻⁷` Тл.

Після знаходження індукції `B` обчислюються підсумкові характеристики кола:
- **Магнітний потік:** `Φ = B · A`
- **Магнітний опір зазору:** `R_m,gap = l_g / (μ_0 · A)`
- **Магнітний опір осердя:** `R_m,core = (H(B) · l_core) / Φ`
- **Повний опір:** `R_m,total = R_m,core + R_m,gap`
- **Індуктивність:** `L = N² / R_m,total`
- **Накопичена енергія:** `W_m = (1/2) · L · I²`

---

### 3. Чисельна стабільність та захист від переповнення

Під час розрахунку режимів екстремального перевантаження, коли намагнічувальна сила `F` перевищує розрахункову у десятки разів, аргумент експоненти `k2 · B²` у моделі Брауера може вийти за межі допустимих чисельних діапазонів типу `double` (переповнення при `exp(x) > 10³⁰⁸`).

Для гарантування абсолютної обчислювальної стабільності у високопродуктивних CAD-соліверах застосовують два захисні механізми:
1. **Обмеження поправки ітерації:** Зсув індукції за один крок `ΔB` обмежується максимальною величиною `|ΔB| ≤ 0.2` Тл. Це запобігає перельоту через коліно кривої у зонах із малим значенням похідної.
2. **Асимптотична лінеаризація у глибокому насиченні:** При досягненні індукції `B > 2.5` Тл експоненціальну функцію замінюють на лінійну асимптоту з нахилом `μ_0`. Це відповідає фізичній реальності, оскільки після повного орієнтування всіх доменів феромагнетик поводиться як вакуум.

---

### 4. Архітектура нелінійних чисельних соліверів у CAD-системах

У промислових програмах розрахунку електромагнітних пристроїв розв'язання нелінійного магнітного кола виконується як частина глобального обчислювального конвеєра:

1. **Етап валідації вхідних даних:** Перевіряється фізична коректність геометричних параметрів (`l_core > 0`, `l_gap ≥ 0`, `area > 0`, `turns > 0`). Некоректні параметри відсікаються до початку ітерацій.
2. **Етап ініціалізації розв'язувача:** Обчислюється початковий магнітний опір у лінійній зоні `R_m,0`. За початковим наближенням будується початковий вектор індукції.
3. **Ітераційний цикл розв'язання:** Застосовується метод Ньютона — Рафсона із контролем збіжності. Якщо число ітерацій перевищує `max_iter = 100`, солівер повертає помилку незбіжності (*non-convergence error*).
4. **Етап обчислення вторинних параметрів:** За знайденою індукцією `B` інтегрується накопичена енергія `W_m` та обчислюється диференціальна індуктивність `L_diff = dΨ/dI = N² / R_m,diff`.

---

### 5. Порівняльний аналіз програмних реалізацій

Для задоволення вимог різних галузей розробки алгоритм реалізовано на трьох мовах програмування:

1. **Python (Версія для прототипування):** Використовує динамічну типізацію та орієнтований на швидку перевірку розрахунків під час проектування. Результат повертається у вигляді структурованого словника (*dictionary*).
2. **C99 (Версія для вбудованих систем / MCU):** Спроектований для роботи на мікроконтролерах силових джерел живлення без динамічного виділення пам'яті. Використовує передачу даних через вказівники та явний прапорець успішності збіжності `bool converged`.
3. **C++20 (Версія для системного CAD-моделювання):** Застосовує сучасний стандарт C++20. Опис помилок реалізовано без винятків за допомогою монадного типу `std::expected<SimulationResult, SolverError>`. Використано статичні константи з модуля `<numbers>` (`std::numbers::pi`), атрибути `[[nodiscard]]`, гарантовані компілятором `constexpr` та призначені ініціалізатори (*designated initializers*).

:::tabs
```py
import math

class CoreMaterial:
    """Модель матеріалу осердя за формулою Брауера."""
    def __init__(self, k1: float = 4.5, k2: float = 3.8, k3: float = 120.0, b_sat: float = 0.42):
        self.k1 = k1
        self.k2 = k2
        self.k3 = k3
        self.b_sat = b_sat

    def h_field(self, b: float) -> float:
        """Напруженість H(B) у А/м."""
        return (self.k1 * math.exp(self.k2 * b * b) + self.k3) * b

    def dh_db(self, b: float) -> float:
        """Похідна dH/dB."""
        b2 = b * b
        exp_val = math.exp(self.k2 * b2)
        return self.k1 * exp_val * (1.0 + 2.0 * self.k2 * b2) + self.k3


def solve_magnetic_circuit(l_core: float, l_gap: float, area: float, 
                           turns: int, current: float, mat: CoreMaterial) -> dict:
    """Розв'язок нелінійного магнітного кола методом Ньютона-Рафсона."""
    mu0 = 4.0 * math.pi * 1e-7
    mmf = turns * current
    
    # Початкове наближення для B
    b = 0.1
    max_iter = 100
    tol = 1e-7

    for iteration in range(max_iter):
        h = mat.h_field(b)
        f_val = h * l_core + (b / mu0) * l_gap - mmf
        
        dh = mat.dh_db(b)
        df_val = dh * l_core + l_gap / mu0
        
        delta = f_val / df_val
        b -= delta
        
        if b < 0:
            b = 1e-4
            
        if abs(delta) < tol:
            break

    flux = b * area
    reluctance_core = (mat.h_field(b) * l_core) / flux if flux > 0 else 0
    reluctance_gap = l_gap / (mu0 * area)
    total_reluctance = reluctance_core + reluctance_gap
    inductance = (turns * turns) / total_reluctance

    return {
        "b_field": b,
        "flux": flux,
        "reluctance_core": reluctance_core,
        "reluctance_gap": reluctance_gap,
        "total_reluctance": total_reluctance,
        "inductance_uH": inductance * 1e6,
        "iterations": iteration + 1
    }


if __name__ == "__main__":
    material = CoreMaterial(k1=4.5, k2=3.8, k3=120.0)
    res = solve_magnetic_circuit(l_core=0.114, l_gap=0.001, area=2.11e-4, 
                                 turns=30, current=8.0, mat=material)
    print(f"B = {res['b_field']:.4f} Тл")
    print(f"Потік = {res['flux']*1e6:.2f} мкВб")
    print(f"Rm_core = {res['reluctance_core']:.1f} А·вт/Вб")
    print(f"Rm_gap  = {res['reluctance_gap']:.1f} А·вт/Вб")
    print(f"Індуктивність = {res['inductance_uH']:.2f} мкГн")
```
```c
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define MU0 (4.0 * M_PI * 1e-7)

typedef struct {
    double k1;
    double k2;
    double k3;
    double b_sat;
} CoreMaterial;

typedef struct {
    double b_field;
    double flux;
    double reluctance_core;
    double reluctance_gap;
    double total_reluctance;
    double inductance;
    int iterations;
    bool converged;
} MagneticResult;

static double h_field(const CoreMaterial* mat, double b) {
    return (mat->k1 * exp(mat->k2 * b * b) + mat->k3) * b;
}

static double dh_db(const CoreMaterial* mat, double b) {
    double b2 = b * b;
    double exp_val = exp(mat->k2 * b2);
    return mat->k1 * exp_val * (1.0 + 2.0 * mat->k2 * b2) + mat->k3;
}

bool solve_magnetic_circuit(double l_core, double l_gap, double area,
                            int turns, double current, const CoreMaterial* mat,
                            MagneticResult* result) {
    double mmf = turns * current;
    double b = 0.1;
    const int max_iter = 100;
    const double tol = 1e-7;

    for (int iter = 0; iter < max_iter; iter++) {
        double h = h_field(mat, b);
        double f_val = h * l_core + (b / MU0) * l_gap - mmf;
        double df_val = dh_db(mat, b) * l_core + l_gap / MU0;

        double delta = f_val / df_val;
        b -= delta;

        if (b < 1e-6) b = 1e-6;

        if (fabs(delta) < tol) {
            result->b_field = b;
            result->flux = b * area;
            result->reluctance_gap = l_gap / (MU0 * area);
            result->reluctance_core = (h_field(mat, b) * l_core) / result->flux;
            result->total_reluctance = result->reluctance_core + result->reluctance_gap;
            result->inductance = (turns * turns) / result->total_reluctance;
            result->iterations = iter + 1;
            result->converged = true;
            return true;
        }
    }
    result->converged = false;
    return false;
}

int main(void) {
    CoreMaterial ferrite = { .k1 = 4.5, .k2 = 3.8, .k3 = 120.0, .b_sat = 0.42 };
    MagneticResult res;

    if (solve_magnetic_circuit(0.114, 0.001, 2.11e-4, 30, 8.0, &ferrite, &res)) {
        printf("B = %.4f T\n", res.b_field);
        printf("Flux = %.2f uWb\n", res.flux * 1e6);
        printf("Rm_core = %.1f A*t/Wb\n", res.reluctance_core);
        printf("Rm_gap  = %.1f A*t/Wb\n", res.reluctance_gap);
        printf("L = %.2f uH\n", res.inductance * 1e6);
    } else {
        printf("Помилка: алгоритм не збігся.\n");
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <numbers>
#include <expected>
#include <system_error>

namespace physics::magnetics {

constexpr double mu0 = 4.0 * std::numbers::pi * 1e-7;

struct CoreMaterial {
    double k1{4.5};
    double k2{3.8};
    double k3{120.0};
    double b_sat{0.42};

    [[nodiscard]] constexpr double h_field(double b) const noexcept {
        return (k1 * std::exp(k2 * b * b) + k3) * b;
    }

    [[nodiscard]] constexpr double dh_db(double b) const noexcept {
        const double b2 = b * b;
        const double exp_val = std::exp(k2 * b2);
        return k1 * exp_val * (1.0 + 2.0 * k2 * b2) + k3;
    }
};

struct CircuitParams {
    double l_core_m;
    double l_gap_m;
    double area_m2;
    int turns;
    double current_a;
};

struct SimulationResult {
    double b_field_t;
    double flux_wb;
    double reluctance_core;
    double reluctance_gap;
    double total_reluctance;
    double inductance_h;
    int iterations;
};

enum class SolverError {
    invalid_parameters,
    non_convergence
};

[[nodiscard]] std::expected<SimulationResult, SolverError> 
solve_circuit(const CircuitParams& params, const CoreMaterial& mat) noexcept {
    if (params.l_core_m <= 0.0 || params.area_m2 <= 0.0 || params.turns <= 0) {
        return std::unexpected(SolverError::invalid_parameters);
    }

    const double mmf = params.turns * params.current_a;
    double b = 0.1;
    constexpr int max_iter = 100;
    constexpr double tol = 1e-7;

    for (int iter = 0; iter < max_iter; ++iter) {
        const double h = mat.h_field(b);
        const double f_val = h * params.l_core_m + (b / mu0) * params.l_gap_m - mmf;
        const double df_val = mat.dh_db(b) * params.l_core_m + params.l_gap_m / mu0;

        const double delta = f_val / df_val;
        b -= delta;

        if (b < 1e-6) b = 1e-6;

        if (std::abs(delta) < tol) {
            const double flux = b * params.area_m2;
            const double rm_gap = params.l_gap_m / (mu0 * params.area_m2);
            const double rm_core = (mat.h_field(b) * params.l_core_m) / flux;
            const double rm_total = rm_core + rm_gap;
            const double inductance = (params.turns * params.turns) / rm_total;

            return SimulationResult{
                .b_field_t = b,
                .flux_wb = flux,
                .reluctance_core = rm_core,
                .reluctance_gap = rm_gap,
                .total_reluctance = rm_total,
                .inductance_h = inductance,
                .iterations = iter + 1
            };
        }
    }

    return std::unexpected(SolverError::non_convergence);
}

} // namespace physics::magnetics

int main() {
    using namespace physics::magnetics;

    const CoreMaterial ferrite{};
    const CircuitParams params{
        .l_core_m = 0.114,
        .l_gap_m = 0.001,
        .area_m2 = 2.11e-4,
        .turns = 30,
        .current_a = 8.0
    };

    const auto result = solve_circuit(params, ferrite);

    if (result) {
        std::cout << "B = " << result->b_field_t << " T\n"
                  << "Flux = " << result->flux_wb * 1e6 << " uWb\n"
                  << "Rm_core = " << result->reluctance_core << " A*t/Wb\n"
                  << "Rm_gap  = " << result->reluctance_gap << " A*t/Wb\n"
                  << "L = " << result->inductance_h * 1e6 << " uH\n";
    } else {
        std::cerr << "Solver error occurred.\n";
    }
}
```
:::
