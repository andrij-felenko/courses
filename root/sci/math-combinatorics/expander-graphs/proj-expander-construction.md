# ⚙️ Реалізація явного графа Маргуліса — Габбера — Галіля та обчислення спектральної щілини

У цій практичній вставці подано детальну програмну реалізацію детермінованого 8-регулярного графа-розширювача Маргуліса — Габбера — Галіля (Margulis-Gabber-Galil) на дискретному торі `ℤ_m × ℤ_m`, алгоритм генерації випадкового блукання для вибіркового аналізу (марківського семплінгу) та чисельний метод степеневих ітерацій (Power Iteration) для аналітичного обчислення спектральної щілини `γ = d - λ₂`.

## Алгебраїчна структура графа та математична постановка задачі

Граф Маргуліса — Габбера — Галіля є нескінченним сімейством `8`-регулярних графів із кількістю вершин `N = m²`. Вершини графа утворюють двовимірну дискретну сітку (тор) `ℤ_m × ℤ_m`, де кожна вершина кодується парою цілочисельних координат `(x, y)` у межах від `0` до `m - 1`.

Алгебраїчна унікальність цієї побудови полягає в тому, що ребра графа задаються не списком суміжності у пам'яті, а сукупністю вісімки фіксованих афінних перетворень двовимірного векторного простору за модулем `m`. Для кожної вершини `(x, y)` 8 її сусідів утворюються застосуванням чотирьох базових операцій та їхніх обернених функцій:

1. Перше вертикальне зсувне перетворення:
   `T₁(x, y) = (x, (y + x) mod m)`
2. Обернене перше вертикальне перетворення:
   `T₁⁻¹(x, y) = (x, (y - x + m) mod m)`
3. Друге вертикальне зсувне перетворення зі зсувом одиниці:
   `T₂(x, y) = (x, (y + x + 1) mod m)`
4. Обернене друге вертикальне перетворення:
   `T₂⁻¹(x, y) = (x, (y - x - 1 + m) mod m)`
5. Перше горизонтальне зсувне перетворення:
   `S₁(x, y) = ((x + y) mod m, y)`
6. Обернене перше горизонтальне перетворення:
   `S₁⁻¹(x, y) = ((x - y + m) mod m, y)`
7. Друге горизонтальне зсувне перетворення зі зсувом одиниці:
   `S₂(x, y) = ((x + y + 1) mod m, y)`
8. Обернене друге горизонтальне перетворення:
   `S₂⁻¹(x, y) = ((x - y - 1 + m) mod m, y)`

Оскільки кожна з цих функцій є бієктивним відображенням множини `ℤ_m × ℤ_m` на себе, кожна вершина випромінює тотожно 8 ребер, що ґарантує строгу 8-регулярність графа. Для межових вершин сітки (коли `x = 0` або `y = 0`) арифметичний модуль `mod m` здійснює автоматичне закольцовування (wrap-around), перетворюючи плоску сітку на топологічний дискретний тор.

Практична цінність такого підходу полягає у відсутності необхідності зберігати список чи матрицю суміжності у базі даних чи оперативній пам'яті. Для графа з мільярдом вершин `N = 10⁹` операція пошуку сусідів будь-якої вершини виконується за сталий час `O(1)`, вимагаючи лише кількох арифметичних операцій додавання та обчислення остачі від ділення.

## Чисельний метод Power Iteration для обчислення спектральної щілини

Аби обчислити спектральну щілину `γ = d - λ₂`, необхідно знайти друге за величиною власне значення `λ₂` матриці суміжності `A`. Для великих графів пряме обчислення власних значень через розклад якобі чи QR-розклад вимагає `O(N³)` операцій, що є неприйнятним.

Замість цього застосовується метод степеневих ітерацій (Power Iteration), адаптований під відокремлення другого власного значення:

1. **Ініціалізація:** Генерується випадковий вектор `v⁰ ∈ ℝⁿ`.
2. **Ортогоналізація відносно `v₁`:** Головне власне значення `λ₁ = 8` відповідає постійному власному вектору `v₁ = (1/√N, ..., 1/√N)ᵀ`. Якщо початковий вектор `v⁰` має неперпендикулярну компоненту до `v₁`, то на кожному кроці множення ця компонента зростатиме найшвидше (з коефіцієнтом 8), і алгоритм поверне `λ₁ = 8` замість `λ₂`. Тому на кожному кроці від вектора віднімається його середнє значення:
   `v_proj[i] = v[i] - (1/N) · ∑ⱼ v[j]`
