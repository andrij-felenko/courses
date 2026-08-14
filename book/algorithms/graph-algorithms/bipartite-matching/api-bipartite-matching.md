# 📋 Інтерфейс та довбня: довідник API дводольного паросполучення

Програмний модуль дводольного паросполучення забезпечує низькорівневий C/C++ контракт для системного програмування, підтримку промислових форматів даних та порівняльну специфікацію обчислювальних алгоритмів. Інтерфейс охоплює базові класи розв'язувачів для неуважених і зважених графів, а також розширений API для динамічного оновлення ребер у системних програмах реального часу.

### Системне призначення та архітектура модуля

Програмний модуль дводольного паросполучення призначений для вбудовування у високопродуктивні обчислювальні системи, такі як планувальники задач у розподілених операційних системах, модулі зіставлення ключових точок у комп'ютерному зорі, а також комутаційні матриці високошвидкісних мережевих маршрутизаторів. 

Головна архітектурна вимога до модуля — мінімізація накладних витрат на динамічне виділення пам'яті під час виконання обчислень. Для досягнення цієї мети реалізація відокремлює фазу ініціалізації структури графа (де виділяються основні масиви суміжності та станів) від фази безпосереднього розв'язання задачі. Завдяки цьому повторний виклик розв'язувача на тому самому екземплярі графа зі зміненою топологією не спричиняє системних викликів `malloc` або `free`, що гарантує детермінований час відгуку у системах реального часу.

Програмний модуль гарантує повну побітову відтворюваність результатів при однакових вхідних даних, а також забезпечує потокобезпечність (Thread Safety) на рівні константних читальних операцій після завершення фази побудови графа.

---

### 1. Програмний контракт C / C++ API

#### Специфікація типів даних, структур та сигнатур

Для забезпечення сумісності з низькорівневим системним кодом мовою C та ідіоматичними конструкціями C++20, контракт надає еквівалентні типи даних, переліки статусів виконання та алгоритмічних стратегій. Код статусу `BIPARTITE_SUCCESS` гарантує, що обчислення завершено повністю, а масиви паросполучення містять валідні індекси вершин.

Перелік статусів виконання `BipartiteStatus` визначає правила обробки виняткових ситуацій. Якщо функція отримує від'ємний індекс вершини або індекс, що перевищує задекларований розмір частки, повертається `BIPARTITE_ERR_INVALID_INDEX`. Передача нульових вказівників повертає `BIPARTITE_ERR_NULL_POINTER`.

:::tabs
```c
/* C API: Повертані коди помилок та статусів виконання */
typedef enum {
    BIPARTITE_SUCCESS          =  0,  /* Успішне обчислення */
    BIPARTITE_ERR_NULL_POINTER = -1,  /* Передано нульовий вказівник */
    BIPARTITE_ERR_INVALID_INDEX= -2,  /* Індекс вершини вийшов за межі [0, N-1] або [0, M-1] */
    BIPARTITE_ERR_OUT_OF_MEMORY= -3,  /* Не вдалося виділити пам'ять */
    BIPARTITE_ERR_INVALID_GRAPH= -4   /* Граф містить некоректні ребра або порушено дводольність */
} BipartiteStatus;

/* Конфігурація розв'язувача */
typedef enum {
    ALGORITHM_KUHN          = 0,  /* Простий DFS, O(V * E), оптимальний для малих і розріджених графів */
    ALGORITHM_HOPCROFT_KARP = 1,  /* Фазовий BFS+DFS, O(E * sqrt(V)), для великих графів */
    ALGORITHM_DINIC_FLOW    = 2   /* Зведення до потоку через алгоритм Дініца, O(E * sqrt(V)) */
} BipartiteAlgorithm;

/* Структура результату обчислення у C */
typedef struct {
    int matching_size;        /* Кількість ребер у максимальному паросполученні */
    int* match_u;             /* Масив розміром u_size: match_u[u] = v або -1 */
    int* match_v;             /* Масив розміром v_size: match_v[v] = u або -1 */
    int* vertex_cover_u;      /* Прапорець 0/1: чи належить u_i до мінімального покриття */
    int* vertex_cover_v;      /* Прапорець 0/1: чи належить v_j до мінімального покриття */
    double execution_time_ms; /* Час виконання у мілісекундах */
} MatchingResult;

/* Сигнатури функцій C API */
BipartiteStatus bipartite_graph_create(int u_size, int v_size, int initial_capacity, void** graph_handle);
void bipartite_graph_destroy(void* graph_handle);
BipartiteStatus bipartite_graph_add_edge(void* graph_handle, int u, int v);
BipartiteStatus bipartite_solve_matching(void* graph_handle, BipartiteAlgorithm algo, MatchingResult* result);
void bipartite_result_free(MatchingResult* result);
```
```cpp
// C++20 API: Переліки та структури результату
namespace graph::matching {

enum class Status {
    Success = 0,
    NullPointer = -1,
    InvalidIndex = -2,
    OutOfMemory = -3,
    InvalidGraph = -4
};

enum class Algorithm {
    Kuhn = 0,
    HopcroftKarp = 1,
    Dinic = 2
};

struct MatchingSolution {
    std::size_t matching_size{0};
    std::vector<int> match_u; // match_u[u] = v або -1
    std::vector<int> match_v; // match_v[v] = u або -1
    std::vector<bool> min_vertex_cover_u;
    std::vector<bool> min_vertex_cover_v;
    double execution_time_ms{0.0};
};

class BipartiteMatchingSolver {
public:
    explicit BipartiteMatchingSolver(std::size_t u_size, std::size_t v_size);
    ~BipartiteMatchingSolver() noexcept = default;

    BipartiteMatchingSolver(const BipartiteMatchingSolver&) = delete;
    BipartiteMatchingSolver& operator=(const BipartiteMatchingSolver&) = delete;
    BipartiteMatchingSolver(BipartiteMatchingSolver&&) noexcept = default;
    BipartiteMatchingSolver& operator=(BipartiteMatchingSolver&&) noexcept = default;

    void add_edge(std::size_t u, std::size_t v);
    void clear_edges() noexcept;
    [[nodiscard]] MatchingSolution solve(Algorithm algo = Algorithm::HopcroftKarp) const;

    [[nodiscard]] std::size_t u_size() const noexcept;
    [[nodiscard]] std::size_t v_size() const noexcept;
    [[nodiscard]] std::size_t edge_count() const noexcept;

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace graph::matching
```
:::

