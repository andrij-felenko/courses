# ⚙️ Практичні алгоритми розв'язання задачі комівояжера: DP, 2-Opt та Branch and Bound

Практична реалізація алгоритмів розв'язання задачі комівояжера (TSP) вимагає суворого узгодження обчислювальної складності з архітектурними особливостями сучасних процесорів та підсистеми пам'яті. У той час як теоретичний опис оперує абстрактними графами, програмна інженерія зіштовхується з обмеженнями розміру кеш-пам'яті L1/L2/L3, вирівнюванням даних у ОЗП, бітовими зсувами та можливістю локальної оптимізації через низькорівневий паралелізм.

Цей розділ містить детальний практичний розбір двох фундаментальних підходів: точного алгоритму динамічного програмування Хелда-Карпа для малих графів (`n ≤ 20`) та високопродуктивної евристики локального пошуку 2-Opt для великих графів (`n > 50`), реалізованих мовами C та C++.

---

## 1. Точний розв'язок: Алгоритм Хелда-Карпа на бітових масках

Алгоритм динамічного програмування Хелда-Карпа дозволяє знизити складність розв meзання з часової факторіальної межі `O(n!)` до експоненціальної `O(n² · 2ⁿ)`. Основним інструментом інженерної реалізації цього алгоритму є **бітові маски** (bitmasks), де ціле беззнакове число `uint32_t` або `uint64_t` слугує компактним поданням підмножини відвіданих вершин.

### 1.1. Математика бітового кодування та кеш-оптимізація

Нехай граф містить `n` вершин з номерами від `0` до `n-1`. Довільна підмножина вершин `S ⊆ V` кодується двійковим цілим числом `mask`, у якому `i`-й біт встановлено в `1`, якщо вершина `i` належить до підмножини `S`, і в `0`, якщо вершина `i` відсутня у підмножині `S`:

```
mask = ∑_{i ∈ S} (1 << i)
```

Операції над підмножинами виконуються за один такт процесора за допомогою побітових інструкцій:
- **Перевірка належності вершини `v` до підмножини `S`:** `(mask & (1U << v)) != 0`
- **Додавання вершини `v` до підмножини `S`:** `next_mask = mask | (1U << v)`
- **Вилучення вершини `v` з підмножини `S`:** `prev_mask = mask ^ (1U << v)`

Матриця станів динамічного програмування зберігається в пам meті як двовимірний масив `dp[num_states][n]`, де `num_states = 1U << n`. Елемент `dp[mask][u]` містить довжину найкоротшого шляху, який починається в базі (вершина `0`), відвідує всі вершини, позначені `1` у бітовій масці `mask`, і закінчується у вершині `u`.

З токи зору архітектури процесора, розгортання двовимірного масиву у плоский одновимірний вектор розміру `(1U << n) * n` забезпечує високу локальність даних у кеші L1/L2. Коли зовнішній цикл ітерується за зростанням бітової маски `mask`, сусідні стани потрапляють у той самий кеш-рядок (Cache Line), що мінімізує промахи кешу (Cache Misses).

---

### 1.2. Покроковий розбір алгоритму Хелда-Карпа на прикладі 4 вершин

Розглянемо покроковий процес обчислення станів для графа з `n = 4` вершинами `{0, 1, 2, 3}`.

1. **Ініціалізація (Базовий стан):**
   Встановлюємо `dp[1U << 0][0] = dp[1][0] = 0.0`. Усі інші елементи `dp[mask][u]` заповнюємо нескінченністю `INF`.

2. **Крок 1: Підмножини з 2 вершин (`|S| = 2`):**
   Розглядаємо маски `mask`, які містять біт `0` та ще один встановлений біт:
   - Для маски `0011` (`{0, 1}`): `dp[3][1] = dp[1][0] + w(0, 1) = w(0, 1)`
   - Для маски `0101` (`{0, 2}`): `dp[5][2] = dp[1][0] + w(0, 2) = w(0, 2)`
   - Для маски `1001` (`{0, 3}`): `dp[9][3] = dp[1][0] + w(0, 3) = w(0, 3)`

3. **Крок 2: Підмножини з 3 вершин (`|S| = 3`):**
   Розглядаємо маску `0111` (`{0, 1, 2}`):
   - Кінцева вершина `1`: `dp[7][1] = dp[0101][2] + w(2, 1) = dp[5][2] + w(2, 1)`
   - Кінцева вершина `2`: `dp[7][2] = dp[0011][1] + w(1, 2) = dp[3][1] + w(1, 2)`

4. **Крок 3: Повна маска `1111` (`{0, 1, 2, 3}`):**
   Обчислюємо значення `dp[15][u]` для всіх `u ∈ {1, 2, 3}` шляхом мінімізації по всіх можливих попередниках.

