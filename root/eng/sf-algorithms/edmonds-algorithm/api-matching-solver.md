# 📋 Специфікація інтерфейсу розв'язувача паросполучень

Цей документ дає вичерпний структурний довідник (API contract) для інтеграції розв'язувача задач найбільшого та зваженого паросполучення в системні модулі мовами C та C++.

## Системне призначення та контракти використання

Розв'язувач паросполучень (англ. *matching solver*) є автономним обчислювальним компонентом, призначеним для обчислення максимального за потужністю (англ. *maximum cardinality*) або максимального за вагою (англ. *maximum weight*) паросполучення у довільних неорієнтованих графах. Інтерфейс розроблений для застосування у системному програмуванні, високопродуктивних розв'язувачах оптимізаційних задач, геометричному алгоритмічному забезпеченні та логістичних модулях.

Компонент гарантує виконання чотирьох системних контрактів:
1. **Коректність комбінаторного результату:** Знайдене паросполучення задовольняє всі фундаментальні комбінаторні інваріанти. Жодна вершина графа не інцидентна більше ніж одному ребру з обраної підмножини. Сумарна вага або кількість обраних ребер є строго максимальною для даної топології графа.
2. **Детермінізм та відтворюваність обчислень:** Для одного й того самого вхідного графа та збереженого порядку додавання ребер розв'язувач повертає абсолютно ідентичний результат незалежно від архітектури процесора або версії компілятора.
3. **Строга безпека пам'яті та відсутність витоків:** Усі виділення пам'яті здійснюються через явні контексти управління ресурсами. Відсутні витоки пам'яті, невизначена поведінка чи звернення поза межами масивів при будь-яких валідних або некоректних вхідних даних.
4. **Ізоляція стану та відсутність побічних ефектів:** Розв'язувач не використовує прихованих глобальних змінних чи стани, що змінюються у фоновому режимі, що робить його придатним для роботи у багатопотокових середовищах із розділеними контекстами.

## Специфікація інтерфейсу мови C та C++ (C & C++ API Contracts)

C-інтерфейс розроблений за класичним шаблоном непрозорого вказівника (англ. *opaque handle pattern*), що гарантує бінарну сумісність (ABI). C++-інтерфейс пропонує ідіоматичний обгортковий клас `MatchingSolver` із семантикою RAII та безпекою винятків.

### 1. Переліки, типи даних та коди повернення

Переліки встановлюють можливі режими обчислень, коди помилок та інтерфейси користувацьких алокаторів пам'яті. Код `MATCHING_SUCCESS` гарантує успішне завершення операції. Коди від'ємних значень сигналізують про помилки виділення пам'яті або вихід за межі масиву.

:::tabs
```c
typedef enum {
    MATCHING_SUCCESS = 0,
    MATCHING_ERROR_INVALID_PARAM = -1,
    MATCHING_ERROR_OUT_OF_MEMORY = -2,
    MATCHING_ERROR_INDEX_OUT_OF_BOUNDS = -3,
    MATCHING_ERROR_GRAPH_TOO_LARGE = -4,
    MATCHING_ERROR_STATE_CORRUPTED = -5,
    MATCHING_ERROR_NULL_POINTER = -6
} matching_error_t;

typedef enum {
    MATCHING_MODE_CARDINALITY = 0,
    MATCHING_MODE_WEIGHTED_EXACT = 1,
    MATCHING_MODE_WEIGHTED_APPROX = 2
} matching_mode_t;

typedef struct {
    void* (*custom_malloc)(size_t size);
    void (*custom_free)(void* ptr);
    void* (*custom_realloc)(void* ptr, size_t new_size);
} matching_allocator_t;
```
```cpp
namespace graph::matching {

enum class ErrorCode {
    Success = 0,
    InvalidParam = -1,
    OutOfMemory = -2,
    IndexOutOfBounds = -3,
    GraphTooLarge = -4,
    StateCorrupted = -5,
    NullPointer = -6
};

enum class Mode {
    Cardinality = 0,
    WeightedExact = 1,
    WeightedApprox = 2
};

struct Allocator {
    std::function<void*(size_t)> custom_malloc;
    std::function<void(void*)> custom_free;
    std::function<void*(void*, size_t)> custom_realloc;
};

} // namespace graph::matching
```
:::

### 2. Структури результатів та статистики

