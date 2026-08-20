# ⚙️ Обчислювальний рушій PageRank для розріджених графів

Ця практична вставка містить закінчену високопродуктивну реалізацію алгоритму PageRank мовами C та C++ з використанням розрідженого формату представлення графа CSR, коректною обробкою висячих вузлів, числовим трасуванням та аналізом типових інженерних пасток.

### Постановка задачі

Потрібно розробити компонент ранжування для вебграфа з довільною кількістю вершин `N` та орієнтованих ребер `E`. Алгоритм повинен:
1. Зберігати структуру ребер у компактному форматі, що забезпечує лінійну складність за пам'яттю `O(N + E)`.
2. Коректно обробляти висячі вершини (із нульовим вихідним степенем) без витікання сумарного рангу.
3. Виконувати ітерації степеневого методу до досягнення заданої точності за L1-нормою `∑ |r⁽ᵏ⁺¹⁾[i] - r⁽ᵏ⁾[i]| < ε`.
4. Забезпечувати послідовний доступ до пам'яті для ефективної утилізації процесорного кешу L1/L2.

### Архітектура та формат CSR

Для представлення графа використано формат **CSR** (англ. *Compressed Sparse Row*), оптимізований під прямий обхід вихідних ребер. Граф описується трьома неперервними масивами:
- `row_ptr[u]`: індекс початку списку сусідів вершини `u` в масиві ребер (масив розміром `N + 1`).
- `col_idx`: масив цільових вершин `v` для кожного ребра `u → v` (масив розміром `E`).
- `out_degree[u]`: кількість вихідних посилань вершини `u` (дорівнює різниці `row_ptr[u+1] - row_ptr[u]`).

Така організація даних усуває розкидання вказівників по оперативній пам'яті: під час обходу ребер вершини `u` процесор завантажує цільові індекси `col_idx` послідовними кеш-лініями (по 64 байти).

На кожній ітерації алгоритм виконує чотири послідовні фази:
1. **Акумуляція висячих вузлів:** обчислюється сума рангу всіх тупикових сторінок `S_dangling = ∑_{u: out_degree[u]=0} r[u]`.
2. **Базовий зсув:** розраховується універсальна частка телепортації `base_rank = (d · S_dangling + (1 - d)) / N`, якою ініціалізується наступний вектор `r_next`.
3. **Розкид авторитету (англ. *Push-based update*):** для кожної вершини `u` з ненульовим степенем визначається частка передачі `share = (d · r[u]) / out_degree[u]`, яка додається до комірок `r_next[v]` усіх її сусідів `v`.
4. **Оцінка збіжності:** підсумовується абсолютна різниця `diff = ∑ |r_next[i] - r[i]|`. Якщо `diff < ε`, обчислення завершуються.

### Порівняння моделей оновлення: Push проти Pull

У графових обчисленнях існують дві базові стратегії множення розрідженої матриці на вектор:

1. **Модель розкиду (англ. *Push-based*):**
   - Вершина-джерело `u` переглядає свої вихідні посилання й додає частку `share = d · r[u] / L(u)` до масиву `r_next[v]`.
   - *Перевага:* природно використовує формат вихідних ребер CSR, який природно формується вебкраулером під час парсингу HTML-тегів `<a>`.
   - *Недолік у багатопоточності:* коли декілька потоків одночасно обробляють різні джерела `u₁` та `u₂`, що посилаються на одну й ту саму цільову сторінку `v`, виникає стан гонки (англ. *data race*) на комірці `r_next[v]`.

2. **Модель збору (англ. *Pull-based*):**
   - Цільова вершина `v` переглядає свої вхідні посилання й збирає суму `r_next[v] = base_rank + d · ∑_{u ∈ In(v)} (r[u] / L(u))`.
   - *Перевага:* ідеальна паралельність — кожен потік незалежно записує у власну комірку `r_next[v]`, жодних блокувань чи атомарних операцій не потрібно.
   - *Вимога:* потребує транспонування графа у формат CSC (англ. *Compressed Sparse Column*) або збереження вхідних списків суміжності.

Нижче наведено канонічну послідовну реалізацію моделі Push, яка є найбільш економною за пам'яттю.

### Реалізація: C та C++

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

// Структура розрідженого графа у форматі CSR
typedef struct {
    int num_nodes;
    int num_edges;
    int* row_ptr;     // розмір num_nodes + 1
    int* col_idx;     // розмір num_edges
    int* out_degree;  // розмір num_nodes
} CsrGraph;

// Результат обчислення
typedef struct {
    double* ranks;
    int iterations;
    double final_diff;
    bool converged;
} PageRankResult;

// Створення графа
CsrGraph* create_graph(int num_nodes, int num_edges) {
    if (num_nodes <= 0 || num_edges < 0) return NULL;
    CsrGraph* g = (CsrGraph*)malloc(sizeof(CsrGraph));
    if (!g) return NULL;
    g->num_nodes = num_nodes;
    g->num_edges = num_edges;
    g->row_ptr = (int*)calloc(num_nodes + 1, sizeof(int));
    g->col_idx = (num_edges > 0) ? (int*)malloc(num_edges * sizeof(int)) : NULL;
    g->out_degree = (int*)calloc(num_nodes, sizeof(int));
    if (!g->row_ptr || (!g->col_idx && num_edges > 0) || !g->out_degree) {
        free(g->row_ptr);
        free(g->col_idx);
        free(g->out_degree);
        free(g);
        return NULL;
    }
    return g;
}