5. **Фінал (Замикання циклу):**
   Оптимальна довжина циклу шукається як `min { dp[15][u] + w(u, 0) | u ∈ {1, 2, 3} }`.

---

### 1.3. Повна реалізація алгоритму Хелда-Карпа

Поданий код реалізує точне розв meзання задачі комівояжера з відновленням оптимального маршруту. У вкладці C застосовано плоский одновимірний масив для мінімізації накладних витрат виділення пам'яті, а у вкладці C++ використано контейнери `std::vector` з дотриманням ідіом RAII.

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

#define INF 1e9

typedef struct {
    double min_cost;
    int* path;
    size_t path_len;
} tsp_solution_t;

/**
 * Точний розв'язок задачі комівояжера алгоритмом Хелда-Карпа на мові C.
 * Приймає плоску матрицю відстаней розміром n x n у форматі row-major.
 */
tsp_solution_t tsp_held_karp_c(const double* matrix, size_t n) {
    tsp_solution_t res = {INF, NULL, 0};
    
    /* Перевірка граничних умов: бітові маски uint32_t обмежені 32 вершинами,
       але практичний ліміт пам'яті досягається при n <= 20 (2^20 * 20 * 8 байт ≈ 168 МБ) */
    if (n == 0 || n > 20) {
        return res;
    }

    size_t num_states = 1U << n;
    
    /* Виділення суцільного блоку пам'яті для DP-таблиці та баз даних відновлення шляху */
    double* dp = (double*)malloc(num_states * n * sizeof(double));
    int* parent = (int*)malloc(num_states * n * sizeof(int));

    if (!dp || !parent) {
        free(dp);
        free(parent);
        return res;
    }

    /* Ініціалізація DP-таблиці нескінченністю INF */
    for (size_t s = 0; s < num_states; ++s) {
        for (size_t i = 0; i < n; ++i) {
            dp[s * n + i] = INF;
            parent[s * n + i] = -1;
        }
    }

    /* Базовий стан: старт у вершині 0, у масці встановлено лише 0-й біт (1U << 0) */
    dp[(1U << 0) * n + 0] = 0.0;

    /* Ітерація за зростанням бітової маски запевнює, що підзадачі меншого розміру
       обчислюються раніше за підзадачі більшого розміру */
    for (uint32_t mask = 1; mask < num_states; ++mask) {
        /* Якщо 0-й біт не встановлено, дана маска не містить початкову вершину 0 */
        if (!(mask & 1U)) continue;

        for (size_t u = 0; u < n; ++u) {
            /* Перевіряємо, чи входить вершина u до поточної маски */
            if (!(mask & (1U << u))) continue;
            
            double current_cost = dp[mask * n + u];
            if (current_cost >= INF) continue;

            /* Пробуємо перейти до всіх ще не відвіданих вершин v */
            for (size_t v = 0; v < n; ++v) {
                if (mask & (1U << v)) continue; /* Вершина v вже відвідана */

                uint32_t next_mask = mask | (1U << v);
                double weight = matrix[u * n + v];
                double new_cost = current_cost + weight;

                /* Оновлюємо рекурентне співвідношення Хелда-Карпа */
                if (new_cost < dp[next_mask * n + v]) {
                    dp[next_mask * n + v] = new_cost;
                    parent[next_mask * n + v] = (int)u;
                }
            }
        }
    }

    /* Фінальний крок: знаходження найкращого замикання циклу назад до вершини 0 */
    uint32_t full_mask = (1U << n) - 1;
    size_t last_node = 0;
    
    for (size_t u = 1; u < n; ++u) {
        double cost = dp[full_mask * n + u] + matrix[u * n + 0];
        if (cost < res.min_cost) {
            res.min_cost = cost;
            last_node = u;
        }
    }

    /* Відновлення послідовності вершин шляхом зворотного проходу по масиву parent */
    res.path = (int*)malloc((n + 1) * sizeof(int));
    if (res.path) {
        res.path_len = n + 1;
        uint32_t curr_mask = full_mask;
        size_t curr_node = last_node;
        
        for (int i = (int)n - 1; i >= 1; --i) {
            res.path[i] = (int)curr_node;
            int prev = parent[curr_mask * n + curr_node];
            curr_mask ^= (1U << curr_node);
            curr_node = (size_t)prev;
        }
        res.path[0] = 0;
        res.path[n] = 0;
    }

    free(dp);
    free(parent);
    return res;
}
```

@tab C++
```cpp
#include <vector>
#include <limits>
#include <cstdint>
#include <algorithm>

struct TspResult {
    double min_cost{std::numeric_limits<double>::infinity()};
    std::vector<size_t> path;
};

/**
 * Ідіоматична реалізація алгоритму Хелда-Карпа на C++ з використанням std::vector.
 */
