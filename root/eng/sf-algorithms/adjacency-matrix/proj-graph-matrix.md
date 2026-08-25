# ⚙️ Реалізація матриці суміжності мовами C та C++

Ця практична вставка містить готові до використання, високопродуктивні реалізації матриці суміжності для орієнтованих і зважених графів мовами C та C++, з адаптивним виділенням пам'яті, кеш-орієнтованим плоским масивом та алгоритмом Флойда — Уоршелла.

Головною інженерною перевагою матриці суміжності є можливість її реалізації у вигляді одного суцільного буфера пам'яті (Flat 1D array). Це забезпечує максимальну локальність даних для кеш-пам'яті процесора (CPU Cache Locality), повністю виключає фрагментацію оперативної пам'яті та дозволяє ефективно обробляти ребра за допомогою симульованого двовимірного індексування `i * N + j`.

## 1. Архітектурний дизайн та вибір структури пам'яті

Під час проектирування структури даних для матриці суміжності перед розробником постає вибір між двома основними підходами до організації пам'яті в системних мовах програмування:

### 1.1. Динамічний вкладений масив (Array of Pointers або `std::vector<std::vector<T>>`)

Базовий навчальний підхід передбачає створення масиву вказівників довжиною `N`, де кожен вказівник веде на окремо виділений у купі масив елементів довжиною `N`. 

```
[ ptr_0 ]  --->  [ A[0][0], A[0][1], A[0][2], ..., A[0][N-1] ]
[ ptr_1 ]  --->  [ A[1][0], A[1][1], A[1][2], ..., A[1][N-1] ]
...
[ ptr_N-1 ] ---> [ A[N-1][0], A[N-1][1], ..., A[N-1][N-1] ]
```

Хоча цей підхід дозволяє використовувати зручний синтаксис `matrix[i][j]`, він має фундаментальні інженерні недоліки:
* Вимагає `N + 1` окремих викликів оператора `malloc` або створення об'єктів у купі, що спричиняє високий оверхед аллокатора.
* Створює значну фрагментацію оперативної пам'яті.
* Призводить до частих промахів кешу (Cache Misses) через переходи за вказівниками (*pointer chasing*). Коли процесор ітерується по масиву вказівників, кожен рядок розташований у довільній ділянці купи, що унеможливлює роботу префечера кешу.

### 1.2. Неперервний плоский буфер (Flat 1D Array або `std::vector<T>`)

Оптимальний промисловий підхід полягає у виділенні єдиного неперервного блоку пам'яті розміром `N × N` елементів. Переведення двовимірних координат `(i, j)` у лінійний індекс виконується за формулою `index = i * N + j`.

```
[ A[0][0] ... A[0][N-1] | A[1][0] ... A[1][N-1] | ... | A[N-1][0] ... A[N-1][N-1] ]
<------ рядок 0 --------><------ рядок 1 -------->     <------ рядок N-1 ------>
```

Переваги неперервного буфера:
* Лише 1 виділення пам'яті у купі (`malloc` або `std::vector`).
* Ідеальна послідовна адресація: при обході рядка `i` процесор завантажує сусідні елементи у кеш-лінію (Cache Line, 64 байти), прискорюючи виконання обчислень у рази.
* Сумісність із векторизованими процесорними інструкціями SIMD (AVX2, AVX-512, Neon).

Нижче наведено повні реалізації обома мовами з підтримкою зважених ребер та обчисленням найкоротших шляхів для всіх пар вершин за алгоритмом Флойда — Уоршелла.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#define INF INFINITY

/* Структура зваженої матриці суміжності графа */
typedef struct {
    size_t vertices;
    double* data; /* Неперервний масив розміру vertices * vertices */
} AdjMatrix;

/* Створення матриці суміжності */
AdjMatrix* adj_matrix_create(size_t vertices) {
    if (vertices == 0) return NULL;

    AdjMatrix* graph = (AdjMatrix*)malloc(sizeof(AdjMatrix));
    if (!graph) return NULL;

    graph->vertices = vertices;
    graph->data = (double*)malloc(vertices * vertices * sizeof(double));
    if (!graph->data) {
        free(graph);
        return NULL;
    }

    /* Ініціалізація: 0 на діагоналі, INF для відсутніх ребер */
    for (size_t i = 0; i < vertices; ++i) {
        for (size_t j = 0; j < vertices; ++j) {
            if (i == j) {
                graph->data[i * vertices + j] = 0.0;
            } else {
                graph->data[i * vertices + j] = INF;
            }
        }
    }

    return graph;
}