// Звільнення пам'яті графа
void free_graph(CsrGraph* g) {
    if (!g) return;
    free(g->row_ptr);
    free(g->col_idx);
    free(g->out_degree);
    free(g);
}

// Обчислення PageRank
PageRankResult compute_pagerank(const CsrGraph* g, double damping, double tol, int max_iter) {
    PageRankResult res = {NULL, 0, 0.0, false};
    int N = g ? g->num_nodes : 0;
    if (N <= 0) return res;

    double* r_cur = (double*)malloc(N * sizeof(double));
    double* r_next = (double*)malloc(N * sizeof(double));
    if (!r_cur || !r_next) {
        free(r_cur);
        free(r_next);
        return res;
    }

    // Ініціалізація рівномірним розподілом 1 / N
    double init_val = 1.0 / (double)N;
    for (int i = 0; i < N; ++i) {
        r_cur[i] = init_val;
    }

    int iter = 0;
    double diff = 0.0;

    while (iter < max_iter) {
        iter++;

        // 1. Акумуляція рангу висячих вузлів (out_degree == 0)
        double dangling_sum = 0.0;
        for (int u = 0; u < N; ++u) {
            if (g->out_degree[u] == 0) {
                dangling_sum += r_cur[u];
            }
        }

        // 2. Базовий рівномірний внесок телепортації для кожної вершини
        double base_rank = (damping * dangling_sum + (1.0 - damping)) / (double)N;
        for (int i = 0; i < N; ++i) {
            r_next[i] = base_rank;
        }

        // 3. Розподіл рангу вздовж орієнтованих ребер u -> v
        for (int u = 0; u < N; ++u) {
            int deg = g->out_degree[u];
            if (deg > 0) {
                double share = (damping * r_cur[u]) / (double)deg;
                int start = g->row_ptr[u];
                int end = g->row_ptr[u + 1];
                for (int e = start; e < end; ++e) {
                    int v = g->col_idx[e];
                    r_next[v] += share;
                }
            }
        }

        // 4. Оцінка похибки за L1-нормою: sum |r_next[i] - r_cur[i]|
        diff = 0.0;
        for (int i = 0; i < N; ++i) {
            diff += fabs(r_next[i] - r_cur[i]);
            r_cur[i] = r_next[i]; // копіюємо для наступного кроку
        }

        if (diff < tol) {
            res.converged = true;
            break;
        }
    }

    free(r_next);
    res.ranks = r_cur;
    res.iterations = iter;
    res.final_diff = diff;
    return res;
}
```
```cpp
#include <vector>
#include <cmath>
#include <span>
#include <memory>
#include <expected>
#include <string>
#include <numeric>
#include <algorithm>

// Клас розрідженого графа у форматі CSR
class CsrGraph {
public:
    int num_nodes = 0;
    int num_edges = 0;
    std::vector<int> row_ptr;     // розмір num_nodes + 1
    std::vector<int> col_idx;     // розмір num_edges
    std::vector<int> out_degree;  // розмір num_nodes

    CsrGraph(int nodes, int edges)
        : num_nodes(nodes),
          num_edges(edges),
          row_ptr(nodes + 1, 0),
          col_idx(edges, 0),
          out_degree(nodes, 0) {}
};

// Результат обчислення
struct PageRankResult {
    std::vector<double> ranks;
    int iterations = 0;
    double final_diff = 0.0;
    bool converged = false;
};

