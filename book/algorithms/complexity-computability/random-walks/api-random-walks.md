# 📋 Специфікація інтерфейсу випадкових блукань та стохастичного аналізу

Ця специфікація описує програмний інтерфейс (API) системної бібліотеки `GraphWalkEngine`, призначеної для виконання випадкових блукань, спектрального аналізу графів, побудови рівномірних кістякових дерев та обчислення метрик зв'язності. Бібліотека надає C-сумісний ABI високої продуктивності для інтеграції у системне програмне забезпечення, високопродуктивні обчислювальні модулі та низькорівневі сервіси, а також ідіоматичні обгортки для мови C++ з використанням стандартних контейнерів, шаблонів та принципу RAII.

Головною метою архітектури `GraphWalkEngine` є забезпечення максимальної продуктивності обчислень при мінімальному споживанні пам'яті. Бібліотека розроблена таким чином, щоб дозволяти виконання алгоритмів на графах великої розмірності без необхідності створення повних дублікатів структур даних у пам'яті. Використання компактного формату CSR (Compressed Sparse Row) забезпечує ефективне використання кеш-пам'яті процесора та оптимальну локальність даних під час генерації послідовних кроків випадкового блукача.

---

## 1. Типи даних та структури конфігурації

### 1.1 Коди повернення та помилки (`WalkStatus`)

Система обробки помилок у `GraphWalkEngine` базується на поверненні від'ємних цілочисельних кодів статусів у мові C та строго типізованих переліків у мові C++. Кожна функція бібліотеки повертає значення типу `WalkStatus`, що дозволяє розробнику точно визначати причину виникнення збоїв або відхилень від нормального перебігу обчислень.

:::tabs
```c
typedef enum {
    WALK_SUCCESS              =  0,  // Операцію виконано успішно
    WALK_ERR_INVALID_ARG      = -1,  // Некоректний аргумент (NULL вказівник, вихід за межі)
    WALK_ERR_DISCONNECTED     = -2,  // Граф є незв'язним (цільова вершина недосяжна)
    WALK_ERR_PERIODIC         = -3,  // Граф є дводольним/періодичним без використання lazy walk
    WALK_ERR_DAMPING_RANGE    = -4,  // Коефіцієнт демпфування alpha виходить за межі (0, 1)
    WALK_ERR_NO_MEMORY        = -5,  // Недостатньо оперативної пам'яті
    WALK_ERR_MAX_STEPS        = -6   // Перевищено ліміт кроків без досягнення збіжності
} WalkStatus;
```
```cpp
#include <cstdint>

enum class WalkStatus : int32_t {
    Success             =  0,  // Операцію виконано успішно
    ErrInvalidArg       = -1,  // Некоректний аргумент
    ErrDisconnected     = -2,  // Граф незв'язний
    ErrPeriodic         = -3,  // Граф дводольний
    ErrDampingRange     = -4,  // Некоректний alpha
    ErrNoMemory         = -5,  // Брак пам'яті
    ErrMaxSteps         = -6   // Перевищено кроки
};
```
:::

Значення `WALK_SUCCESS` гарантує, що результуючі вказівники містять коректно обчислені дані. У разі повернення будь-якого від'ємного коду вихідні аргументи залишаються у незмінному стані або скидаються до безпечних типових значень.

---

### 1.2 Конструкції опису графа (`GraphSpec`)

Для забезпечення максимальної швидкості зчитування списків сусідніх вершин граф у пам'яті представляється через структуру `GraphSpec`, яка загортає стиснутий формат списків суміжності CSR. Масив `row_ptr` містить зсуви початків рядків, а масив `col_idx` містить номери суміжних вершин.