/* Звільнення пам'яті (RAII у стилі C) */
void adj_matrix_free(AdjMatrix* graph) {
    if (graph) {
        free(graph->data);
        free(graph);
    }
}

/* Додавання орієнтованого ребра з вагою */
bool adj_matrix_add_edge(AdjMatrix* graph, size_t u, size_t v, double weight) {
    if (!graph || u >= graph->vertices || v >= graph->vertices) {
        return false;
    }
    graph->data[u * graph->vertices + v] = weight;
    return true;
}

/* Перевірка наявності ребра O(1) */
bool adj_matrix_has_edge(const AdjMatrix* graph, size_t u, size_t v) {
    if (!graph || u >= graph->vertices || v >= graph->vertices) {
        return false;
    }
    double w = graph->data[u * graph->vertices + v];
    return !isnan(w) && w != INF;
}

/* Отримання ваги ребра */
double adj_matrix_get_weight(const AdjMatrix* graph, size_t u, size_t v) {
    if (!graph || u >= graph->vertices || v >= graph->vertices) {
        return INF;
    }
    return graph->data[u * graph->vertices + v];
}

/* Алгоритм Флойда — Уоршелла O(N³) над матрицею "на місці" */
bool adj_matrix_floyd_warshall(AdjMatrix* graph, double* dist_matrix) {
    if (!graph || !dist_matrix) return false;

    size_t n = graph->vertices;

    /* Скопіюємо початковий стан матриці */
    for (size_t i = 0; i < n * n; ++i) {
        dist_matrix[i] = graph->data[i];
    }

    /* Основний трикратний цикл Флойда — Уоршелла */
    for (size_t k = 0; k < n; ++k) {
        for (size_t i = 0; i < n; ++i) {
            for (size_t j = 0; j < n; ++j) {
                double ik = dist_matrix[i * n + k];
                double kj = dist_matrix[k * n + j];

                if (ik != INF && kj != INF) {
                    if (ik + kj < dist_matrix[i * n + j]) {
                        dist_matrix[i * n + j] = ik + kj;
                    }
                }
            }
        }
    }

    /* Перевірка на від'ємні цикли на діагоналі */
    for (size_t i = 0; i < n; ++i) {
        if (dist_matrix[i * n + i] < 0.0) {
            return false; /* Граф містить від'ємний цикл */
        }
    }

    return true;
}