#### Управління ресурсами та володіння пам'яттю

У C API пам'ять для структури графа виділяється функцією `bipartite_graph_create` і повинна обов'язково вилучатися функцією `bipartite_graph_destroy`. При обчисленні паросполучення функція `bipartite_solve_matching` виділяє внутрішні масиви `match_u`, `match_v`, `vertex_cover_u` та `vertex_cover_v` всередині структури `MatchingResult`. Користувач зобов'язаний передати цю структуру у `bipartite_result_free` після завершення роботи для запобігання витокам пам'яті.

У C++20 API керування пам'яттю автоматизоване через паттерн RAII та стандартні контейнери `std::vector`. Клас `BipartiteMatchingSolver` забороняє копіювання (конструктор копіювання й оператор присвоєння позначені як `= delete`), але підтримує семантику переміщення (Move Semantics), що дозволяє передавати екземпляри розв'язувача між потоками виконання без накладних витрат.

---

### 2. Специфікація вхідних форматів даних

Для обміну даними між обчислювальними модулями та збереження графів на диску підтримуються три основні формати. Кожен формат розрахований на свій варіант використання: текстові списки ребер зручні для швидкого налагодження, формат DIMACS є стандартом наукових змагань з комбінаторної оптимізації, а JSON використовується у REST API веб-сервісів.

#### Формат 1: Список ребер (Edge List Text Format)

Простий текстовий формат для зберігання дводольних графів у файлах з розширенням `.bde`. Перший рядок, який не є коментарем, містить розміри часток та кількість ребер. Далі йдуть пари індексів вершин.

```text
# Коментарі починаються з символу '#'
# Рядок 1: <U_SIZE> <V_SIZE> <NUM_EDGES>
4 4 7
# Наступні рядки: <U_INDEX> <V_INDEX>
0 0
0 1
1 1
1 2
2 0
2 3
3 2
```

Текстовий парсер обробляє файл послідовно. Усі рядки, що починаються з символу `#`, ігноруються. Індексація вершин є 0-базованою (вершини частки `U` належать діапазону `[0, U_SIZE - 1]`, а вершини частки `V` — діапазону `[0, V_SIZE - 1]`).

#### Формат 2: Формат DIMACS Bipartite Variant (`.bgf`)

Розширення стандартного царинного формату DIMACS, який широко застосовується у наукових дослідженнях та змаганнях з комбінаторної оптимізації. Індексація вершин у цьому форматі є традиційно 1-базованою (починається з 1, а не з 0). Інтерпретатор мапить ці індекси на внутрішні масиви автоматично, зменшуючи кожен індекс на одиницю при зчитуванні.

```text
c Формат DIMACS для дводольних графів
c p bipartite <U_NODES> <V_NODES> <EDGES>
p bipartite 4 4 7
e 1 1
e 1 2
e 2 2
e 2 3
e 3 1
e 3 4
e 4 3
```