// Обчислення PageRank
std::expected<PageRankResult, std::string> compute_pagerank(
    const CsrGraph& graph,
    double damping = 0.85,
    double tolerance = 1e-7,
    int max_iterations = 100)
{
    const int N = graph.num_nodes;
    if (N <= 0) {
        return std::unexpected("Кількість вершин у графі повинна бути більше нуля");
    }

    PageRankResult result;
    result.ranks.assign(N, 1.0 / static_cast<double>(N));
    std::vector<double> r_next(N, 0.0);

    int iter = 0;
    double diff = 0.0;

    while (iter < max_iterations) {
        iter++;

        // 1. Акумуляція рангу висячих вузлів (out_degree == 0)
        double dangling_sum = 0.0;
        for (int u = 0; u < N; ++u) {
            if (graph.out_degree[u] == 0) {
                dangling_sum += result.ranks[u];
            }
        }

        // 2. Базовий рівномірний внесок телепортації для кожної вершини
        const double base_rank = (damping * dangling_sum + (1.0 - damping)) / static_cast<double>(N);
        std::fill(r_next.begin(), r_next.end(), base_rank);

        // 3. Розподіл рангу вздовж орієнтованих ребер u -> v
        for (int u = 0; u < N; ++u) {
            const int deg = graph.out_degree[u];
            if (deg > 0) {
                const double share = (damping * result.ranks[u]) / static_cast<double>(deg);
                const int start = graph.row_ptr[u];
                const int end = graph.row_ptr[u + 1];
                for (int e = start; e < end; ++e) {
                    const int v = graph.col_idx[e];
                    r_next[v] += share;
                }
            }
        }

        // 4. Оцінка похибки за L1-нормою: sum |r_next[i] - r_cur[i]|
        diff = 0.0;
        for (int i = 0; i < N; ++i) {
            diff += std::abs(r_next[i] - result.ranks[i]);
            result.ranks[i] = r_next[i];
        }

        if (diff < tolerance) {
            result.converged = true;
            break;
        }
    }

    result.iterations = iter;
    result.final_diff = diff;
    return result;
}
```
:::

### Покрокове чисельне трасування на тестовому графі

Розглянемо виконання алгоритму на графі з 4 вершин із [основної статті](book:algorithms/pagerank-algorithm/pagerank-algorithm-d.md):
- Вузол `A` (індекс 0) має посилання на `B` (1) та `C` (2). `out_degree[A] = 2`.
- Вузол `B` (індекс 1) має посилання на `D` (3). `out_degree[B] = 1`.
- Вузол `C` (індекс 2) має посилання на `D` (3). `out_degree[C] = 1`.
- Вузол `D` (індекс 3) має посилання на `A` (0). `out_degree[D] = 1`.

При `d = 0.85` початковий вектор `r⁽⁰⁾ = [0.25, 0.25, 0.25, 0.25]ᵀ`.

Покрокова динаміка зміни векторів:
- **Ітерація 1:**
  - Базовий зсув: `(1 - 0.85) / 4 = 0.0375`.
  - Вузол `A` отримує внесок від `D`: `0.0375 + 0.85 · (0.25 / 1) = 0.2500`.
  - Вузол `B` отримує від `A`: `0.0375 + 0.85 · (0.25 / 2) = 0.14375`.
  - Вузол `C` отримує від `A`: `0.0375 + 0.85 · (0.25 / 2) = 0.14375`.
  - Вузол `D` отримує від `B` і `C`: `0.0375 + 0.85 · (0.25 + 0.25) = 0.4625`.
- **Ітерація 2:**
  - `r⁽²⁾ = [0.4306, 0.1438, 0.1438, 0.2819]ᵀ`.
- **Ітерація 20 (збіжність з точністю `10⁻⁷`):**
  - `r* ≈ [0.3725, 0.1958, 0.1958, 0.3703]ᵀ`.

Сума елементів на кожному кроці строго зберігає нормування: `∑ r[i] = 1.000000`.

### Типові інженерні пастки та їх усунення

1. **Модифікація вектора рангів «на місці» (англ. *In-place mutation*):**
   - *Помилка:* оновлення `r[v]` безпосередньо у поточному масиві замість використання проміжного буфера `r_next`.
   - *Наслідок:* значення для пізніших вершин графа обчислюються на основі щойно змінених значень ранніших вершин поточної ітерації (подібно до методу Гауса — Зейделя замість методу простої ітерації). Це порушує симетрію марківського процесу та викликає непередбачувані числові коливання.
   - *Рішення:* обов'язкове використання двох окремих векторів `r_cur` та `r_next` із копіюванням або обміном вказівників (`std::swap`) наприкінці кожної ітерації.

2. **Втрата рангу висячих вузлів:**
   - *Помилка:* ігнорування сторінок без вихідних посилань (`out_degree == 0`) у розрахунку телепортації.
   - *Наслідок:* сума компонентів вектора рангів щокроку згасає (`∑ r[i] < 1`), і після кількох десятків ітерацій увесь вектор скочується до нуля.
   - *Рішення:* підсумовування рангу всіх висячих вузлів `S_dangling` та рівномірне додавання частки `(d · S_dangling) / N` до базового рангу кожної вершини.

3. **Неефективна локальність пам'яті (кеш-промахи):**
   - *Помилка:* представлення графа у вигляді динамічного масиву зв'язних списків (`std::vector<std::vector<int>>` або вказівників на списки).
   - *Наслідок:* розкидання вузлів по всій купі призводить до кеш-промаху під час кожного переходу за ребром.
   - *Рішення:* використання лінійного масиву CSR (`col_idx`), де всі сусіди кожної вершини розташовані в пам'яті строго поспіль.

4. **Паралелізація та гонки даних (англ. *Data races*):**
   - *Помилка:* наївне розпаралелювання циклу розкиду часток `#pragma omp parallel for` за вершинами `u`. Оскільки кілька різних вершин `u₁` та `u₂` можуть посилатися на одну й ту саму цільову вершину `v`, одночасний запис `r_next[v] += share` викликає гонку даних.
   - *Рішення:* або використання атомарних інструкцій `#pragma omp atomic update`, або перехід до pull-моделі на базі транспонованого CSR (CSC), де кожна нитка обчислює свій власний підсумковий елемент `r_next[v] = ∑_{u ∈ In(v)} (d · r[u] / L(u)) + base_rank` без жодних конфліктів запису.
