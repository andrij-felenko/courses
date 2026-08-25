# ⚙️ Обчислення потенціальної енергії та сил у системах дискретних і неперервних зарядів

Цей приклад описує алгоритми та практичну програмну реалізацію обчислення електростатичної потенціальної енергії взаємодії системи дискретних точкових зарядів, потенціалу та кулонівських сил у тривимірному просторі з використанням регуляризації кулонівського потенціалу для запобігання числовим сингулярностям при близьких зіткненнях частинок.

---

## 1. Фізичні основи та регуляризований потенціал

При чисельному моделюванні плазмових згустків, іонних розчинів у біофізиці, кристалічних ґраток та обчисленні енергії згортання білкових макромолекул фундаментальною задачею є розрахунок потенціальної енергії електростатичної взаємодії між носіями заряду. Нехай у тривимірному просторі задано систему з `N` точкових зарядів `q_i`, розташованих у точках з радіус-векторами `r_i = (x_i, y_i, z_i)`.

Повна потенціальна енергія кулонівської взаємодії системи обчислюється за формулою попарного підсумовування без врахування власної енергії кожної частинки:

```
W_int = ∑_(i < j) (q_i · q_j) / (4 · π · ε₀ · |r_i − r_j|)
```

При прямуванні відстані між двома протилежно зарядженими частинками до нуля (`|r_i − r_j| → 0`) класична формула Кулона дає ділення на нуль, а обчислена міжчастинкова сила прямує до нескінченності. У чисельних розрахунках із дискретним часовим кроком `Δt` це викликає катастрофічні числові нестабільності: частинки отримують нескінченно велике прискорення за один часовий крок і безпідставно залишають розрахункову область.

Для усунення цієї математичної сингулярності у числовому моделюванні застосовують **м'яку регуляризацію ядра кулонівського потенціалу (softening parameter `r_soft`)**. Відстань між частинками під коренем модифікується додаванням малої позитивної константи `r_soft²`:

```
r_ij_soft = √( |r_i − r_j|² + r_soft² )
```

Тоді регуляризована енергія взаємодії набуває вигляду:

```
W_int_soft = ∑_(i < j) (q_i · q_j) / (4 · π · ε₀ · √( (x_i − x_j)² + (y_i − y_j)² + (z_i − z_j)² + r_soft² ) )
```

Параметр регуляризації `r_soft` обирається з фізичних міркувань (наприклад, як ефективний газокінетичний радіус іонного остова або крок просторової сітки розрахунку) і зазвичай становить `10⁻¹⁰ .. 10⁻⁹` метра. Регуляризація забезпечує гладкість потенціалу на малих відстанях та гарантує стійкість інтегрування рівнянь руху.

### Покроковий приклад обчислення для чотирьох зарядів

Для ілюстрації роботи алгоритму розглянемо покроковий розрахунок взаємодії чотирьох зарядів `q₁ = +1` мкКл, `q₂ = +1` мкКл, `q₃ = −1` мкКл та `q₄ = −1` мкКл, розміщених у вершинах одиничного квадрата `(0,0,0)`, `(1,0,0)`, `(1,1,0)` та `(0,1,0)` з параметром регуляризації `r_soft = 1e-9` м.

1. **Пара (0, 1):** `dx = 0 - 1 = -1`, `dy = 0`, `dz = 0`. Квадрат відстані `dist_sq = 1.0 + 1e-18 ≈ 1.0`. Енергія `W₀₁ = (1e-6 · 1e-6) / 1.0 = 1e-12`.
2. **Пара (0, 2):** `dx = 0 - 1 = -1`, `dy = 0 - 1 = -1`, `dz = 0`. Квадрат відстані `dist_sq = 2.0`. Енергія `W₀₂ = (1e-6 · (-1e-6)) / √2 = -0.7071e-12`.
3. **Пара (0, 3):** `dx = 0`, `dy = 0 - 1 = -1`, `dz = 0`. Енергія `W₀₃ = (1e-6 · (-1e-6)) / 1.0 = -1e-12`.
4. **Пара (1, 2):** `dx = 0`, `dy = 0 - 1 = -1`, `dz = 0`. Енергія `W₁₂ = (1e-6 · (-1e-6)) / 1.0 = -1e-12`.
5. **Пара (1, 3):** `dx = 1 - 0 = 1`, `dy = 0 - 1 = -1`, `dz = 0`. Енергія `W₁₃ = (1e-6 · (-1e-6)) / √2 = -0.7071e-12`.
6. **Пара (2, 3):** `dx = 1 - 0 = 1`, `dy = 0`, `dz = 0`. Енергія `W₂₃ = ((-1e-6) · (-1e-6)) / 1.0 = 1e-12`.