Символ `c` позначає коментар. Рядок заголовка `p bipartite` оголошує розміри часток та кількість ребер. Рядки, що починаються з `e`, задають окремі ребра графа між лівою та правою часткою.

#### Формат 3: JSON контракт API для веб-сервісів

При передачі даних у мікросервісних архітектурах граф серіалізується у JSON об'єкт. Структура запиту містить чітко визначені поля розмірів часток `u_nodes` та `v_nodes`, масив об'єктів ребер, а також блок опцій для вибору конкретного алгоритму.

```json
{
  "graph": {
    "u_nodes": 4,
    "v_nodes": 4,
    "edges": [
      {"u": 0, "v": 0},
      {"u": 0, "v": 1},
      {"u": 1, "v": 1},
      {"u": 1, "v": 2},
      {"u": 2, "v": 0},
      {"u": 3, "v": 3}
    ]
  },
  "options": {
    "algorithm": "hopcroft_karp",
    "compute_vertex_cover": true
  }
}
```

Відповідь сервісу містить статусне поле, загальну кількість ребер у знайденому паросполученні, список конкретних пар вершин, а також опціональний блок мінімального вершинного покриття, розрахований за теоремою Кеніга.

```json
{
  "status": "success",
  "result": {
    "matching_size": 4,
    "pairs": [
      {"u": 0, "v": 1},
      {"u": 1, "v": 2},
      {"u": 2, "v": 0},
      {"u": 3, "v": 3}
    ],
    "vertex_cover": {
      "u_nodes": [0, 1, 3],
      "v_nodes": [0]
    },
    "execution_time_ms": 0.042
  }
}
```

---

### 3. Довідкова таблиця порівняння складності алгоритмів

Нижче наведено порівняльну характеристику алгоритмів пошуку паросполучення за часовою та просторовою складністю, а також сферами їх застосування. При виборі алгоритму слід керуватися ще й густиною ребер у графі: для дуже розріджених графів алгоритм Куна показує відмінні результати завдяки мінімальній константі у часовій складності, тоді як для щільних графів алгоритм Хопкрофта–Карпа є беззаперечним лідером.

| Алгоритм | Часова складність (найгірший випадок) | Часова складність (розріджений граф) | Просторова складність | Тип графа | Основні переваги та сфери застосування |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Куна (Kuhn DFS)** | `O(V * E)` | `O(V * E)` | `O(V + E)` | Неуважений дводольний | Проста реалізація (до 30 рядків коду), малі накладні витрати на малих графах (`|V| < 1000`). |
| **Хопкрофта–Карпа (Hopcroft–Karp)** | `O(E * sqrt(V))` | `O(E * sqrt(V))` | `O(V + E)` | Неуважений дводольний | Промисловий стандарт для неуважених графів. Фазовий BFS+DFS забезпечує мінімальний час на великих даних. |
| **Потік Дініца (Dinic Flow)** | `O(E * sqrt(V))` | `O(E * sqrt(V))` | `O(V + E)` | Неуважений дводольний | Універсальність: легко додаються обмеження на пропускні здатності та розширюється до мульти-джерел. |
| **Угорський (Kuhn–Munkres)** | `O(V^3)` | `O(V^3)` або `O(V^2 log V + V E)` | `O(V^2)` | Зважений дводольний | Пошук максимального паросполучення **мінімальної/максимальної ваги**. Повна матриця ваг. |
| **Min-Cost Max-Flow (MCMF)** | `O(V * E^2)` | `O(E^2 log V)` | `O(V + E)` | Зважений дводольний | Оптимізація потоку з цінами. Гнучке налаштування обмежень на потужність каналів. |
| **Едмондса (Blossom Algorithm)** | `O(V^4)` або `O(E * sqrt(V))` | `O(E * sqrt(V))` | `O(V + E)` | **Довільний (недводольний)** | Розв'язує задачу для довільних графів за допомогою стиснення непарних циклів (суцвіть). |

---

### 4. Динамічний API для оновлення ребер у реальному часі

У системних програмах (наприклад, у планувальниках задач ОС чи мережевих комутаторах) граф постійно змінюється: ребра додаються або видаляються у процесі роботи. Перераховувати паросполучення з нуля за допомогою алгоритму Хопкрофта–Карпа `O(E * sqrt(V))` на кожну подію занадто дорого. 

Динамічний API дозволяє оновлювати паросполучення інкрементно. При додаванні нового ребра розв'язувач виконує один прохід пошуку доповнюючого шляху від нової реберної пари за `O(V + E)`. При видаленні ребра, яке входило до поточного паросполучення, алгоритм шукає локальний заміщаючий шлях лише для вивільненої вершини, не чіпаючи решту графа.