Структури результатів зберігають масиви обраних ребер, сумарну вагу, вектор парності вершин (вільні вершини позначаються як `-1`), а також обчислювальні метрики, такі як кількість згорнутих квіток та кількість виконаних розширених ітерацій BFS.

:::tabs
```c
typedef struct {
    int u;
    int v;
    double weight;
} matching_edge_t;

typedef struct {
    size_t num_edges;
    double total_weight;
    matching_edge_t* edges;
    int* mate_array;
} matching_result_t;

typedef struct {
    uint64_t num_augmentations;
    uint64_t num_blossoms_contracted;
    uint64_t num_lca_searches;
    double elapsed_milliseconds;
} matching_stats_t;
```
```cpp
namespace graph::matching {

struct Edge {
    int u;
    int v;
    double weight{1.0};

    constexpr bool operator==(const Edge& other) const noexcept {
        return (u == other.u && v == other.v) || (u == other.v && v == other.u);
    }
};

struct Statistics {
    uint64_t num_augmentations{0};
    uint64_t num_blossoms_contracted{0};
    uint64_t num_lca_searches{0};
    double elapsed_milliseconds{0.0};
};

struct Result {
    size_t num_edges{0};
    double total_weight{0.0};
    std::vector<Edge> edges;
    std::vector<int> mate; // mate[u] містить індекс суміжної вершини або -1
    Statistics stats;
};

} // namespace graph::matching
```
:::

### 3. Основні функції та методи управління графом

Основні процедури забезпечують створення екземпляра розв'язувача, послідовне додавання ребер графа, виконання алгоритму Едмондса та коректне звільнення виділених ресурсів. Метод `reserve_edges` в C++ API дозволяє попередньо зарезервувати буфери пам'яті для уникнення повторних алокацій при додаванні багатьох ребер.

:::tabs
```c
/* Створення та знищення графа */
matching_graph_t* matching_graph_create(size_t num_vertices, matching_mode_t mode, const matching_allocator_t* alloc);
void matching_graph_destroy(matching_graph_t* graph);

/* Додавання ребра та аналіз складності */
matching_error_t matching_graph_add_edge(matching_graph_t* graph, int u, int v, double weight);

/* Обчислення паросполучення та звільнення пам'яті результату */
matching_error_t matching_solve(matching_graph_t* graph, matching_result_t* out_result, matching_stats_t* out_stats);
void matching_result_free(matching_result_t* result);
```
```cpp
namespace graph::matching {

class MatchingSolver {
public:
    explicit MatchingSolver(size_t num_vertices, Mode mode = Mode::Cardinality, const std::optional<Allocator>& alloc = std::nullopt);
    ~MatchingSolver() noexcept;

    MatchingSolver(const MatchingSolver&) = delete;
    MatchingSolver& operator=(const MatchingSolver&) = delete;

    MatchingSolver(MatchingSolver&&) noexcept;
    MatchingSolver& operator=(MatchingSolver&&) noexcept;

    void add_edge(int u, int v, double weight = 1.0);
    void reserve_edges(size_t num_edges);

    [[nodiscard]] Result solve();
    [[nodiscard]] size_t num_vertices() const noexcept;
    [[nodiscard]] size_t num_edges() const noexcept;

    void clear() noexcept;

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace graph::matching
```
:::

## Переходи станів та автоматно-структурний інваріант

Об'єкт розв'язувача моделюється у вигляді детермінованого скінченного автомата. Дотримання послідовності викликів гарантує відсутність невизначеної поведінки при зміні графа.

Таблиця станів описує допустимі моменти виконання операцій:

| Початковий стан | Виклик функції / подія | Наступний стан | Системний інваріант |
| :--- | :--- | :--- | :--- |
| `Uninitialized` | `create()` / Конструктор | `Building` | Контекст виділено; граф порожній; `num_edges == 0` |
| `Building` | `add_edge(u, v)` | `Building` | Ребро записане в списки; `0 <= u, v < V` |
| `Building` | `solve()` | `Solved` | Пошук завершено; `match` містить оптимальне паросполучення |
| `Solved` | `add_edge(u, v)` | `Building` | Результат розв'язку інвалідовано; потрібен новий `solve()` |
| `Solved` | `clear()` | `Building` | Ребра й паросполучення скинуто; пам'ять вершин збережено |
| `Building` / `Solved` | `destroy()` / Деструктор | `Uninitialized` | Усі ресурси та буфери пам'яті повністю звільнено |

