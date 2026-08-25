# ⚙️ Алгоритм Гошена — Копельмана та метод системи неперетинних множин для моделювання перколації

Моделювання перколації на дискретних ґратках вимагає вимірювання структурних характеристик випадкових середовищ: знаходження зв'язаних компонент (кластерів), визначення їхніх розмірів та виявлення того, чи існує наскрізний (протікаючий) кластер, який з'єднує протилежні межі системи.

Канонічним рішенням для двовимірної квадратної ґратки розміром `N × N` є **алгоритм Гошена — Копельмана** (*Hoshen-Kopelman algorithm*, 1976), який інтегрує виявлення зв'язаності в однопрохідне растрове сканування ґратки з використанням високоефективної структури даних **системи неперетинних множин** (*Disjoint-Set Union, DSU*, або *Union-Find*).

---

## Математичний принцип та кроки алгоритму

Головне завдання алгоритму полягає у присвоєнні кожному відкритому вузлу ґратки числової мітки кластера так, щоб усі вузли, які належат до одного зв'язаного кластера, отримали однаковий ідентифікатор.

Алгоритм виконується за такі кроки:

1. **Ініціалізація та растрове сканування**: Ґратка обходиться послідовно рядок за рядком (зліва направо, зверху вниз). Для кожного вузла `(r, c)` перевіряється його стан. Якщо вузол закритий, переходимо до наступного.
2. **Локальна перевірка сусідам**: Для відкритого вузла `(r, c)` аналізуються лише два вже оброблені сусідні вузли: лівий `(r, c-1)` та верхній `(r-1, c)`.
3. **Правила маркування**:
   - Якщо обидва сусіди закриті (або знаходяться за межами ґратки), відкритому вузлу призначається **нова унікальна тимчасова мітка** `next_label++`.
   - Якщо відкритий лише один із двох сусідів, поточному вузлу присвоюється мітка цього відкритого сусіда.
   - Якщо відкриті обидва сусіди і вони вже мають **різні мітки** `label1` та `label2`, поточний вузол отримує одну з цих міток, а у структурі DSU реєструється зв'язок еквівалентності через операцію `Union(label1, label2)`.
4. **Канонізація міток та збирання статистики**: Після завершення однократного сканування виконується другий швидкий прохід по ґратці. Кожна тимчасова мітка замінюється на її канонічний корінь у DSU `Find(label)`. Одночасно підраховується кількість вузлів у кожному кластері та перевіряється перетин міток верхньої й нижньої (або лівої та правої) меж ґратки.

Завдяки техніці стиснення шляхів (*path compression*) у DSU, коли під час кожного пошуку кореневого елемента всі проміжні вузли перев'язуються безпосередньо до кореня, середня часова складність алгоритму Гошена — Копельмана є майже строго лінійною — `O(N² · α(N²))`, де `α` — обернена функція Аккермана. Для будь-які практичних розмірів ґраток `α(N²) ≤ 5`, що дає змогу моделювати ґратки з мільйонами вузлів за частки секунди.

---

## Альтернативний підхід: Алгоритм Леата (Leath Growth Algorithm)

У той час як алгоритм Гошена — Копельмана обробляє відразу всю ґратку для заданого `p`, для вивчення фрактальної структури поблизу `p_c` часто використовують **алгоритм Леата** (*Leath cluster growth algorithm*, 1976).

Алгоритм Леата вирощує один окремий кластер із центрального вузла-зародка:
1. Центральний вузол `(N/2, N/2)` позначається як активний фронт росту.
2. Для кожного сусіда активного вузла генерується випадкова величина: з ймовірністю `p` сусід приєднується до кластера і додається в чергу росту (BFS), а з ймовірністю `1 - p` позначається як смертельно заблокований.
3. Процес продовжується, поки черга росту не спустошиться (скінченний кластер) або поки кластер не досягне зовнішньої межі симуляційного вікна (протікаючий кластер).

Головна перевага алгоритму Леата полягає в тому, що він не вимагає збереження всієї матриці ґратки в пам'яті: стан вузлів генерується «динамічно на льоту» в міру просування фронту росту. Це дає змогу досліджувати кластери з мільйонами вузлів при незначному використанні оперативної пам'яті.