3. **Множення на матрицю суміжності:** Обчислити новий вектор `wᵏ = A · vᵏ⁻¹`. Завдяки імплантованій функції сусідів, це множення виконується за час `O(N · d)` без створення самої матриці `A`:
   `w[next_idx] += v[cur_idx]` для всіх 8 сусідів.
4. **Оцінка значення Реле:** Обчислюється наближення власного значення:
   `λ₂ ≈ (vᵀ · A · v) / (vᵀ · v)`
5. **Нормалізація:** Вектор `wᵏ` ділиться на його евклідову норму `‖wᵏ‖₂`, аби запобігти арифметичному переповненню типу з плаваючою крапкою.

Процес повторюється доти, доки різниця між значеннями `λ₂` на двох послідовних ітераціях не стане меншою за задану точність `tol = 1e-6`.

## Програмна реалізація мовами C та C++

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

typedef struct {
    int x;
    int y;
} Vertex;

static inline int mod_m(int a, int m) {
    int r = a % m;
    return r < 0 ? r + m : r;
}

// Повертає 8 сусідів вершини (x, y) у графі Маргуліса — Габбера — Галіля
void get_mgg_neighbors(Vertex v, int m, Vertex neighbors[8]) {
    int x = v.x;
    int y = v.y;

    neighbors[0] = (Vertex){x, mod_m(y + x, m)};
    neighbors[1] = (Vertex){x, mod_m(y - x, m)};
    neighbors[2] = (Vertex){x, mod_m(y + x + 1, m)};
    neighbors[3] = (Vertex){x, mod_m(y - x - 1, m)};
    neighbors[4] = (Vertex){mod_m(x + y, m), y};
    neighbors[5] = (Vertex){mod_m(x - y, m), y};
    neighbors[6] = (Vertex){mod_m(x + y + 1, m), y};
    neighbors[7] = (Vertex){mod_m(x - y - 1, m), y};
}

// Випадкове блукання довжиною steps від початкової вершини
void expander_random_walk(Vertex start, int m, int steps, Vertex *path) {
    Vertex current = start;
    path[0] = current;
    Vertex neighbors[8];

    for (int k = 1; k <= steps; ++k) {
        get_mgg_neighbors(current, m, neighbors);
        int next_idx = rand() % 8;
        current = neighbors[next_idx];
        path[k] = current;
    }
}

// Монотонний нормалізатор вектора
static void normalize_vector(double *v, int size) {
    double norm = 0.0;
    for (int i = 0; i < size; ++i) {
        norm += v[i] * v[i];
    }
    norm = sqrt(norm);
    if (norm > 1e-12) {
        for (int i = 0; i < size; ++i) {
            v[i] /= norm;
        }
    }
}

// Ортогоналізація відносно постійного першого власного вектора v1 = (1/√N, ..., 1/√N)
static void project_perpendicular_to_v1(double *v, int size) {
    double sum = 0.0;
    for (int i = 0; i < size; ++i) {
        sum += v[i];
    }
    double avg = sum / size;
    for (int i = 0; i < size; ++i) {
        v[i] -= avg;
    }
}

// Обчислення другого власного значення λ2 методом степенів (Power Iteration)
double compute_mgg_lambda2(int m, int max_iterations, double tol) {
    int N = m * m;
    double *v = (double *)malloc(N * sizeof(double));
    double *next_v = (double *)malloc(N * sizeof(double));

    if (!v || !next_v) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        free(v);
        free(next_v);
        return -1.0;
    }

    // Ініціалізація випадковим вектором
    for (int i = 0; i < N; ++i) {
        v[i] = ((double)rand() / RAND_MAX) - 0.5;
    }

    project_perpendicular_to_v1(v, N);
    normalize_vector(v, N);

    double lambda2 = 0.0;
    Vertex neighbors[8];

    for (int iter = 0; iter < max_iterations; ++iter) {
        // Множення на матрицю суміжності: next_v = A * v
        for (int i = 0; i < N; ++i) {
            next_v[i] = 0.0;
        }

        for (int idx = 0; idx < N; ++idx) {
            Vertex cur = {idx / m, idx % m};
            get_mgg_neighbors(cur, m, neighbors);
            for (int k = 0; k < 8; ++k) {
                int n_idx = neighbors[k].x * m + neighbors[k].y;
                next_v[n_idx] += v[idx];
            }
        }

        // Ортогоналізація відносно v1 для видалення компоненти першого власного вектора (λ1 = 8)
        project_perpendicular_to_v1(next_v, N);

        // Оцінка значення Рейлі: λ2 = v^T * next_v
        double rayleigh = 0.0;
        for (int i = 0; i < N; ++i) {
            rayleigh += v[i] * next_v[i];
        }

        normalize_vector(next_v, N);

        double diff = fabs(rayleigh - lambda2);
        lambda2 = rayleigh;

        for (int i = 0; i < N; ++i) {
            v[i] = next_v[i];
        }

        if (diff < tol) {
            break;
        }
    }

    free(v);
    free(next_v);
    return lambda2;
}