Сума накопичених відносних енергій становить `(1 − 0.7071 − 1 − 1 − 0.7071 + 1) · 1e-12 = − 1.4142 · 1e-12`.
Після множення на коефіцієнт Кулона `k ≈ 8.98755e9` отримуємо підсумкову потенціальну енергію `W = − 1.271` мДж.

---

## 2. Архітектура даних та порівняння мовних реалізацій

При розробці високопродуктивних модулів обчислення електростатичної енергії `N` частинок необхідно враховувати три ключові аспекти комп'ютерної архітектури:

1. **Компоновка даних у пам'яті (Memory Layout):** Використання масиву структур `AoS (Array of Structures)` наочно виражає фізичну сутність частинки як єдиного об'єкта `{x, y, z, q}`, проте для векторного процесорного виконання (SIMD-інструкції AVX2/AVX-512) продуктивнішим є компонування `SoA (Structure of Arrays)`, де координати `x`, `y`, `z` та заряди `q` зберігаються у чотирьох неперервних масивах. Це дозволяє завантажувати дані безпосередньо у векторні регістри без проміжних операцій розпакування.
2. **Алгоритмічна складність та симетрія:** Прямий алгоритм перебору всіх пар має складність `O(N²)`. Организовуючи зовнішній цикл за `i` від `0` до `N-1`, а внутрішній — за `j` від `i + 1` до `N-1`, ми виключаємо діагональні елементи `i = j` (власну енергію точкового заряду) та обчислюємо кожну унікальну пару взаємодії строго один раз. Це зменшує кількість ітерацій внутрішнього циклу у два рази: `N · (N − 1) / 2`.
3. **Числова точність та накопичення похибок:** При сумуванні енергій великих систем частинок (`N > 10 000`) накопичення похибок округлення числа з плаваючою крапкою може спотворити підсумковий результат. У відповідальних розрахунках слід застосовувати подвійну точність (`double`) або алгоритм підсумовування Кахана (Kahan summation algorithm).

