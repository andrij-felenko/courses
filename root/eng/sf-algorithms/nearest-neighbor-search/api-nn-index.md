# 📋 Програмний інтерфейс індексу пошуку найближчих сусідів

Уніфікований інтерфейс просторового та векторного пошуку визначає програмний контракт для побудови індексів, динамічного додавання векторів, а також виконання точних і наближених запитів `k`-найближчих сусідів (k-NN) та радіусного пошуку (Range Search).

Інтерфейс спроєктовано з урахуванням суворих вимог до багатопотокової безпеки, нульового копіювання буферів (zero-copy), прямої векторизації пам'яті через інструкції SIMD та детального збору діагностичної телеметрії запитів (кількість відвіданих вузлів, обчислених відстаней та тривалість виконання).

### Типи даних та конфігурація індексу

:::tabs
```c
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

/* Метрика відстані */
typedef enum {
    NN_METRIC_L2 = 0,             /* Квадрат або лінійна евклідова відстань */
    NN_METRIC_COSINE = 1,         /* Косинусна кутова відстань: 1 - cos(theta) */
    NN_METRIC_INNER_PRODUCT = 2   /* Скалярний добуток: -<u, v> (для максимального добутку) */
} nn_metric_type_t;

/* Тип алгоритмічного рушія індексу */
typedef enum {
    NN_ENGINE_FLAT_SCAN = 0,      /* Точний паралельний SIMD-скан */
    NN_ENGINE_METRIC_TREE = 1,    /* Метричне дерево (VP-Tree / Ball-Tree) */
    NN_ENGINE_GRAPH_HNSW = 2,     /* Наближений ієрархічний граф (HNSW) */
    NN_ENGINE_QUANTIZED_IVF = 3   /* Інвертований індекс із квантуванням (IVF-PQ) */
} nn_engine_type_t;

/* Коди результатів виконання операцій */
typedef enum {
    NN_SUCCESS = 0,
    NN_ERR_INVALID_ARGUMENT = -1,
    NN_ERR_OUT_OF_MEMORY = -2,
    NN_ERR_DIMENSION_MISMATCH = -3,
    NN_ERR_INDEX_NOT_BUILT = -4,
    NN_ERR_CONCURRENCY_VIOLATION = -5
} nn_status_t;

/* Конфігурація для створення індексу */
typedef struct {
    int dimension;                /* Розмірність векторного простору D */
    nn_metric_type_t metric;      /* Метрика відстані */
    nn_engine_type_t engine;      /* Архітектурний тип індексу */
    size_t initial_capacity;      /* Очікувана початкова кількість точок N */
    float approximation_factor;   /* Епсилон (epsilon) для наближеного пошуку (0 = точно) */
    int num_threads;              /* Кількість потоків для побудови та пакетного пошуку */
} nn_config_t;

/* Діагностичні метрики виконання окремого запиту */
typedef struct {
    size_t distance_evaluations;  /* Реальна кількість виконаних обчислень відстаней */
    size_t nodes_visited;         /* Кількість відвіданих вузлів дерева чи вершин графа */
    double latency_microseconds;  /* Тривалість виконання запиту в мікросекундах */
    float recall_estimate;        /* Оцінка Recall відносно точного скану */
} nn_search_stats_t;

/* Контейнер результатів пошуку */
typedef struct {
    int64_t *ids;                 /* Масив ідентифікаторів знайдених точок розміром k */
    float *distances;             /* Масив відстаней до знайдених точок розміром k */
    size_t count;                 /* Фактична кількість повернених точок (<= k) */
    size_t capacity;              /* Виділений розмір буферів */
} nn_result_set_t;

/* Непрозорий покажчик на екземпляр індексу */
typedef struct nn_index nn_index_t;
```
```cpp
#include <cstddef>
#include <cstdint>
#include <span>
#include <vector>
#include <memory>
#include <expected>
#include <chrono>

enum class MetricType {
    L2 = 0,
    Cosine = 1,
    InnerProduct = 2
};

enum class EngineType {
    FlatScan = 0,
    MetricTree = 1,
    GraphHNSW = 2,
    QuantizedIVF = 3
};

enum class IndexError {
    InvalidArgument = 1,
    OutOfMemory = 2,
    DimensionMismatch = 3,
    IndexNotBuilt = 4,
    ConcurrencyViolation = 5
};

struct IndexConfig {
    int dimension{128};
    MetricType metric{MetricType::L2};
    EngineType engine{EngineType::FlatScan};
    size_t initial_capacity{10000};
    float approximation_factor{0.0f};
    int num_threads{0};
};

struct SearchStats {
    size_t distance_evaluations{0};
    size_t nodes_visited{0};
    std::chrono::nanoseconds latency{0};
    float recall_estimate{1.0f};
};

struct SearchResult {
    std::vector<int64_t> ids;
    std::vector<float> distances;
    SearchStats stats;
};

class INearestNeighborIndex {
public:
    virtual ~INearestNeighborIndex() = default;

    [[nodiscard]] virtual int dimension() const noexcept = 0;
    [[nodiscard]] virtual size_t size() const noexcept = 0;
    [[nodiscard]] virtual MetricType metric() const noexcept = 0;

    virtual std::expected<void, IndexError> build(
        std::span<const float> raw_vectors,
        std::span<const int64_t> ids) = 0;

    virtual std::expected<void, IndexError> insert(
        int64_t id,
        std::span<const float> vector) = 0;

    [[nodiscard]] virtual std::expected<SearchResult, IndexError> search_knn(
        std::span<const float> query,
        size_t k) const = 0;

    [[nodiscard]] virtual std::expected<SearchResult, IndexError> search_radius(
        std::span<const float> query,
        float radius) const = 0;
};
```
:::