TspResult tsp_held_karp_cpp(const std::vector<std::vector<double>>& matrix) {
    const size_t n = matrix.size();
    if (n == 0 || n > 20) return {};

    const uint32_t num_states = 1U << n;
    constexpr double inf = std::numeric_limits<double>::infinity();

    /* Таблиця DP розміром (2^n) x n з автоматичним очищенням пам'яті */
    std::vector<std::vector<double>> dp(num_states, std::vector<double>(n, inf));
    std::vector<std::vector<int>> parent(num_states, std::vector<int>(n, -1));

    dp[1U << 0][0] = 0.0;

    for (uint32_t mask = 1; mask < num_states; ++mask) {
        if (!(mask & 1U)) continue;

        for (size_t u = 0; u < n; ++u) {
            if (!(mask & (1U << u))) continue;
            if (dp[mask][u] == inf) continue;

            for (size_t v = 0; v < n; ++v) {
                if (mask & (1U << v)) continue;

                uint32_t next_mask = mask | (1U << v);
                double new_cost = dp[mask][u] + matrix[u][v];

                if (new_cost < dp[next_mask][v]) {
                    dp[next_mask][v] = new_cost;
                    parent[next_mask][v] = static_cast<int>(u);
                }
            }
        }
    }

    uint32_t full_mask = (1U << n) - 1;
    TspResult result;
    size_t last_node = 0;

    for (size_t u = 1; u < n; ++u) {
        if (dp[full_mask][u] == inf) continue;
        double total = dp[full_mask][u] + matrix[u][0];
        if (total < result.min_cost) {
            result.min_cost = total;
            last_node = u;
        }
    }

    if (result.min_cost == inf) return result;

    /* Зворотний трекінг для відновлення гамільтонового циклу */
    result.path.resize(n + 1);
    uint32_t curr_mask = full_mask;
    size_t curr_node = last_node;

    for (int i = static_cast<int>(n) - 1; i >= 1; --i) {
        result.path[i] = curr_node;
        int prev = parent[curr_mask][curr_node];
        curr_mask ^= (1U << curr_node);
        curr_node = static_cast<size_t>(prev);
    }
    result.path[0] = 0;
    result.path[n] = 0;

    return result;
}
```
:::

---

## 2. Швидка евристика локального пошуку 2-Opt

Для задач великої розмірності (`n > 50` або навіть `n = 100 000`) точні експоненціальні алгоритми є непридатними. Основною практичною альтернативою є евристики локального пошуку, серед яких найпопулярнішим алгоритмом є **2-Opt**.

### 2.1. Геометрична та кодова логіка 2-Opt

Алгоритм 2-Opt працює шляхом ітеративного вилучення двох ребер `(u, v)` та `(x, y)` з поточного замкненого маршруту і заміну їх на дві нові ребра `(u, x)` та `(v, y)`. На масиві вершин `tour` ця операція відповідає дзеркальному розвороту (реверсу) підмасиву елементів між індексами `i + 1` та `j`.

Умова покращення маршруту:

```
w(u, x) + w(v, y) < w(u, v) + w(x, y)
```

Якщо ця умова виконується, заміщення ребер гарантовано зменшує загальну довжину маршруту.

Аналіз індексів при заміни ребер:
Нехай початковий маршрут задано масивом `[A, B, C, D, E, A]`.
Якщо обрано `i = 0` (вершина `A`, ребро `A-B`) та `j = 2` (вершина `C`, ребро `C-D`):
- Старі ребра: `(A, B)` та `(C, D)`.
- Нові ребра: `(A, C)` та `(B, D)`.
- Реверс підмасиву від індексу `i+1 = 1` до `j = 2` (елементи `B, C`) перетворює порядок на `[A, C, B, D, E, A]`.
- Усі внутрішні ребра сегмента між `i+1` та `j` розвертаються у зворотному напрямку. Для симетричних графах це не змінює їхню довжину.

---

### 2.2. Повна реалізація евристики 2-Opt

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

/**
 * Обчислення повної довжини замкненого маршруту за матрицею відстаней.
 */
static double calculate_tour_length(const int* tour, size_t n, const double* matrix) {
    double len = 0.0;
    for (size_t i = 0; i < n; ++i) {
        size_t u = (size_t)tour[i];
        size_t v = (size_t)tour[(i + 1) % n];
        len += matrix[u * n + v];
    }
    return len;
}

/**
 * Локальна оптимізація маршруту алгоритмом 2-Opt у стилі C.
 * Виконує ітеративний розворот підмасивів до досягнення локального оптимуму.
 */
void tsp_2opt_refine_c(int* tour, size_t n, const double* matrix) {
    if (n < 4) return;
    bool improved = true;

    while (improved) {
        improved = false;
        for (size_t i = 0; i < n - 1; ++i) {
            for (size_t j = i + 2; j < n; ++j) {
                /* Пропускаємо випадок, коли i=0 та j=n-1, оскільки це та сама пара ребер */
                if (i == 0 && j == n - 1) continue;

                size_t u = (size_t)tour[i];
                size_t v = (size_t)tour[i + 1];
                size_t x = (size_t)tour[j];
                size_t y = (size_t)tour[(j + 1) % n];

                double current_dist = matrix[u * n + v] + matrix[x * n + y];
                double new_dist = matrix[u * n + x] + matrix[v * n + y];

                /* Враховуємо похибку плаваючої крапки 1e-9 для уникнення нескінченних циклів */
                if (new_dist < current_dist - 1e-9) {
                    /* Реверс підмасиву елементів від i+1 до j включно */
                    size_t left = i + 1, right = j;
                    while (left < right) {
                        int temp = tour[left];
                        tour[left] = tour[right];
                        tour[right] = temp;
                        left++;
                        right--;
                    }
                    improved = true;
                }
            }
        }
    }
}
```