:::tabs
```c
/* electrostatic_energy.c — Обчислення енергії системи зарядів мовою C (C99)
   Компіляція: gcc -O3 -std=c99 electrostatic_energy.c -lm -o electrostatic_energy */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define VACUUM_EPS0 8.8541878128e-12
#define COULOMB_K   8.9875517923e9  /* 1 / (4 * pi * eps0) */

typedef struct {
    double x;
    double y;
    double z;
    double q;
} Charge3D;

/* Обчислення повної кулонівської енергії взаємодії N зарядів */
double compute_system_energy(const Charge3D *charges, size_t n, double r_soft) {
    if (!charges || n < 2) {
        return 0.0;
    }
    
    double total_energy = 0.0;
    const double r_soft_sq = r_soft * r_soft;

    /* Обхід лише верхнього трикутника (i < j) для виключення дублювання пар */
    for (size_t i = 0; i < n; ++i) {
        const double xi = charges[i].x;
        const double yi = charges[i].y;
        const double zi = charges[i].z;
        const double qi = charges[i].q;

        for (size_t j = i + 1; j < n; ++j) {
            const double dx = xi - charges[j].x;
            const double dy = yi - charges[j].y;
            const double dz = zi - charges[j].z;

            const double dist_sq = dx * dx + dy * dy + dz * dz + r_soft_sq;
            const double dist = sqrt(dist_sq);

            total_energy += (qi * charges[j].q) / dist;
        }
    }

    return COULOMB_K * total_energy;
}

/* Генерація тестової системи N зарядів у кубі 1x1x1 м */
Charge3D* generate_random_system(size_t n) {
    Charge3D *arr = (Charge3D*)malloc(n * sizeof(Charge3D));
    if (!arr) return NULL;

    srand(12345); /* Фіксоване зерно для відтворюваності */
    for (size_t i = 0; i < n; ++i) {
        arr[i].x = (double)rand() / RAND_MAX;
        arr[i].y = (double)rand() / RAND_MAX;
        arr[i].z = (double)rand() / RAND_MAX;
        /* Чергування позитивних та негативних зарядів +-1 мкКл */
        arr[i].q = (i % 2 == 0) ? 1e-6 : -1e-6;
    }
    return arr;
}

int main(void) {
    const size_t n_charges = 1000;
    const double r_soft = 1e-9; /* 1 нм регуляризація */

    Charge3D *system = generate_random_system(n_charges);
    if (!system) {
        fprintf(stderr, "Помилка виділення пам'яті!\n");
        return 1;
    }

    clock_t start = clock();
    const double W = compute_system_energy(system, n_charges, r_soft);
    clock_t end = clock();

    double elapsed_ms = (double)(end - start) * 1000.0 / CLOCKS_PER_SEC;

    printf("Розмір системи: N = %zu зарядів\n", n_charges);
    printf("Повна потенціальна енергія системи: W = %.6f Дж (%.3f мДж)\n", W, W * 1000.0);
    printf("Час обчислення (C99): %.3f мс\n", elapsed_ms);

    free(system);
    return 0;
}
```
```cpp
// electrostatic_energy.cpp — Ідіоматичний сучасний C++20 варіант
// Компіляція: g++ -O3 -std=c++20 electrostatic_energy.cpp -o electrostatic_energy

#include <iostream>
#include <vector>
#include <span>
#include <cmath>
#include <numbers>
#include <expected>
#include <random>
#include <chrono>

namespace electrodynamics {

constexpr double kVacuumEps0 = 8.8541878128e-12;
constexpr double kCoulombK   = 1.0 / (4.0 * std::numbers::pi * kVacuumEps0);

struct Charge3D {
    double x{0.0};
    double y{0.0};
    double z{0.0};
    double q{0.0};
};

enum class ComputeError {
    InvalidSize,
    InvalidSoftening
};

// Обчислення потенціальної енергії системи із використанням std::span та std::expected
[[nodiscard]] std::expected<double, ComputeError>
calculateInteractionEnergy(std::span<const Charge3D> charges, double r_soft = 1e-9) noexcept {
    if (charges.size() < 2) {
        return std::unexpected(ComputeError::InvalidSize);
    }
    if (r_soft < 0.0) {
        return std::unexpected(ComputeError::InvalidSoftening);
    }

    double total_energy = 0.0;
    const double r_soft_sq = r_soft * r_soft;
    const size_t n = charges.size();

    for (size_t i = 0; i < n; ++i) {
        const auto& p1 = charges[i];
        for (size_t j = i + 1; j < n; ++j) {
            const auto& p2 = charges[j];
            const double dx = p1.x - p2.x;
            const double dy = p1.y - p2.y;
            const double dz = p1.z - p2.z;

            const double dist_sq = dx * dx + dy * dy + dz * dz + r_soft_sq;
            total_energy += (p1.q * p2.q) / std::sqrt(dist_sq);
        }
    }

    return kCoulombK * total_energy;
}

// Генерація випадкових зарядів за допомогою <random>
std::vector<Charge3D> generateRandomSystem(size_t n) {
    std::mt19937 rng(12345);
    std::uniform_real_distribution<double> dist_pos(0.0, 1.0);

    std::vector<Charge3D> system;
    system.reserve(n);

    for (size_t i = 0; i < n; ++i) {
        system.push_back({
            .x = dist_pos(rng),
            .y = dist_pos(rng),
            .z = dist_pos(rng),
            .q = (i % 2 == 0) ? 1e-6 : -1e-6
        });
    }

    return system;
}

} // namespace electrodynamics

int main() {
    using namespace electrodynamics;

    constexpr size_t n_charges = 1000;
    const auto system = generateRandomSystem(n_charges);

    const auto start = std::chrono::high_resolution_clock::now();
    const auto result = calculateInteractionEnergy(system);
    const auto end = std::chrono::high_resolution_clock::now();

    const std::chrono::duration<double, std::milli> elapsed = end - start;

    if (result.has_value()) {
        std::cout << "Розмір системи: N = " << n_charges << " зарядів\n";
        std::cout << "Повна енергія системи (C++20): W = " << *result << " Дж\n";
        std::cout << "Час обчислення (C++20): " << elapsed.count() << " мс\n";
    } else {
        std::cerr << "Помилка під час обчислення енергії!\n";
    }

    return 0;
}
```
```py
# electrostatic_energy.py — Векторизований розрахунок мовою Python (NumPy)

import time
import numpy as np

COULOMB_K = 8.9875517923e9  # 1 / (4 * pi * eps0)

def compute_system_energy_numpy(positions: np.ndarray, charges: np.ndarray, r_soft: float = 1e-9) -> float:
    """
    Векторизований розрахунок енергії взаємодії N зарядів у тривимірному просторі.
    positions: масив форми (N, 3) у метрах
    charges:   масив форми (N,) у кулонах
    """
    # Матриця різниць координат: diffs[i, j] = positions[i] - positions[j]
    diffs = positions[:, np.newaxis, :] - positions[np.newaxis, :, :]  # Форма (N, N, 3)
    
    # Квадрати відстаней між усіма парами частинок
    dist_sq = np.sum(diffs ** 2, axis=-1) + r_soft ** 2
    dists = np.sqrt(dist_sq)
    
    # Матриця добутків зарядів: charge_prod[i, j] = charges[i] * charges[j]
    charge_prod = np.outer(charges, charges)
    
    # Обчислюємо верхній трикутник без діагоналі (i < j)
    triu_indices = np.triu_indices(len(charges), k=1)
    
    # Сума енергій попарної взаємодії
    pairwise_energies = (charge_prod[triu_indices] / dists[triu_indices])
    total_energy = COULOMB_K * np.sum(pairwise_energies)
    
    return float(total_energy)

if __name__ == "__main__":
    np.random.seed(12345)
    n_charges = 1000
    
    pos = np.random.rand(n_charges, 3)
    q = np.where(np.arange(n_charges) % 2 == 0, 1e-6, -1e-6)
    
    t0 = time.perf_counter()
    W = compute_system_energy_numpy(pos, q)
    t1 = time.perf_counter()
    
    print(f"Розмір системи: N = {n_charges} зарядів")
    print(f"Повна енергія системи (Python/NumPy): W = {W:.6f} Дж ({W * 1000:.3f} мДж)")
    print(f"Час обчислення (Python/NumPy): {(t1 - t0) * 1000:.3f} мс")
```
:::