### Опис функцій C API

| Сигнатура функції | Призначення | Повертане значення |
|---|---|---|
| `nn_index_create(const nn_config_t *cfg, nn_index_t **out)` | Виділення пам'яті та ініціалізація індексу за конфігурацією | `NN_SUCCESS` або код помилки |
| `nn_index_build(nn_index_t *idx, const float *data, const int64_t *ids, size_t n)` | Пакетне завантаження `n` векторів та побудова оптимізованої структури | `NN_SUCCESS`, `NN_ERR_DIMENSION_MISMATCH` |
| `nn_index_insert(nn_index_t *idx, int64_t id, const float *vec)` | Динамічна вставка окремого вектора в наявну структуру індексу | `NN_SUCCESS`, `NN_ERR_OUT_OF_MEMORY` |
| `nn_index_search_knn(const nn_index_t *idx, const float *q, size_t k, nn_result_set_t *res, nn_search_stats_t *st)` | Пошук `k` найближчих сусідів для вектора запиту `q` | `NN_SUCCESS` або код помилки |
| `nn_index_search_radius(const nn_index_t *idx, const float *q, float r, nn_result_set_t *res, nn_search_stats_t *st)` | Пошук усіх точок, що лежать у межах евклідової сфери радіуса `r` | `NN_SUCCESS` або код помилки |
| `nn_index_free(nn_index_t *idx)` | Безпечне вивільнення всіх внутрішніх масивів і структур індексу | Повертає `void` |

### Сигнатури функцій мовою C