:::tabs
```c
typedef struct {
    uint32_t num_vertices;    // Кількість вершин у графі (n)
    uint64_t num_edges;       // Кількість ребер у графі (m)
    bool is_directed;         // Прапорець орієнтованості (true - орієнтований, false - неорієнтований)
    const uint32_t* row_ptr;  // Масив зсувів у форматі CSR (Compressed Sparse Row) розміру n + 1
    const uint32_t* col_idx;  // Масив суміжних вершин у форматі CSR розміру 2m (або m)
    const double* weights;    // Масив ваг ребер (NULL для невиваженого графа)
} GraphSpec;
```
```cpp
#include <cstdint>
#include <span>
#include <optional>

struct GraphSpec {
    uint32_t num_vertices{0};
    uint64_t num_edges{0};
    bool is_directed{false};
    std::span<const uint32_t> row_ptr{};
    std::span<const uint32_t> col_idx{};
    std::optional<std::span<const double>> weights{std::nullopt};
};
```
:::

Використання беззнакових 32-бітних цілих чисел дозволяє представляти графи розміром до 4 мільярдів вершин, а 64-бітний лічильник `num_edges` знімає обмеження на кількість ребер для надвеликих мереж.

---

### 1.3 Конфігурація випадкового блукання (`WalkConfig`)

Структура `WalkConfig` акумулює всі керівні параметри стохастичного процесу: тривалість блукання, коефіцієнт телепортації, режим ледачих переходів та вихідний стан генератора псевдовипадкових чисел.

:::tabs
```c
typedef struct {
    uint64_t max_steps;       // Максимальна кількість кроків у блуканні
    double alpha_damping;     // Коефіцієнт демпфування PageRank (типово 0.85)
    bool is_lazy;             // Прапорець ледачого блукання (P_lazy = 0.5 I + 0.5 P)
    uint32_t random_seed;     // Зерно ініціалізації генератора псевдовипадкових чисел
} WalkConfig;
```
```cpp
#include <cstdint>

struct WalkConfig {
    uint64_t max_steps{1000000ULL};
    double alpha_damping{0.85};
    bool is_lazy{true};
    uint32_t random_seed{42};
};
```
:::

Параметр `is_lazy` включає додавання петльових переходів із ймовірністю `1/2`, що є обов'язковим при виконанні аналізу на дводольних графах для запобігання нескінченним осциляціям векторів ймовірностей.

---

### 1.4 Результати спектрального аналізу (`SpectralInfo`)

Структура `SpectralInfo` призначена для збереження спектральних характеристик матриці переходів `P`, обчислених за допомогою алгоритмів Ланцоша або ітерацій Арнольді.

:::tabs
```c
typedef struct {
    double lambda_2;          // Друге за величиною власне значення (lambda_2)
    double spectral_gap;      // Спектральний зазор gamma = 1 - lambda_2
    double cheeger_lower;     // Нижня межа кондуктансу (gamma / 2)
    double cheeger_upper;     // Верхня межа кондуктансу (sqrt(2 * gamma))
    uint64_t est_mixing_time; // Оцінка часу перемішування t_mix(0.01)
} SpectralInfo;
```
```cpp
#include <cstdint>

struct SpectralInfo {
    double lambda_2{0.0};
    double spectral_gap{0.0};
    double cheeger_lower{0.0};
    double cheeger_upper{0.0};
    uint64_t est_mixing_time{0};
};
```
:::

Значення `spectral_gap` надає розробнику можливість оцінити швидкість збіжності алгоритмів Монте-Карло ще до початку масового випуску блукачів.

---

## 2. Сигнатури функцій та контракти викликів

### 2.1 Ініціалізація та знищення графа

Функція `graph_spec_create` виконує виділення динамічної пам'яті під об'єкт `GraphSpec` і перевіряє коректність розмірностей.

:::tabs
```c
WalkStatus graph_spec_create(uint32_t n, bool is_directed, GraphSpec** out_graph);
void graph_spec_free(GraphSpec* graph);
```
```cpp
#include <memory>
#include <expected>

class GraphSpecWrapper {
public:
    static std::expected<GraphSpecWrapper, WalkStatus> create(uint32_t n, bool is_directed);
    ~GraphSpecWrapper(); // Автоматичний RAII виклик free
};
```
:::

Усі виділені ресурси мають бути звільнені парним викликом `graph_spec_free` для усунення витоків оперативної пам'яті.

---

### 2.2 Генерація одиничного кроку блукача