int main(void) {
    size_t n = 4;
    AdjMatrix* g = adj_matrix_create(n);

    adj_matrix_add_edge(g, 0, 1, 5.0);
    adj_matrix_add_edge(g, 0, 3, 10.0);
    adj_matrix_add_edge(g, 1, 2, 3.0);
    adj_matrix_add_edge(g, 2, 3, 1.0);

    printf("Перевірка ребра (0 -> 1): %s\n", 
           adj_matrix_has_edge(g, 0, 1) ? "Є" : "Немає");
    printf("Перевірка ребра (1 -> 3): %s\n", 
           adj_matrix_has_edge(g, 1, 3) ? "Є" : "Немає");

    double* dist = (double*)malloc(n * n * sizeof(double));
    if (adj_matrix_floyd_warshall(g, dist)) {
        printf("Найкоротша відстань від 0 до 3: %.1f (очікується 9.0: 0->1->2->3)\n", 
               dist[0 * n + 3]);
    }

    free(dist);
    adj_matrix_free(g);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <optional>
#include <span>
#include <stdexcept>
#include <limits>
#include <concepts>

/* Оболонковий шаблонний клас для зваженого або бінарного графа */
template <typename T = double>
requires std::is_arithmetic_v<T>
class AdjacencyMatrix {
public:
    static constexpr T Infinity = std::numeric_limits<T>::has_infinity 
                                  ? std::numeric_limits<T>::infinity() 
                                  : std::numeric_limits<T>::max();

    explicit AdjacencyMatrix(std::size_t vertices)
        : m_vertices(vertices), m_matrix(vertices * vertices, Infinity) {
        // Заповнюємо діагональ нулями
        for (std::size_t i = 0; i < m_vertices; ++i) {
            m_matrix[i * m_vertices + i] = T{0};
        }
    }

    [[nodiscard]] std::size_t num_vertices() const noexcept {
        return m_vertices;
    }

    // Додавання орієнтованого ребра
    void add_edge(std::size_t u, std::size_t v, T weight = T{1}) {
        validate_vertex(u);
        validate_vertex(v);
        m_matrix[u * m_vertices + v] = weight;
    }

    // Додавання неорієнтованого ребра (симетричний запис)
    void add_undirected_edge(std::size_t u, std::size_t v, T weight = T{1}) {
        add_edge(u, v, weight);
        add_edge(v, u, weight);
    }

    // Видалення ребра
    void remove_edge(std::size_t u, std::size_t v) {
        validate_vertex(u);
        validate_vertex(v);
        m_matrix[u * m_vertices + v] = (u == v) ? T{0} : Infinity;
    }

    // Перевірка наявності ребра O(1)
    [[nodiscard]] bool has_edge(std::size_t u, std::size_t v) const {
        validate_vertex(u);
        validate_vertex(v);
        return m_matrix[u * m_vertices + v] != Infinity;
    }

    // Отримання ваги через std::optional
    [[nodiscard]] std::optional<T> get_weight(std::size_t u, std::size_t v) const {
        validate_vertex(u);
        validate_vertex(v);
        T w = m_matrix[u * m_vertices + v];
        if (w == Infinity) return std::nullopt;
        return w;
    }

    // Доступ до рядка матриці як std::span для cache-friendly обходу
    [[nodiscard]] std::span<const T> get_row(std::size_t u) const {
        validate_vertex(u);
        return std::span<const T>(&m_matrix[u * m_vertices], m_vertices);
    }

    // Обчислення найкоротших шляхів для всіх пар (Floyd-Warshall)
    [[nodiscard]] std::vector<T> compute_all_pairs_shortest_paths() const {
        std::vector<T> dist = m_matrix; // Копіюємо стан матриці
        const std::size_t n = m_vertices;

        for (std::size_t k = 0; k < n; ++k) {
            for (std::size_t i = 0; i < n; ++i) {
                for (std::size_t j = 0; j < n; ++j) {
                    T ik = dist[i * n + k];
                    T kj = dist[k * n + j];
                    if (ik != Infinity && kj != Infinity) {
                        if (ik + kj < dist[i * n + j]) {
                            dist[i * n + j] = ik + kj;
                        }
                    }
                }
            }
        }
        return dist;
    }

private:
    void validate_vertex(std::size_t v) const {
        if (v >= m_vertices) {
            throw std::out_of_range("Індекс вершини вийшов за межі графа");
        }
    }

    std::size_t m_vertices;
    std::vector<T> m_matrix; // Плоский неперервний буфер у купі
};

int main() {
    try {
        AdjacencyMatrix<double> graph(4);

        graph.add_edge(0, 1, 5.0);
        graph.add_edge(0, 3, 10.0);
        graph.add_edge(1, 2, 3.0);
        graph.add_edge(2, 3, 1.0);

        std::cout << "Ребро (0 -> 1): " << (graph.has_edge(0, 1) ? "Так" : "Ні") << '\n';
        std::cout << "Ребро (3 -> 0): " << (graph.has_edge(3, 0) ? "Так" : "Ні") << '\n';

        auto dist = graph.compute_all_pairs_shortest_paths();
        std::cout << "Найкоротша відстань 0 -> 3: " << dist[0 * 4 + 3] << " (маршрут 0->1->2->3)\n";

        // Обхід вихідних ребер вершини 0 через std::span
        std::cout << "Суміжні сусіди вершини 0:\n";
        auto row0 = graph.get_row(0);
        for (std::size_t v = 0; v < row0.size(); ++v) {
            if (row0[v] != graph.Infinity && v != 0) {
                std::cout << "  -> вершина " << v << " з вагою " << row0[v] << '\n';
            }
        }

    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << '\n';
    }

    return 0;
}
```
:::

## 2. Покроковий розбір реалізації та низькорівневі оптимізації

Розглянемо деталі виконання коду та системні оптимізації, які застосовуються у наведених прикладах.

### 2.1. Управління пам'яттю та RAII

У реалізації C виділення пам'яті вимагає двох перевірок повернення `malloc`. Спочатку виділяється заголовок `AdjMatrix`, потім масив `data`. Якщо друге виділення зазнає невдачі, функція `adj_matrix_create` обов'язково звільняє заголовок, запобігаючи витоку пам'яті. Деструктор `adj_matrix_free` очищує обидва блоки у зворотному порядку.

У реалізації C++ реалізовано концепцію **RAII** (Resource Acquisition Is Initialization). Контейнер `std::vector<T>` автоматично виділяє неперервний буфер у купі при виклику конструктора та самостійно звільняє його під час руйнування об'єкта `AdjacencyMatrix`. Це гарантує виняткову безпеку (Exception Safety) — якщо при виділенні пам'яті станеться `std::bad_alloc`, система не залишить незвільнених ресурсів.

### 2.2. Оптимізація порядку циклів (Loop Nesting Order)

У реалізації алгоритму Флойда — Уоршелла порядок трикратного циклу обрано як `k → i → j`:

```cpp
for (size_t k = 0; k < n; ++k) {
    for (size_t i = 0; i < n; ++i) {
        // Значення ik стабільне протягом усього циклу по j
        T ik = dist[i * n + k];
        for (size_t j = 0; j < n; ++j) {
            T kj = dist[k * n + j];
            if (ik + kj < dist[i * n + j]) {
                dist[i * n + j] = ik + kj;
            }
        }
    }
}
```

У внутрішньому циклі `j` змінні `dist[i * n + j]` та `dist[k * n + j]` ітеруються по сусідніх комірках пам'яті з кроком 1 (stride 1). Це дозволяє процесору завантажувати в кеш-лінію по 8 або 16 елементів типу `double` або `float` за один раз.

Якби ми поміняли місцями цикли `i` та `j` і зробили цикл по `i` найвнутрішнішим, вираз `dist[i * n + j]` ітерувався б із кроком `N` елементів (stride N). При великому `N` кожен крок внутрішнього циклу спричиняв би промах кешу (L1 Cache Miss), уповільнюючи алгоритм у 8–15 разів!

### 2.3. Векторизація SIMD та бітова паралельність

При використанні бітових матриць (`uint64_t*` або `std::vector<bool>`) обчислення логічних операцій над графом стають гранично швидкими завдяки векторам SIMD:

```cpp
// Приклад бітового перетину рядків u та v за допомогою AVX2 інструкцій
void intersect_rows_avx2(const uint64_t* row_u, const uint64_t* row_v, 
                         uint64_t* result, size_t words) {
    size_t i = 0;
    for (; i + 4 <= words; i += 4) {
        // Завантажуємо по 256 бітів (4 слова по 64 біти) у SIMD-регістри
        __m256i a = _mm256_loadu_si256((const __m256i*)&row_u[i]);
        __m256i b = _mm256_loadu_si256((const __m256i*)&row_v[i]);
        __m256i res = _mm256_and_si256(a, b);
        _mm256_storeu_si256((__m256i*)&result[i], res);
    }
    // Хвіст обробляємо звичайним циклом
    for (; i < words; ++i) {
        result[i] = row_u[i] & row_v[i];
    }
}
```

Використання інструкцій AVX2 дозволяє обробляти по 256 ребер (256 булевих значень суміжності) за один системний такт процесора, досягаючи гігабітних швидкостей аналізу графів.

### 2.4. Використання сучасних C++20 Abstractions

* `std::span<const T>` у методі `get_row(u)` повертає безнаслідний перегляд неперервного рядка матриці. Це надає зручний інтерфейс масиву без створення додаткових копій векторів у купі.
* `std::optional<T>` у методі `get_weight(u, v)` робить код чітким та виразним. Розробник, який викликає цей метод, змушений обробити випадок `std::nullopt` (відсутність ребра), що запобігає випадковому використанню магічних чисел чи невизначеної поведінки.
* Концепт `requires std::is_arithmetic_v<T>` гарантує на етапі компіляції, що матриця створюється лише для числових типів (`int`, `float`, `double`, `uint64_t`), запобігаючи помилкам компіляції глибоко всередині шаблонного коду.

### 2.5. Профілювання та динамічне розширення

Для матриці суміжності операція додавання нової вершини `add_vertex()` вимагає створення нового плоского масиву розміром `(N + 1)²`, копіювання `N²` елементів зі старого масиву та видалення старого буфера. Це операція складності `O(N²)`.

Тому при проектуванні високонавантажених систем розмір матриці суміжності зазвичай виділяють із запасом (наприклад, верхня межа можливих вершин `N_max`), або застосовують її виключно у статичних графах з фіксованою конфігурацією топології.