int main(void) {
    int m = 12; // Сітка 12x12 (N = 144)
    printf("--- Тестування графа Маргуліса — Габбера — Галіля (m = %d, N = %d) ---\n", m, m * m);

    Vertex start = {0, 0};
    Vertex neighbors[8];
    get_mgg_neighbors(start, m, neighbors);

    printf("Сусіди вершини (0, 0):\n");
    for (int i = 0; i < 8; ++i) {
        printf("  Сусід %d: (%d, %d)\n", i + 1, neighbors[i].x, neighbors[i].y);
    }

    double lambda2 = compute_mgg_lambda2(m, 500, 1e-6);
    double gap = 8.0 - lambda2;

    printf("\nСпектральний аналіз:\n");
    printf("  d (степінь) = 8\n");
    printf("  λ₂ (друге власне значення) = %.6f\n", lambda2);
    printf("  Спектральна щілина γ = d - λ₂ = %.6f\n", gap);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <array>
#include <numeric>
#include <iomanip>

struct Vertex {
    int x{0};
    int y{0};

    bool operator==(const Vertex& other) const {
        return x == other.x && y == other.y;
    }
};

class MargulisExpander {
public:
    explicit MargulisExpander(int m) : m_grid_size(m), m_num_vertices(m * m) {}

    [[nodiscard]] int grid_size() const noexcept { return m_grid_size; }
    [[nodiscard]] int num_vertices() const noexcept { return m_num_vertices; }
    [[nodiscard]] static constexpr int degree() noexcept { return 8; }

    [[nodiscard]] std::array<Vertex, 8> get_neighbors(Vertex v) const noexcept {
        const int x = v.x;
        const int y = v.y;
        const int m = m_grid_size;

        auto mod_m = [m](int a) noexcept -> int {
            int r = a % m;
            return r < 0 ? r + m : r;
        };

        return std::array<Vertex, 8>{
            Vertex{x, mod_m(y + x)},
            Vertex{x, mod_m(y - x)},
            Vertex{x, mod_m(y + x + 1)},
            Vertex{x, mod_m(y - x - 1)},
            Vertex{mod_m(x + y), y},
            Vertex{mod_m(x - y), y},
            Vertex{mod_m(x + y + 1), y},
            Vertex{mod_m(x - y - 1), y}
        };
    }

    [[nodiscard]] std::vector<Vertex> random_walk(Vertex start, size_t steps) const {
        std::vector<Vertex> path;
        path.reserve(steps + 1);
        path.push_back(start);

        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<size_t> dist(0, 7);

        Vertex current = start;
        for (size_t i = 0; i < steps; ++i) {
            auto neighbors = get_neighbors(current);
            current = neighbors[dist(gen)];
            path.push_back(current);
        }
        return path;
    }

    [[nodiscard]] double compute_spectral_gap(size_t max_iterations = 500, double tol = 1e-6) const {
        const size_t N = m_num_vertices;
        std::vector<double> v(N);

        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_real_distribution<double> dist(-0.5, 0.5);

        for (auto& val : v) {
            val = dist(gen);
        }

        project_perpendicular_to_v1(v);
        normalize_vector(v);

        double lambda2 = 0.0;
        std::vector<double> next_v(N, 0.0);

        for (size_t iter = 0; iter < max_iterations; ++iter) {
            std::fill(next_v.begin(), next_v.end(), 0.0);

            for (size_t idx = 0; idx < N; ++idx) {
                Vertex cur{static_cast<int>(idx / m_grid_size), static_cast<int>(idx % m_grid_size)};
                auto neighbors = get_neighbors(cur);
                for (const auto& n : neighbors) {
                    size_t n_idx = static_cast<size_t>(n.x * m_grid_size + n.y);
                    next_v[n_idx] += v[idx];
                }
            }

            project_perpendicular_to_v1(next_v);

            double rayleigh = 0.0;
            for (size_t i = 0; i < N; ++i) {
                rayleigh += v[i] * next_v[i];
            }

            normalize_vector(next_v);

            double diff = std::abs(rayleigh - lambda2);
            lambda2 = rayleigh;
            v = next_v;

            if (diff < tol) {
                break;
            }
        }

        return static_cast<double>(degree()) - lambda2;
    }

private:
    int m_grid_size;
    int m_num_vertices;

    static void normalize_vector(std::vector<double>& vec) noexcept {
        double norm = 0.0;
        for (double val : vec) {
            norm += val * val;
        }
        norm = std::sqrt(norm);
        if (norm > 1e-12) {
            for (double& val : vec) {
                val /= norm;
            }
        }
    }

    static void project_perpendicular_to_v1(std::vector<double>& vec) noexcept {
        double sum = std::accumulate(vec.begin(), vec.end(), 0.0);
        double avg = sum / static_cast<double>(vec.size());
        for (double& val : vec) {
            val -= avg;
        }
    }
};

int main() {
    std::cout << std::fixed << std::setprecision(6);
    int m = 12;
    MargulisExpander expander(m);

    std::cout << "=== C++ Реалізація графа Маргуліса — Габбера — Галіля ===" << std::endl;
    std::cout << "Розмір сітки m = " << m << ", Вершин N = " << expander.num_vertices() << std::endl;

    Vertex start{0, 0};
    auto neighbors = expander.get_neighbors(start);
    std::cout << "\nСусіди вершини (0, 0):" << std::endl;
    for (size_t i = 0; i < neighbors.size(); ++i) {
        std::cout << "  [" << i + 1 << "] (" << neighbors[i].x << ", " << neighbors[i].y << ")\n";
    }

    double gap = expander.compute_spectral_gap();
    double lambda2 = static_cast<double>(expander.degree()) - gap;

    std::cout << "\nРезультати спектрального аналізу:" << std::endl;
    std::cout << "  Степінь d = " << expander.degree() << std::endl;
    std::cout << "  λ₂ = " << lambda2 << std::endl;
    std::cout << "  Спектральна щілина γ = d - λ₂ = " << gap << std::endl;

    return 0;
}
```
:::

## Аналіз пасток реалізації та інженерні тонкощі

Під час реалізації та порівняльного аналізу алгоритмів на розширювачах виникає кілька типових системних пасток:

1. **Пастка від'ємної остачі в математиці C/C++:**
   У стандартах мов C99 та C++11 операція `a % m` реалізує так зване truncation division (ділення з відкиданням дробової частини). Це означає, що для від'ємного чисельника результати є від'ємними (наприклад, `-1 % 12` повертає `-1`, а не `11`). Використання виразу `(y - x) % m` без примусового додавання `+ m` призводить до звернення за від'ємними індексами масиву та аварійного завершення програми (`Segmentation Fault`).

2. **Чисельний дрейф та накопичення похибок у Power Iteration:**
   Оскільки перше власне значення `λ₁ = 8` є більшим за `λ₂`, під час ітерацій навіть крихітна похибка заокруглення чисел із плаваючою точкою (float/double) створює паразитно виростаючу компоненту у напрямку вектора `v₁ = (1, ..., 1)ᵀ`. Без регулярного виклику процедури `project_perpendicular_to_v1` на кожній ітерації алгоритм Power Iteration невідворотно зіб'ється на обчислення головного власного значення `λ₁ = 8` замість шуканого `λ₂`.

3. **Оптимізація локальності кеш-пам'яті (Cache Locality):**
   При обчисленні `next_v[n_idx] += v[idx]` розсіяні записи в масив `next_v` викликають нерегулярний доступ до оперативної пам'яті (Cache Misses). У високонавантажених C++ серверах доцільно розбити вектор на L1-кешовані блоки розміром `m × m` або застосовувати двовимірний масив замість плоского векторного розкладу.

4. **Розпаралелювання за допомогою OpenMP:**
   Зовнішній цикл множення `for (int idx = 0; idx < N; ++idx)` не має перехресних залежностей за даними при зчитуванні `v[idx]`. Однак запис у `next_v[n_idx]` вимагає атомарного підсумовування `#pragma omp atomic` або використання локальних векторів для кожного потоку з подальшим редукційним додаванням.

5. **Точність типів із плаваючою точкою (Float vs Double):**
   Для графів великого розміру (`N > 10⁶`) використання 32-бітного типу `float` призводить до передчасної втрати точності під час ортогоналізаційного віднімання `v[i] -= avg`. Використання 64-бітного типу `double` або 80-бітного `long double` є обов'язковим для збереження стійкості методу ітерацій.