Функція `graph_walk_step` реалізує найатомарнішу операцію бібліотеки — обчислення одного переходу випадкового блукача з поточної вершини `current_vertex`.

:::tabs
```c
WalkStatus graph_walk_step(
    const GraphSpec* graph,
    uint32_t current_vertex,
    bool is_lazy,
    uint64_t* seed_state,
    uint32_t* out_next
);
```
```cpp
#include <expected>
#include <cstdint>

std::expected<uint32_t, WalkStatus> graph_walk_step(
    const GraphSpec& graph,
    uint32_t current_vertex,
    bool is_lazy,
    uint64_t& seed_state
) noexcept;
```
:::

Ця функція оптимізована для виконання всередині гарячих циклів і не виконує внутрішніх виділень пам'яті у купі (heap).

---

### 2.3 Перевірка s-t зв'язності (Aleliunas Algorithm)

Функція `graph_walk_check_st_connectivity` реалізує алгоритм Алелюнаса перевірки досяжності вершини `t` з вершини `s` у неорієнтованому графі за допомогою випадкового блукання.

:::tabs
```c
WalkStatus graph_walk_check_st_connectivity(
    const GraphSpec* graph,
    uint32_t s,
    uint32_t t,
    uint32_t num_trials,
    bool* out_connected
);
```
```cpp
#include <expected>
#include <cstdint>

std::expected<bool, WalkStatus> check_st_connectivity(
    const GraphSpec& graph,
    uint32_t s,
    uint32_t t,
    uint32_t num_trials = 5
);
```
:::

Алгоритм виконує блукання тривалістю `2m · n` кроків. Якщо за `num_trials` незалежних запусків вершина `t` жодного разу не була відвідана, параметр `out_connected` приймає значення `false`.

---

### 2.4 Обчислення PageRank

Функція `graph_walk_compute_pagerank` реалізує оцінку стаціонарного розподілу PageRank методом Монте-Карло за допомогою симуляції ансамблю незалежних блукачів.

:::tabs
```c
WalkStatus graph_walk_compute_pagerank(
    const GraphSpec* graph,
    const WalkConfig* config,
    uint64_t num_walks,
    double* out_pagerank
);
```
```cpp
#include <vector>
#include <expected>

std::expected<std::vector<double>, WalkStatus> compute_pagerank(
    const GraphSpec& graph,
    const WalkConfig& config,
    uint64_t num_walks
);
```
:::

Вихідний масив `out_pagerank` отримує нормований вектор весов, сума елементів якого дорівнює 1.

---

### 2.5 Генерація кістякового дерева (Wilson's Algorithm)

Функція `graph_walk_generate_ust_wilson` будує рівномірно випадкове кістякове дерево (Uniform Spanning Tree, UST) за допомогою блукання з вилученням циклів (LERW).

:::tabs
```c
WalkStatus graph_walk_generate_ust_wilson(
    const GraphSpec* graph,
    uint32_t seed,
    uint32_t* out_edges_u,
    uint32_t* out_edges_v
);
```
```cpp
#include <vector>
#include <utility>
#include <expected>

using EdgePair = std::pair<uint32_t, uint32_t>;

std::expected<std::vector<EdgePair>, WalkStatus> generate_ust_wilson(
    const GraphSpec& graph,
    uint32_t seed
);
```
:::

Якщо граф не є зв'язним, функція перериває виконання та повертає код `WALK_ERR_DISCONNECTED`.

---

### 2.6 Обчислення ефективного опору та часів комутації

Функція `graph_walk_effective_resistance` розраховує ефективний опір `R_eff(u, v)` та час комутації `C(u, v) = 2m · R_eff(u, v)` між двома вузлами графа.

:::tabs
```c
WalkStatus graph_walk_effective_resistance(
    const GraphSpec* graph,
    uint32_t u,
    uint32_t v,
    double* out_r_eff,
    double* out_commute_time
);
```
```cpp
#include <expected>

struct ResistanceResult {
    double r_eff{0.0};
    double commute_time{0.0};
};

std::expected<ResistanceResult, WalkStatus> calculate_effective_resistance(
    const GraphSpec& graph,
    uint32_t u,
    uint32_t v
);
```
:::