---

## Реалізація алгоритму Гошена — Копельмана

Нижче наведено повністю робочі реалізації моделі вузлової перколації та алгоритму Гошена — Копельмана мовами C++ та C. Приклад мовою C++ демонструє об'єктно-орієнтований підхід із використанням RAII, `std::vector` та випадкових генераторів `std::mt19937_64`. Приклад мовою C показує низькорівневе управління пам'яттю за допомогою `malloc`/`free` та стандартного `rand()`.

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <random>
#include <numeric>
#include <algorithm>

// Структура даних Система Неперетинних Множин (Union-Find)
class DisjointSetUnion {
private:
    std::vector<int> parent;
    std::vector<int> rank;

public:
    explicit DisjointSetUnion(int n) : parent(n + 1), rank(n + 1, 0) {
        std::iota(parent.begin(), parent.end(), 0);
    }

    // Пошук кореня з автоматичним стисненням шляху
    int find(int i) {
        if (parent[i] == i)
            return i;
        return parent[i] = find(parent[i]);
    }

    // Об'єднання двох міток за рангом
    void unite(int i, int j) {
        int root_i = find(i);
        int root_j = find(j);
        if (root_i != root_j) {
            if (rank[root_i] < rank[root_j]) {
                std::swap(root_i, root_j);
            }
            parent[root_j] = root_i;
            if (rank[root_i] == rank[root_j]) {
                rank[root_i]++;
            }
        }
    }
};

// Результати аналізу перколаційної сітки
struct PercolationResult {
    bool has_spanning_cluster;
    int total_clusters;
    int max_cluster_size;
    double occupied_fraction;
};

// Клас симуляції узлової перколації на 2D квадратній ґратці
class PercolationSimulation {
private:
    int N;
    double p;
    std::vector<uint8_t> grid; // 1 - відкритий вузол, 0 - закритий

public:
    PercolationSimulation(int size, double prob, uint64_t seed = 42)
        : N(size), p(prob), grid(size * size, 0) {
        
        std::mt19937_64 rng(seed);
        std::bernoulli_distribution dist(p);
        for (int i = 0; i < N * N; ++i) {
            grid[i] = dist(rng) ? 1 : 0;
        }
    }

    PercolationResult run_hoshen_kopelman() {
        std::vector<int> labels(N * N, 0);
        DisjointSetUnion dsu(N * N / 2 + 2);
        int next_label = 1;

        for (int r = 0; r < N; ++r) {
            for (int c = 0; c < N; ++c) {
                int idx = r * N + c;
                if (!grid[idx]) continue;

                int left_label = (c > 0 && grid[idx - 1]) ? labels[idx - 1] : 0;
                int top_label = (r > 0 && grid[idx - N]) ? labels[idx - N] : 0;

                if (left_label == 0 && top_label == 0) {
                    labels[idx] = next_label++;
                } else if (left_label != 0 && top_label == 0) {
                    labels[idx] = left_label;
                } else if (left_label == 0 && top_label != 0) {
                    labels[idx] = top_label;
                } else {
                    labels[idx] = left_label;
                    dsu.unite(left_label, top_label);
                }
            }
        }

        // Другий прохід: нормалізація міток та підрахунок розмірів
        std::vector<int> cluster_sizes(next_label, 0);
        for (int i = 0; i < N * N; ++i) {
            if (labels[i] > 0) {
                labels[i] = dsu.find(labels[i]);
                cluster_sizes[labels[i]]++;
            }
        }

        // Перевірка наскрізного протікання (з верхньої межі до нижньої)
        std::vector<uint8_t> top_roots(next_label, 0);
        std::vector<uint8_t> bottom_roots(next_label, 0);

        for (int c = 0; c < N; ++c) {
            if (labels[c] > 0) top_roots[labels[c]] = 1;
            if (labels[(N - 1) * N + c] > 0) bottom_roots[labels[(N - 1) * N + c]] = 1;
        }

        bool spanning = false;
        int active_clusters = 0;
        int max_size = 0;

        for (int l = 1; l < next_label; ++l) {
            if (cluster_sizes[l] > 0 && dsu.find(l) == l) {
                active_clusters++;
                if (cluster_sizes[l] > max_size) {
                    max_size = cluster_sizes[l];
                }
                if (top_roots[l] && bottom_roots[l]) {
                    spanning = true;
                }
            }
        }

        int occupied_count = 0;
        for (uint8_t cell : grid) occupied_count += cell;

        return {spanning, active_clusters, max_size, static_cast<double>(occupied_count) / (N * N)};
    }
};