При виклику `add_edge()` у стані `Solved` попередньо обчислене паросполучення інвалідується. Компонент автоматично скидає кешовані результати та повертається в стан `Building`.

## Параметри конфігурації та оцінка ресурсомісткості

### Обсяг оперативної пам'яті (Memory Overhead)

Для графа з `V` вершинами та `E` ребрами витрати оперативної пам'яті складаються з наступних компонентів:
- **Списки суміжності:** `2 · E · sizeof(int)` байт (для збереження орієнтованих дуг неорієнтованого графа).
- **Масиви стану алгоритму:** `5 · V · sizeof(int)` байт (`match`, `parent`, `base`, `type`, `visited_lca`).
- **Черга BFS:** `V · sizeof(int)` байт.

Для типового графа з `V = 100,000` та `E = 500,000` сумарні витрати пам'яті не перевищують `12.5 МБ`, що робить розв'язувач придатним для вбудованих систем та серверних додатків з обмеженими ресурсами.

### Продуктивність та часові межі (Performance Benchmarks)

Таблиця нижче ілюструє очікувані витрати процесорного часу при обчисленні максимальних паросполучень на стандартній серверній платформі:

| Категорія графа | Просторовий масштаб (`V`, `E`) | Складність алгоритму | Очікуваний час виконання |
| :--- | :--- | :--- | :--- |
| Двочастковий граф | `V = 10,000, E = 50,000` | `O(V · E)` | ~12 мс |
| Розріджений недвочастковий | `V = 10,000, E = 30,000` | `O(V · E)` | ~28 мс |
| Щільний випадковий граф | `V = 5,000, E = 500,000` | `O(V^3)` | ~165 мс |
| Граф зі складною вкладеністю квіток | `V = 8,000, E = 40,000` | `O(V · E α(V))` | ~42 мс |

## Регламент володіння пам'яттю та управління ресурсами

1. **Контракт володіння C API:**
   - Пам'ять для `matching_graph_t` виділяється функцією `matching_graph_create` і вимагає обов'язкового виклику `matching_graph_destroy`.
   - Вихідний масив результату `out_result->edges` та `out_result->mate_array` виділяється функцією `matching_solve`. Клієнтський код зобов'язаний передати `out_result` у функцію `matching_result_free` після завершення роботи з даними.
2. **Контракт володіння C++ API:**
   - Клас `MatchingSolver` застосовує ідіому RAII. Пам'ять внутрішніх масивів виділяється у конструкторі та автоматично звільняється у деструкторі.
   - Метод `solve()` повертає значення за семантикою переміщення (англ. *move semantics*). Вектор ребер `edges` та вектор парності `mate` передаються клієнту без копіювання буферів.

## Потокобезпека та багаторазове використання (Thread Safety)

- **Конкурентне читання:** Одночасне читання даних із декількох потоків без модифікації об'єкта є абсолютно потокобезпечним.
- **Паралельне обчислення:** Для паралельного розв'язання декількох задач кожен потік повинен використовувати свій власний екземпляр `MatchingSolver`.
- **Синхронізація:** При модифікації одного й того самого об'єкта з декількох потоків необхідна зовнішня синхронізація через `std::mutex` або м'ютекси POSIX.

## Опис помилок та крайові випадки

Розв'язувач гарантує строге повернення описових кодів помилок замість створення аварійного завершення (крашу):
- `MATCHING_ERROR_NULL_POINTER`: Передано `NULL` у якості контексту графа або вихідної структури.
- `MATCHING_ERROR_INDEX_OUT_OF_BOUNDS`: Індекси вершин `u` або `v` знаходяться поза діапазоном `[0, num_vertices - 1]`.
- `MATCHING_ERROR_INVALID_PARAM`: Спроба додавання самопетлі (`u == v`) або від'ємної ваги у зваженому режимі.
- `MATCHING_ERROR_OUT_OF_MEMORY`: Невдале виділення динамічної пам'яті алокатором.
- `MATCHING_ERROR_STATE_CORRUPTED`: Спроба запуску `matching_solve` на об'єкті, що не пройшов ініціалізацію.

Уся обробка помилок у C++ API супроводжується генеруванням винятків типу `std::invalid_argument`, `std::out_of_range` або `std::bad_alloc`, що зберігає узгодженість зі стандартною бібліотекою C++.