:::tabs
```c
/* Створення нового екземпляра індексу */
nn_status_t nn_index_create(const nn_config_t *config, nn_index_t **out_index);

/* Пакетна побудова індексу з лінійного буфера координат */
nn_status_t nn_index_build(nn_index_t *index,
                           const float *vectors_flat,
                           const int64_t *ids,
                           size_t count);

/* Динамічне додавання одного вектора */
nn_status_t nn_index_insert(nn_index_t *index,
                            int64_t id,
                            const float *vector);

/* Пошук k найближчих сусідів */
nn_status_t nn_index_search_knn(const nn_index_t *index,
                                const float *query,
                                size_t k,
                                nn_result_set_t *out_result,
                                nn_search_stats_t *out_stats);

/* Радіусний пошук (Range Search) */
nn_status_t nn_index_search_radius(const nn_index_t *index,
                                   const float *query,
                                   float radius,
                                   nn_result_set_t *out_result,
                                   nn_search_stats_t *out_stats);

/* Вивільнення ресурсів */
void nn_index_free(nn_index_t *index);
```
```cpp
/* Фабричний метод для створення поліморфного індексу */
std::unique_ptr<INearestNeighborIndex> create_nearest_neighbor_index(const IndexConfig& config);
```
:::

### Деталізація кодів помилок та виняткових ситуацій

1. **`NN_SUCCESS` (0)**: Операція виконана успішно, вихідні структури заповнені валідними даними.
2. **`NN_ERR_INVALID_ARGUMENT` (-1)**: Некоректні параметри виклику: нульовий покажчик на запит, розмірність `dimension ≤ 0`, запитувана кількість сусідів `k = 0`, або від'ємне значення радіуса у радіусному пошуку.
3. **`NN_ERR_OUT_OF_MEMORY` (-2)**: Системі не вдалося виділити необхідний обсяг динамічної пам'яті для внутрішніх масивів індексу чи буферів результатів.
4. **`NN_ERR_DIMENSION_MISMATCH` (-3)**: Розмірність переданого вектора запиту не збігається з розмірністю `D`, зафіксованою під час ініціалізації індексу.
5. **`NN_ERR_INDEX_NOT_BUILT` (-4)**: Спроба виконати запит до порожнього індексу або індексу, для якого ще не завершено фазу побудови `nn_index_build`.
6. **`NN_ERR_CONCURRENCY_VIOLATION` (-5)**: Виявлено стан перегонів (англ. *data race*), наприклад виконання запиту одночасно з модифікацією структури індексу іншим потоком без блокування.

### Життєвий цикл індексу та керування ресурсами

Життєвий цикл структури просторового пошуку складається з чітких послідовних фаз:

1. **Ініціалізація (`nn_index_create`)**:
   - Виділяється керуюча структура, перевіряється валідність параметрів та апаратна підтримка SIMD на поточному процесорі.
   - Якщо обрано режим `NN_ENGINE_FLAT_SCAN`, виділяється вирівняний буфер під вектори. Для `NN_ENGINE_GRAPH_HNSW` ініціалізуються списки суміжності.
2. **Наповнення та індексація (`nn_index_build` або `nn_index_insert`)**:
   - **Пакетний режим (`build`)**: Найбільш ефективний шлях створення. Всі `N` векторів передаються суцільним масивом. Дерева (VP-Tree, KD-Tree) будуються збалансованими за `O(N log N)`, а графи будують зв'язки з оптимізованим порядком вставки.
   - **Потоковий режим (`insert`)**: Дозволяє додавати окремі вектори під час роботи системи. Для дерев може вимагати періодичного перебалансування при накопиченні перекосів.
3. **Виконання запитів (`search_knn`, `search_radius`)**:
   - Запит читає незмінні структури індексу. Клієнт передає масив координат довжиною `D` та отримує відсортований за зростанням відстані список знайдених сусідів.
4. **Знищення та вивільнення (`nn_index_free`)**:
   - Рекурсивно або ітеративно звільняються всі внутрішні вузли, вирівняні буфери координат та допоміжні таблиці.

### Інтерпретація метрик діагностики (Search Stats)