:::tabs
```c
/* C API: Динамічне оновлення графа */
typedef struct DynamicMatchingState DynamicMatchingState;

DynamicMatchingState* dynamic_matching_create(int u_size, int v_size);
void dynamic_matching_destroy(DynamicMatchingState* state);

/* Додавання ребра з підтриманням поточного паросполучення за O(V + E) */
bool dynamic_matching_insert_edge(DynamicMatchingState* state, int u, int v);

/* Видалення ребра */
bool dynamic_matching_remove_edge(DynamicMatchingState* state, int u, int v);

int dynamic_matching_get_size(const DynamicMatchingState* state);
```
```cpp
// C++20 API: Динамічне оновлення графа
namespace graph::matching {

class DynamicBipartiteMatching {
public:
    DynamicBipartiteMatching(std::size_t u_size, std::size_t v_size);
    ~DynamicBipartiteMatching() noexcept = default;

    // Інкрементне додавання ребра (u, v)
    // Якщо паросполучення можна збільшити за 1 прохід DFS, воно збільшується за O(V + E)
    bool insert_edge(std::size_t u, std::size_t v);

    // Видалення ребра (u, v)
    // Якщо ребро належало паросполученню, шукається локальний заміщаючий шлях
    bool remove_edge(std::size_t u, std::size_t v);

    // Отримання поточного розміру паросполучення за O(1)
    [[nodiscard]] std::size_t matching_size() const noexcept;

    // Перевірка: чи покрита вершина u у поточній конфігурації
    [[nodiscard]] bool is_u_matched(std::size_t u) const;
    [[nodiscard]] bool is_v_matched(std::size_t v) const;
};

} // namespace graph::matching
```
:::

---

### 5. Інтерфейс розширення для зважених графів (Hungarian Algorithm)

Для задач, де кожне ребро `e = (u, v)` має ваговий коефіцієнт (наприклад, затримка передачі пакета або вартість виконання завдання робітником), використовується зважений розв'язувач. Шаблонний клас `HungarianSolver` підтримує як цілочисельні ваги `int64_t`, так і числа з плаваючою комою `double`.

Метод Угорського алгоритму працює над повними матрицями ваг `N x M`. Якщо між вершинами `u` та `v` ребро відсутнє, у матриці ваг задається нескінченно мале або нескінченно велике значення ( залежно від того, шукається максимум чи мінімум).

:::tabs
```c
/* C API для Угорського алгоритму зваженого паросполучення */
typedef struct {
    int u;
    int v;
    double weight;
} CWeightedEdge;

typedef struct {
    double total_weight;
    int count;
    CWeightedEdge* edges;
} CWeightedMatchingSolution;

CWeightedMatchingSolution* hungarian_solve_max(const double* weight_matrix, int n, int m);
void hungarian_solution_free(CWeightedMatchingSolution* sol);
```
```cpp
// C++20 API для Угорського алгоритму
namespace graph::matching {

template <typename WeightType = double>
struct WeightedEdge {
    std::size_t u;
    std::size_t v;
    WeightType weight;
};

template <typename WeightType = double>
struct WeightedMatchingSolution {
    WeightType total_weight{0};
    std::vector<WeightedEdge<WeightType>> matched_edges;
};

template <typename WeightType = double>
class HungarianSolver {
public:
    explicit HungarianSolver(const std::vector<std::vector<WeightType>>& weight_matrix);

    [[nodiscard]] WeightedMatchingSolution<WeightType> solve_max_weight();
    [[nodiscard]] WeightedMatchingSolution<WeightType> solve_min_weight();
};

} // namespace graph::matching
```
:::

---

### 6. Словник прапорців CLI та налаштувань конфігурації

При використанні консольних утиліт аналізу графів (наприклад, `bipartite-cli`) застосовуються такі параметри командного рядка:

- `--algo=kuhn|hopcroft|dinic` — вибір алгоритму обчислення. За замовчуванням використовується `hopcroft`.
- `--format=edgelist|dimacs|json` — формат вхідного файлу даних.
- `--input=<path>` — обов'язковий параметр, шлях до вхідного файлу графа.
- `--output=<path>` — шлях для збереження результатів у форматі JSON або CSV.
- `--compute-cover` — увімкнути обчислення мінімального вершинного покриття відповідно до теореми Кеніга.
- `--quiet` — режим мінімального виводу (друкує лише чисельне значення розміру паросполучення для використання у баш-скриптах).
- `--benchmark` — виконати серію з 100 запусків для вимірювання середнього часу виконання та споживання оперативної пам'яті.