Обчислення виконується за допомогою ітеративних методів розв'язання системи лінійних рівнянь з матрицею Лапласа графа.

---

## 3. C++ Обгортка високого рівня (`GraphWalkEngine.hpp`)

Для мови C++ надається об'єктно-орієнтована обгортка з підтримкою концептів, RAII та смарт-вказівників:

:::tabs
```c
// Низькорівневий розширювач для C
typedef struct GraphWalkEngineC GraphWalkEngineC;
GraphWalkEngineC* engine_c_create(const GraphSpec* spec);
void engine_c_destroy(GraphWalkEngineC* engine);
```
```cpp
namespace graph_walk {

class GraphWalkEngine {
public:
    explicit GraphWalkEngine(GraphSpec spec);
    ~GraphWalkEngine();

    // Заборона копіювання, дозволено переміщення
    GraphWalkEngine(const GraphWalkEngine&) = delete;
    GraphWalkEngine& operator=(const GraphWalkEngine&) = delete;
    GraphWalkEngine(GraphWalkEngine&&) noexcept;
    GraphWalkEngine& operator=(GraphWalkEngine&&) noexcept;

    // Метод s-t зв'язності
    [[nodiscard]] bool is_connected(size_t s, size_t t, uint32_t trials = 5) const;

    // Обчислення PageRank
    [[nodiscard]] std::vector<double> pagerank(const WalkConfig& config, uint64_t num_walks) const;

    // Генерація UST
    [[nodiscard]] std::vector<std::pair<uint32_t, uint32_t>> generate_ust(uint32_t seed) const;

    // Спектральні характеристики
    [[nodiscard]] SpectralInfo analyze_spectrum() const;

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace graph_walk
```
:::

Використання ідіоми pImpl (Pointer to Implementation) приховує низькорівневі C-структури та забезпечує повну бінарну сумісність (ABI stability) при оновленні версій бібліотеки.

---

## 4. Складність та ресурсні вимоги

Нижче наведено підсумкову таблицю часової та просторової складності функцій бібліотеки:

| Алгоритмічна функція | Часова складність (Time) | Просторова складність (Space) | Клас пам'яті | Гарантія завершення |
| :--- | :--- | :--- | :--- | :--- |
| `graph_walk_step` | `O(1)` | `O(1)` | Робочі регістри | Строга |
| `check_st_connectivity` | `O(m · n)` | `O(log n)` біт | Логарифмічна | Імовірнісна (≥ 1 - 2⁻ᵏ) |
| `compute_pagerank` | `O(N · L)` | `O(n)` біт | Поліноміальна | Строга |
| `generate_ust_wilson` | `O(m · R_eff)` | `O(n)` біт | Поліноміальна | Точна рівномірна |
| `effective_resistance` | `O(n³)` або `O(m log² n)` | `O(n + m)` біт | Поліноміальна | Точна алгебраїчна |

---

## 5. Граничні умови та обробка виняткових ситуацій

Під час роботи з бібліотекою `GraphWalkEngine` розробнику необхідно враховувати наступні крайові випадки та особливості поведінки алгоритмів:

1. **Ізольовані вершини (`degree(v) = 0`):**
   Виклик `graph_walk_step` для ізольованої вершини повертає код `WALK_ERR_INVALID_ARG`. Для PageRank ізольовані вершини вважаються тупиками, і блукач автоматично виконує телепортацію.

2. **Періодичні / Дводольні графи:**
   При виконанні спектрального аналізу на дводольному графі без прапорця `is_lazy` функція `analyze_spectrum` повертає `WALK_ERR_PERIODIC`, оскільки `lambda_n = -1` унеможливлює оцінку часу перемішування.

3. **Незв'язний граф у `generate_ust_wilson`:**
   Якщо граф має більше ніж одну компоненту зв'язності, алгоритм Уїлсона не здатний покрити всі вершини й потрапляє у нескінченний цикл. Перед запуском функція перевіряє зв'язність і повертає `WALK_ERR_DISCONNECTED`.