int main() {
    const int grid_size = 200;
    const double p_val = 0.59274; // Близько до критичного порогу p_c ≈ 0.592746

    PercolationSimulation sim(grid_size, p_val, 12345);
    PercolationResult res = sim.run_hoshen_kopelman();

    std::cout << "Розмір ґратки: " << grid_size << "x" << grid_size << "\n";
    std::cout << "Частка відкритих вузлів p: " << res.occupied_fraction << "\n";
    std::cout << "Наявність наскрізного кластера: " << (res.has_spanning_cluster ? "ТАК" : "НІ") << "\n";
    std::cout << "Кількість кластерів: " << res.total_clusters << "\n";
    std::cout << "Розмір найбільшого кластера: " << res.max_cluster_size << "\n";

    return 0;
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

// Система неперетинних множин (DSU) мовою C
typedef struct {
    int *parent;
    int *rank;
    int size;
} DSU;

DSU* dsu_create(int size) {
    DSU *dsu = (DSU*)malloc(sizeof(DSU));
    dsu->parent = (int*)malloc((size + 1) * sizeof(int));
    dsu->rank = (int*)calloc(size + 1, sizeof(int));
    dsu->size = size;
    for (int i = 0; i <= size; i++) {
        dsu->parent[i] = i;
    }
    return dsu;
}

void dsu_free(DSU *dsu) {
    free(dsu->parent);
    free(dsu->rank);
    free(dsu);
}

int dsu_find(DSU *dsu, int i) {
    if (dsu->parent[i] == i)
        return i;
    return dsu->parent[i] = dsu_find(dsu, dsu->parent[i]);
}

void dsu_unite(DSU *dsu, int i, int j) {
    int root_i = dsu_find(dsu, i);
    int root_j = dsu_find(dsu, j);
    if (root_i != root_j) {
        if (dsu->rank[root_i] < dsu->rank[root_j]) {
            int tmp = root_i; root_i = root_j; root_j = tmp;
        }
        dsu->parent[root_j] = root_i;
        if (dsu->rank[root_i] == dsu->rank[root_j]) {
            dsu->rank[root_i]++;
        }
    }
}

typedef struct {
    bool has_spanning_cluster;
    int total_clusters;
    int max_cluster_size;
    double occupied_fraction;
} PercolationResultC;

PercolationResultC run_percolation_simulation_c(int N, double p, unsigned int seed) {
    srand(seed);
    uint8_t *grid = (uint8_t*)calloc(N * N, sizeof(uint8_t));
    int occupied_count = 0;

    for (int i = 0; i < N * N; i++) {
        if ((double)rand() / RAND_MAX < p) {
            grid[i] = 1;
            occupied_count++;
        }
    }

    int *labels = (int*)calloc(N * N, sizeof(int));
    DSU *dsu = dsu_create(N * N / 2 + 2);
    int next_label = 1;

    for (int r = 0; r < N; r++) {
        for (int c = 0; c < N; c++) {
            int idx = r * N + c;
            if (!grid[idx]) continue;

            int left = (c > 0 && grid[idx - 1]) ? labels[idx - 1] : 0;
            int top = (r > 0 && grid[idx - N]) ? labels[idx - N] : 0;

            if (left == 0 && top == 0) {
                labels[idx] = next_label++;
            } else if (left != 0 && top == 0) {
                labels[idx] = left;
            } else if (left == 0 && top != 0) {
                labels[idx] = top;
            } else {
                labels[idx] = left;
                dsu_unite(dsu, left, top);
            }
        }
    }

    int *cluster_sizes = (int*)calloc(next_label, sizeof(int));
    for (int i = 0; i < N * N; i++) {
        if (labels[i] > 0) {
            labels[i] = dsu_find(dsu, labels[i]);
            cluster_sizes[labels[i]]++;
        }
    }

    uint8_t *top_roots = (uint8_t*)calloc(next_label, sizeof(uint8_t));
    uint8_t *bottom_roots = (uint8_t*)calloc(next_label, sizeof(uint8_t));

    for (int c = 0; c < N; c++) {
        if (labels[c] > 0) top_roots[labels[c]] = 1;
        if (labels[(N - 1) * N + c] > 0) bottom_roots[labels[(N - 1) * N + c]] = 1;
    }

    bool spanning = false;
    int active_clusters = 0;
    int max_size = 0;

    for (int l = 1; l < next_label; l++) {
        if (cluster_sizes[l] > 0 && dsu_find(dsu, l) == l) {
            active_clusters++;
            if (cluster_sizes[l] > max_size) {
                max_size = cluster_sizes[l];
            }
            if (top_roots[l] && bottom_roots[l]) {
                spanning = true;
            }
        }
    }

    PercolationResultC res = {
        spanning,
        active_clusters,
        max_size,
        (double)occupied_count / (N * N)
    };

    free(grid);
    free(labels);
    free(cluster_sizes);
    free(top_roots);
    free(bottom_roots);
    dsu_free(dsu);

    return res;
}

int main() {
    int N = 200;
    double p = 0.59274;
    PercolationResultC res = run_percolation_simulation_c(N, p, 12345);

    printf("Модель C — Ґратка %dx%d\n", N, N);
    printf("Частка відкритих вузлів: %.5f\n", res.occupied_fraction);
    printf("Протікання: %s\n", res.has_spanning_cluster ? "ТАК" : "НІ");
    printf("Кількість кластерів: %d\n", res.total_clusters);
    printf("Найбільший кластер: %d вузлів\n", res.max_cluster_size);

    return 0;
}
```
:::

---

## Оптимізація пам'яті та кеш-локальності

Під час обробки масштабних ґраток (наприклад `10000 × 10000` з 100 мільйонами вузлів) вирішальне значення має ефективність використання L1/L2/L3 кешу процесора та мінімізація виділення пам'яті.

1. **Неперервний масив (Contiguous Layout)**: Ґратка представляється як єдиний одномірний вектор `std::vector<uint8_t>`, де елемент `(r, c)` адресується через `r * N + c`. Це виключає додаткові покажчики та забезпечує апаратну превибірку (*hardware prefetching*) рядків.
2. **Пакувальне зберігання станів (Bit-packing)**: Оскільки стан вузла (відкритий/закритий) потребує лише 1 біт інформації, 8 вузлів можна упакувати в 1 байт `uint8_t` або 64 вузли в `uint64_t`. Це зменшує обсяг пам'яті для матриці у 8 разів і прискорює растрове сканування через бітові операції `AND`/`OR`.
3. **Скелювання пам'яті для DSU**: У гіршому випадку шахової дошки розрядність міток не перевищує `N² / 2`. Масив батьківських посилань `parent` доцільно створювати розміром `N² / 2 + 2`, що економить пам'ять порівняно з розміром `N²`.

---

## Метод екстраполяції скінченнорозмірного скейлінгу

Для точного знаходження нескінченного порогу `p_c(∞)` вимірюють ймовірність протікання `П(p, N)` для серії систем різних розмірів `N ∈ {50, 100, 200, 500, 1000}`.

1. Для кожного `N` знаходять точку `p_c(N)`, де `П(p_c(N), N) = 0.5`.
2. Будують регресійну залежність `p_c(N)` від `N⁻¹/ⁿ`.
3. Точка перетину регресійної прямої з віссю ординат при `N⁻¹/ⁿ → 0` дає шукане термодинамічне значення `p_c(∞)` із точністю до `10⁻⁶`.