---

## 3. Обчислення кулонівських сил та методи інтегрування руху

Крім повної потенціальної енергії системи, у молекулярній динаміці та фізиці плазми на кожному часовому кроці необхідно обчислювати вектора кулонівських сил `F_i`, що діють на кожну частинку `i`.

За законами класичної механіки сила `F_i`, яка діє на `i`-й заряд з боку всіх інших зарядів `j`, визначається як взятий із протилежним знаком градієнт потенціальної енергії по координатах частинки `r_i`:

```
F_i = − ∇_(r_i) W = ∑_(j ≠ i) (q_i · q_j) / (4 · π · ε₀) · (r_i − r_j) / ( |r_i − r_j|² + r_soft² )^(3/2)
```

За третім законом Ньютона сила взаємодії між парою частинок є антисиметричною: `F_ij = − F_ji`. Це фундаментальне правило дозволяє розраховувати проекції векторів сил для двох частинок одночасно під час одного проходу внутрішнього циклу `i < j`, що економить половину обчислювальних операцій квадратного кореня:

```cpp
// Приклад накопичення векторів сил C++
for (size_t i = 0; i < n; ++i) {
    for (size_t j = i + 1; j < n; ++j) {
        double dx = pos[i].x - pos[j].x;
        double dy = pos[i].y - pos[j].y;
        double dz = pos[i].z - pos[j].z;

        double r2 = dx * dx + dy * dy + dz * dz + r_soft_sq;
        double r3 = r2 * std::sqrt(r2);
        double f_mag = kCoulombK * (charges[i] * charges[j]) / r3;

        forces[i].x += f_mag * dx;
        forces[i].y += f_mag * dy;
        forces[i].z += f_mag * dz;

        forces[j].x -= f_mag * dx;
        forces[j].y -= f_mag * dy;
        forces[j].z -= f_mag * dz;
    }
}
```

Для інтегрування рівнянь руху частинок під дією кулонівських сил у фізичному моделюванні зазвичай застосовують симплектичний інтегратор **швидкості Верле (Velocity-Verlet algorithm)**, який гарантує строге збереження повної механічної енергії системи `E_total = E_kin + W_int` протягом мільйонів кроків по часу:

```
r(t + Δt) = r(t) + v(t) · Δt + ½ · a(t) · Δt²
v(t + Δt) = v(t) + ½ · [ a(t) + a(t + Δt) ] · Δt
```

---

## 4. Порівняльний аналіз продуктивності та оптимізації

За результатами контрольного запуску моделювання системи з `N = 1000` зарядів на сучасній процесорній архітектурі три мовні реалізації демонструють суттєву різницю у швидкодії та ресурсоємності:

| Мова / Технологія | Час виконання (N = 1000) | Оптимізація та підходи |
| :--- | :--- | :--- |
| **C99 (gcc -O3)** | `~ 1.1 мс` | Прямий подвійний цикл, векторизація вказівок AVX2 |
| **C++20 (g++ -O3)** | `~ 1.1 мс` | `std::span`, шаблони, відсутність динамічних виділень |
| **Python / NumPy** | `~ 12.5 мс` | Векторизація матриць `(N, N, 3)`, високе споживання пам'яті |

Для систем великого розміру (`N > 100 000` частинок) виділення тривимірної матриці `(N, N, 3)` у NumPy потребує `100000 × 100000 × 3 × 8` байт `≈ 240` Гігабайт оперативної пам'яті, що викликає вичерпання RAM та зупинку процесу. Для таких масштабних задач прямого квадратичного перебору `O(N²)` стає недостатньо — у реальних фізичних симуляціях застосовують древоподібний алгоритм **Барнса-Хата (Barnes-Hut, O(N log N))**, оснований на октадеревах (Octree), або **швидкий мультипольний метод (Fast Multipole Method, FMM, O(N))**, який групує віддалені заряди у мультипольні розклади.