Структура `nn_search_stats_t` повертає телеметрію, критично важливу для тюнінгу параметрів навантажених систем:
- **`distance_evaluations`**: Кількість реальних обчислень відстаней між парою векторів. Для Flat Scan це завжди рівно `N`. Для ефективного дерева чи графа це число становить `0.01%..5%` від `N`. Якщо це число наближається до `N`, це свідчить про деградацію індексу через прокляття розмірності.
- **`nodes_visited`**: Кількість пройдених внутрішніх вузлів дерева чи вершин графа під час жадібного пошуку. Порівняння `nodes_visited` із `distance_evaluations` дозволяє оцінити накладні витрати на навігацію індексом.
- **`latency_microseconds`**: Астрономічний час виконання запиту процесором. Дозволяє виявляти просідання продуктивності через затримки кеш-пам'яті або переривання.
- **`recall_estimate`**: Частка повернених сусідів, які справді входять до істинної множини найближчих точок. Використовується під час автоматичного калібрування параметрів наближеного пошуку на валідаційних вибірках.

### Бінарна серіалізація та підтримка відображення пам'яті (Memory-Mapped I/O)

Для промислових баз даних із мільйонами векторів час холодного старту сервера має вирішальне значення. Інтерфейс підтримує збереження та миттєве завантаження індексу з диска без повного копіювання в оперативну пам'ять:

- **Бінарний заголовок файлу**:
  - Магічне число (4 байти): `0x4E4E4958` (`"NNIX"`).
  - Версія формату (2 байти): `0x0001`.
  - Тип метрики та рушія (2 байти).
  - Розмірність `D` (4 байти) та загальна кількість векторів `N` (8 байтів).
  - Оффсет до таблиці векторів та оффсет до графової чи деревної структури.
- **Відображення у пам'ять (`mmap`)**:
  - Для пласких індексів (`Flat Scan`) або квантованих баз (`IVF-PQ`) файл монтується системним викликом `mmap(PROT_READ, MAP_SHARED)`.
  - Операційна система автоматично підтягує сторінки файлу з SSD у сторінковий кеш ядра (англ. *page cache*) за запитом, дозволяючи виконувати пошук у базах даних розміром 100+ ГБ, що перевищують фізичний обсяг RAM.

### Пакетна оптимізація запитів (Batch Search)

Коли сервер одночасно отримує сотні запитів від різних клієнтів, обробка кожного запиту окремо є неефективною з точки зору пропускної здатності шини пам'яті. У лінійному пошуку кожен окремий запит вимагає повного прочитання всієї бази `N × D × 4` байтів із пам'яті до кешу.

Пакетний пошук (англ. *batch search*) завантажує матрицю запитів розміром `B × D` (де `B = 32..256`) і перемножує її з блоками бази розміром `M × D` за допомогою блокових матричних операцій GEMM (General Matrix Multiply). Це дозволяє прочитати кожен вектор бази даних з оперативної пам'яті лише один раз для цілої пачки запитів, піднімаючи сумарну пропускну здатність системи (QPS) у 4–10 разів.

### Інваріанти та гарантії потокобезпечності (Concurrency Model)

1. **Багаточитацька безпека (Concurrent Queries)**:
   - Функції `nn_index_search_knn` та `nn_index_search_radius` є повністю реентрабельними (англ. *reentrant*) і потокобезпечними за умови, що індекс уже побудовано і до нього не застосовуються паралельні мутації.
   - Сотні потоків можуть одночасно виконувати читання спільних структур без використання м'ютексів та блокувань (lock-free read paths).
2. **Мутації та динамічні вставки**:
   - Виклики `nn_index_build` та `nn_index_insert` вимагають ексклюзивного доступу до структури (single-writer model).
   - У багатопотокових середовищах із постійним потоком оновлень рекомендується використовувати подвійну буферизацію (англ. *double-buffering*) або графові реалізації з гранулярним блокуванням окремих списків суміжності через атомарні операції `std::atomic`.
3. **Керування пам'яттю**:
   - Буфери `ids` та `distances` у структурі `nn_result_set_t` виділяються клієнтським кодом або автоматично розширюються функцією пошуку через `realloc`.
   - Виклик `nn_index_free` звільняє виключно внутрішні таблиці індексу і не зачіпає вектори клієнта, якщо вони передавалися через покажчик на зовнішню пам'ять.