@tab C++
```cpp
#include <vector>
#include <numeric>
#include <algorithm>

/**
 * Обчислення сумарної довжини маршруту на C++.
 */
double calculate_tour_length(const std::vector<size_t>& tour, 
                            const std::vector<std::vector<double>>& matrix) {
    double total = 0.0;
    const size_t n = tour.size();
    for (size_t i = 0; i < n; ++i) {
        total += matrix[tour[i]][tour[(i + 1) % n]];
    }
    return total;
}

/**
 * Ідіоматична C++ реалізація евристики 2-Opt з використанням std::reverse.
 */
void tsp_2opt_refine_cpp(std::vector<size_t>& tour, 
                         const std::vector<std::vector<double>>& matrix) {
    const size_t n = tour.size();
    if (n < 4) return;
    bool improved = true;

    while (improved) {
        improved = false;
        for (size_t i = 0; i < n - 1; ++i) {
            for (size_t j = i + 2; j < n; ++j) {
                if (i == 0 && j == n - 1) continue;

                size_t u = tour[i];
                size_t v = tour[i + 1];
                size_t x = tour[j];
                size_t y = tour[(j + 1) % n];

                double current_dist = matrix[u][v] + matrix[x][y];
                double new_dist = matrix[u][x] + matrix[v][y];

                if (new_dist < current_dist - 1e-9) {
                    /* Ідіоматичний розворот діапазону в C++ */
                    std::reverse(tour.begin() + static_cast<ptrdiff_t>(i + 1), 
                                 tour.begin() + static_cast<ptrdiff_t>(j + 1));
                    improved = true;
                }
            }
        }
    }
}
```
:::

---

## 3. Критичні інженерні пастки реалізації

При розробці високопродуктивних солверів TSP розробники регулярно зіштовхуються з трьома категоріями помилок:

1. **Переповнення бітового зсуву (Bit Shift Overflow):**
   Вираз `1U << v` у мовах C та C++ виконує зсув 32-бітного цілого беззнакового числа. При `v ≥ 32` стається невизначена поведінка (Undefined Behavior, UB). Для підтримки масок до 64 вершин необхідно явно використовувати суфікс `ULL`: `1ULL << v`. Для `n > 64` слід переходити на спеціалізовані бітові масиви (наприклад, `std::bitset` або вектор `std::vector<uint64_t>`).

2. **Нестабільність порівнянь чисел з плаваючою крапкою:**
   Нагромадження похибок округлення чисел типу `double` під час тисяч операцій додавання може призводити до нескінченних циклів розвертання в 2-Opt (коли `new_dist` і `current_dist` відрізняються на `1e-16` через обмеження точності IEEE 754). Порівняння покращення слід обов meязково проводити з урахуванням епсилон-порогу: `new_dist < current_dist - 1e-9`.

3. **Застосування 2-Opt до асиметричних матриць:**
   Операція 2-Opt перевертає порядок проходження підмасиву між індексами `i+1` та `j`. Якщо граф є симетричним (`w[a][b] = w[b][a]`), вага реверсивного підшляху не змінюється. Проте якщо матриця є асиметричною (`w[a][b] ≠ w[b][a]`), розворот підмасиву змінює напрямок проходження усіх внутрішніх ребер, що робить швидку оцінку `w(u,x) + w(v,y)` некоректною і вимагає повного переобчислення ваг всього розверненого сегмента.

4. **Локальні мінімуми евристик:**
   Алгоритм 2-Opt гарантує досягнення лише локального оптимуму. Для виходу з локальних пасток у сучасних системах застосовують мультистарт (запуск 2-Opt з сотень випадкових початкових перестановок) або переходять до складніших евристик Lin-Kernighan (LKH) чи алгоритмів імітації відпалу (Simulated Annealing).
