# 📋 Інтерфейс комбінаторного вкладення та перевірки планарності

Ця довідкова специфікація визначає програмний контракт (C/C++ API) для представлення планарних графів, виконання лінійної перевірки планарності, побудови комбінаторних карт (системи ротацій та подвійно зв'язаного списку ребер DCEL), виділення топологічних граней, обчислення двоїстого графа, а також вилучення сертифіката непланарності Куратовського.

Інтерфейс спроектовано для використання у високонавантажених CAD/EDA системах проектування топології мікросхем, модулях візуалізації великих графів, геоінформаційних системах (ГІС) та бібліотеках обчислювальної геометрії.

## Архітектурні принципи та вибір структур даних

При роботі з планарними графами у промислових системах традиційні матриці суміжності або неструктуровані списки сусідів є недостатніми. Матриця суміжності вимагає квадратичної пам'яті `O(V²)`, що неприпустимо для графів на мільйони вершин, для яких кількість ребер обмежена лінійною величиною `E ≤ 3V - 6`. Звичайні списки суміжності зберігають зв'язки між вершинами, проте повністю ігнорують топологію граней та взаємний порядок слідування ребер на площині.

Для забезпечення максимальної швидкодії, стабільності та математичної точності в бібліотеці реалізовано комбіновану архітектуру:
- **Низькорівневий C-інтерфейс** використовує компактні плоскі масиви з попереднім виділенням пам'яті. Усі топологічні вказівники замінено на 32-бітні цілочисельні індекси, що гарантує відсутність фрагментації купи та забезпечує безперервне розміщення даних у кеш-пам'яті процесора (L1/L2 Cache Locality).
- **Високорівневий C++20 інтерфейс** загортає низькорівневі дескриптори в безпечні RAII-обгортки, надає семантику переміщення, виключає витоки пам'яті та транслює помилки через стандартний монодичний тип `std::expected`.
- **Топологічна модель напівребер (Half-Edge / DCEL)** дозволяє здійснювати обхід довільної грані за час, пропорційний її ступеню `O(deg(f))`, та підтримує ефективне додавання і видалення ребер без глобальної перебудови графа.

## Огляд архітектури типів та структур даних

### 1. Перелік кодів результатів (`PlanarResult` / `PlanarStatus`)

Кожна операція бібліотеки повертає чітко типізований статус виконання, що дозволяє відокремити нормальний стан планарності від помилок виділення пам'яті чи некоректних аргументів.

:::tabs
```c
typedef enum PlanarResult {
    PLANAR_OK                  =  0, /* Операція успішна; граф є планарним */
    PLANAR_NON_PLANAR          =  1, /* Граф непланарний (знайдено обструкцію Куратовського) */
    PLANAR_ERR_NULL_PTR        = -1, /* Передано нульовий вказівник на обов'язковий дескриптор */
    PLANAR_ERR_INVALID_VERT    = -2, /* Індекс вершини виходить за межі діапазону [0, V-1] */
    PLANAR_ERR_EDGE_CAPACITY   = -3, /* Перевищено максимальну місткість виділеного масиву ребер */
    PLANAR_ERR_NOT_EMBEDDED    = -4, /* Запит граней або координат для графа без вкладення */
    PLANAR_ERR_NO_CERTIFICATE  = -5  /* Запит сертифіката Куратовського для планарного графа */
} PlanarResult;
```
```cpp
#include <system_error>
#include <string_view>

enum class PlanarStatus {
    Ok = 0,
    NonPlanar,
    NullPointer,
    InvalidVertex,
    EdgeCapacityExceeded,
    NotEmbedded,
    NoCertificate
};

[[nodiscard]] constexpr std::string_view to_string(PlanarStatus status) noexcept {
    switch (status) {
        case PlanarStatus::Ok: return "OK (Planar)";
        case PlanarStatus::NonPlanar: return "Non-Planar Graph";
        case PlanarStatus::NullPointer: return "Null Pointer Error";
        case PlanarStatus::InvalidVertex: return "Invalid Vertex Index";
        case PlanarStatus::EdgeCapacityExceeded: return "Edge Capacity Exceeded";
        case PlanarStatus::NotEmbedded: return "Graph Not Embedded";
        case PlanarStatus::NoCertificate: return "No Kuratowski Certificate Available";
    }
    return "Unknown Error";
}
```
:::

Семантика кодів результатів:
- `PLANAR_OK`: свідчить про успішне виконання функції. Якщо викликалася функція перевірки планарності, цей статус означає, що граф можна вкласти у площину без перетинів.
- `PLANAR_NON_PLANAR`: повертається функціями аналізу або побудови вкладення, коли топологічний бар'єр унеможливлює плоске розташування.
- Коди помилок із від'ємними значеннями свідчать про порушення контракту виклику (недійсні дескриптори, некоректні індекси вершин або спроба звернення до топологічних граней до моменту побудови комбінаторного вкладення).

### 2. Тип обструкції Куратовського (`KuratowskiType` / `ObstructionType`)

Топологічна класифікація забороненого підграфа визначає форму свідка непланарності згідно з класичною теоремою Куратовського.

:::tabs
```c
typedef enum KuratowskiType {
    KURATOWSKI_NONE = 0, /* Граф планарний; заборонені конфігурації відсутні */
    KURATOWSKI_K5   = 1, /* Знайдено топологічне підрозбиття або мінор повного графа K5 */
    KURATOWSKI_K3_3 = 2  /* Знайдено топологічне підрозбиття або мінор повного двочасткового графа K3,3 */
} KuratowskiType;
```
```cpp
enum class ObstructionType {
    None = 0,
    K5,
    K3_3
};
```
:::

Семантика типів обструкції:
- `KURATOWSKI_K5`: свідок містить 5 базових вершин степеня 4 та 10 неперетинних простих шляхів, що з'єднують кожну пару цих вершин.
- `KURATOWSKI_K3_3`: свідок містить дві групи по 3 базові вершини (степеня 3) та 9 неперетинних простих шляхів між вершинами протилежних груп.

### 3. Структура сертифіката непланарності (`KuratowskiCertificate`)

Сертифікат непланарності надає вичерпний топологічний доказ того, чому граф не може бути зображений на площині.

:::tabs
```c
typedef struct KuratowskiPath {
    int u;                  /* Початкова базова вершина */
    int v;                  /* Кінцева базова вершина */
    int* path_vertices;     /* Масив проміжних вершин підрозбиття ребра (довжини length + 1) */
    int length;             /* Кількість ребер у топологічному шляху */
} KuratowskiPath;

typedef struct KuratowskiCertificate {
    KuratowskiType type;    /* Тип знайденої обструкції (K5 або K3,3) */
    int core_vertices[6];   /* Індекси базових вузлів (5 для K5, 6 для K3,3) */
    int core_count;         /* Кількість базових вузлів (5 або 6) */
    KuratowskiPath paths[15]; /* Топологічні шляхи між базовими вузлами (10 для K5, 9 для K3,3) */
    int path_count;         /* Загальна кількість шляхів */
} KuratowskiCertificate;
```
```cpp
#include <vector>

struct SubdividedPath {
    std::size_t u;
    std::size_t v;
    std::vector<std::size_t> vertices;
};

struct KuratowskiWitness {
    ObstructionType type{ObstructionType::None};
    std::vector<std::size_t> core_vertices;
    std::vector<SubdividedPath> paths;

    [[nodiscard]] bool is_valid() const noexcept {
        return type != ObstructionType::None;
    }
};
```
:::

Поля структури сертифіката:
- `core_vertices`: містить індекси вихідних вершин, які утворюють каркас повної конфігурації.
- `paths`: масив ланцюжків вершин, що утворюють підрозбиті ребра. Кожен такий шлях з'єднує дві базові вершини та не перетинається внутрішніми вершинами з іншими шляхами сертифіката.

### 4. Подвійно зв'язаний список напівребер (`HalfEdge` / DCEL)

Для ефективного обходу граней, пошуку суміжних областей та побудови двоїстих графів використовується топологічна модель подвійно зв'язаного списку ребер (Doubly Connected Edge List, DCEL).

:::tabs
```c
typedef struct HalfEdge {
    int id;                 /* Унікальний числовий ідентифікатор напівребра */
    int origin;             /* Індекс вершини, з якої виходить напівребро */
    int twin;               /* Індекс парного протилежного напівребра (origin -> target) */
    int next;               /* Наступне напівребро вздовж периметра грані проти годинникової стрілки */
    int prev;               /* Попереднє напівребро вздовж периметра тієї самої грані */
    int face;               /* Індекс грані, розташованої зліва від напівребра */
} HalfEdge;
```
```cpp
struct HalfEdgeRecord {
    std::size_t id;
    std::size_t origin;
    std::size_t twin;
    std::size_t next;
    std::size_t prev;
    std::size_t face;
};
```
:::

Топологічні інваріанти структури `HalfEdge`:
- Для кожного напівребра `h` виконується `half_edges[h.twin].twin == h.id`.
- Напівребро `h` та його `twin` мають протилежні орієнтації: `half_edges[h.twin].origin == half_edges[h.next].origin`.
- Замкнений обхід `h = h.next` утворює межу рівно однієї зв'язної грані.

### 5. Структура грані (`PlanarFace` / `FaceRecord`)

:::tabs
```c
typedef struct PlanarFace {
    int id;                 /* Унікальний ідентифікатор грані [0, num_faces - 1] */
    int outer_half_edge;    /* Одне з напівребер зовнішньої межі грані */
    int edge_count;         /* Ступінь грані deg(f) (кількість ребер на її периметрі) */
    bool is_unbounded;      /* true для зовнішньої необмеженої грані f_ext */
} PlanarFace;
```
```cpp
#include <vector>

struct FaceRecord {
    std::size_t id;
    std::size_t start_edge;
    std::size_t degree;
    bool is_unbounded{false};
    std::vector<std::size_t> boundary_vertices;
};
```
:::

### 6. Основний дескриптор графа (`PlanarGraph` / `PlanarGraphModel`)

:::tabs
```c
typedef struct PlanarGraph {
    int num_vertices;       /* Кількість вершин V */
    int num_edges;          /* Кількість ненапрямлених ребер E */
    int num_faces;          /* Кількість граней F */
    
    int* head;              /* Індекси перших напівребер для кожної вершини */
    HalfEdge* half_edges;   /* Масив напівребер розміром 2 * max_edges */
    int half_edge_count;    /* Поточна кількість напівребер у масиві */
    int max_edges;          /* Максимальна виділена місткість ребер */
    
    int** rotation_system;  /* rotation_system[u] — циклічний масив ребер навколо u */
    int* rotation_degree;   /* Ступінь кожної вершини deg(u) */
    bool is_embedded;       /* true, якщо вкладення побудовано успішно */
    
    PlanarFace* faces;      /* Масив топологічних граней розбиття */
} PlanarGraph;
```
```cpp
#include <vector>
#include <memory>

class PlanarGraphModel {
public:
    explicit PlanarGraphModel(std::size_t num_vertices, std::size_t max_edges = 0);
    ~PlanarGraphModel() = default;

    PlanarGraphModel(const PlanarGraphModel&) = delete;
    PlanarGraphModel& operator=(const PlanarGraphModel&) = delete;
    PlanarGraphModel(PlanarGraphModel&&) noexcept = default;
    PlanarGraphModel& operator=(PlanarGraphModel&&) noexcept = default;

    [[nodiscard]] std::size_t vertex_count() const noexcept { return num_vertices_; }
    [[nodiscard]] std::size_t edge_count() const noexcept { return num_edges_; }
    [[nodiscard]] std::size_t face_count() const noexcept { return faces_.size(); }
    [[nodiscard]] bool is_embedded() const noexcept { return is_embedded_; }

private:
    std::size_t num_vertices_{0};
    std::size_t num_edges_{0};
    bool is_embedded_{false};

    std::vector<HalfEdgeRecord> half_edges_;
    std::vector<std::vector<std::size_t>> rotation_system_;
    std::vector<FaceRecord> faces_;
};
```
:::

## Специфікація функцій життєвого циклу графа

### `planar_graph_create`
Виділяє пам'ять та ініціалізує первинні таблиці дескриптора графа.

:::tabs
```c
PlanarResult planar_graph_create(PlanarGraph** graph, int num_vertices, int max_edges);
```
```cpp
#include <expected>
#include <memory>

[[nodiscard]] std::expected<std::unique_ptr<PlanarGraphModel>, PlanarStatus>
create_planar_graph(std::size_t num_vertices, std::size_t max_edges = 0);
```
:::

- **Вхідні параметри:**
  - `num_vertices`: кількість вершин у створюваному графі. Мусить задовольняти умові `num_vertices ≥ 1`.
  - `max_edges`: попередньо зарезервована місткість масиву ненапрямлених ребер. Якщо передано `0`, бібліотека автоматично резервує `max_edges = 3 * num_vertices - 6` згідно з максимальною межею Ейлера.
- **Вихідні параметри:**
  - `graph`: адреса покажчика, у який записується створений дескриптор.
- **Повертані значення:**
  - `PLANAR_OK`: успішне виділення та ініціалізація.
  - `PLANAR_ERR_NULL_PTR`: передано `NULL` замість адреси вихідного дескриптора.
  - `PLANAR_ERR_INVALID_VERT`: значення `num_vertices < 1`.
- **Попередні умови:** Вказівник `graph != NULL`.
- **Післяумови:** Створено порожній граф із нульовою кількістю ребер та граней. Усі списки суміжності ініціалізовано значенням `-1`.

### `planar_graph_destroy`
Звільняє всі внутрішні динамічні буфери дескриптора.

:::tabs
```c
void planar_graph_destroy(PlanarGraph* graph);
```
```cpp
// У C++ виклик деструктора ~PlanarGraphModel() здійснюється автоматично через RAII (std::unique_ptr).
```
:::

- **Вхідні параметри:** `graph` — дескриптор графа, пам'ять якого підлягає звільненню (якщо передано `NULL`, функція повертає керування без дій).
- **Гарантія безпеки:** Безпечно викликати для графа у будь-якому стані (як до побудови вкладення, так і після).

### `planar_graph_add_edge`
Додає нове ненапрямлене ребро між двома вершинами.

:::tabs
```c
PlanarResult planar_graph_add_edge(PlanarGraph* graph, int u, int v, int* edge_id);
```
```cpp
[[nodiscard]] std::expected<std::size_t, PlanarStatus>
PlanarGraphModel::add_edge(std::size_t u, std::size_t v);
```
:::

- **Вхідні параметри:**
  - `graph`: активний дескриптор графа.
  - `u, v`: індекси вершин, які необхідно з'єднати ребром (`0 ≤ u, v < num_vertices`).
  - `edge_id`: необов'язковий вихідний покажчик для збереження присвоєного порядкового номера ребра `[0, num_edges - 1]` (дозволяється передавати `NULL`).
- **Повертані значення:**
  - `PLANAR_OK`: ребро успішно додано.
  - `PLANAR_ERR_INVALID_VERT`: один або обидва індекси вершин виходять за допустимий діапазон.
  - `PLANAR_ERR_EDGE_CAPACITY`: кількість ребер досягла ліміту `max_edges`.
- **Топологічні наслідки:** Створюються два зустрічні напівребра `u -> v` та `v -> u`. Якщо раніше було побудовано вкладення, прапорець `is_embedded` скидається у `false`, вимагаючи повторної перевірки.

## Специфікація функцій топологічного аналізу та вкладення

### `planar_graph_check_planarity`
Виконує детерміновану лінійну перевірку планарності за методом Left-Right DFS.

:::tabs
```c
PlanarResult planar_graph_check_planarity(PlanarGraph* graph, bool* is_planar);
```
```cpp
[[nodiscard]] std::expected<bool, PlanarStatus>
PlanarGraphModel::check_planarity();
```
:::

- **Вхідні параметри:** `graph` — дескриптор аналізованого графа.
- **Вихідні параметри:** `is_planar` — булевий прапорець (`true` — планарний, `false` — непланарний).
- **Часова складність:** `O(V + E)` у найгіршому випадку.
- **Просторова складність:** `O(V)` додаткової пам'яті.
- **Алгоритмічний ланцюг:**
  1. Перевірка формули Ейлера `E ≤ 3V - 6` (відсікання за `O(1)`).
  2. Знаходження точок зчленування та поділ на двозв'язні блоки.
  3. Побудова пальмового дерева DFS та перевірка дворозфарбовуваності графа конфліктів через систему DSU.

### `planar_graph_compute_embedding`
Формує комбінаторну систему ротацій навколо всіх вершин графа.

:::tabs
```c
PlanarResult planar_graph_compute_embedding(PlanarGraph* graph);
```
```cpp
[[nodiscard]] PlanarStatus
PlanarGraphModel::compute_embedding();
```
:::

- **Повертані значення:**
  - `PLANAR_OK`: комбінаторне вкладення побудовано, циклічні перестановки ребер збережено.
  - `PLANAR_NON_PLANAR`: граф непланарний; побудова плоскої карти неможлива.
- **Післяумови:** Заповнено масив `rotation_system`, встановлено прапорець `is_embedded = true`.

### `planar_graph_extract_faces`
Здійснює топологічне трасування замкнених граней за збудованою системою ротацій.

:::tabs
```c
PlanarResult planar_graph_extract_faces(PlanarGraph* graph);
```
```cpp
[[nodiscard]] std::expected<std::vector<FaceRecord>, PlanarStatus>
PlanarGraphModel::extract_faces();
```
:::

- **Повертані значення:**
  - `PLANAR_OK`: усі грані успішно виділено та класифіковано.
  - `PLANAR_ERR_NOT_EMBEDDED`: функцію викликано до `planar_graph_compute_embedding`.
- **Топологічна верифікація:** Функція автоматично перевіряє виконання формули Ейлера: `V - E + F == 1 + k` (де `k` — кількість зв'язних компонент). Якщо баланс порушено, повертається внутрішня помилка алгоритму.

### `planar_graph_get_kuratowski_certificate`
Вилучає точний підграф-свідок непланарності для діагностики відхилень.

:::tabs
```c
PlanarResult planar_graph_get_kuratowski_certificate(PlanarGraph* graph, KuratowskiCertificate* cert);
```
```cpp
[[nodiscard]] std::expected<KuratowskiWitness, PlanarStatus>
PlanarGraphModel::get_kuratowski_certificate();
```
:::

- **Вхідні параметри:** `graph` — дескриптор непланарного графа.
- **Вихідні параметри:** `cert` — структура для збереження координат підрозбиття.
- **Повертані значення:**
  - `PLANAR_OK`: свідок успішно вилучений.
  - `PLANAR_ERR_NO_CERTIFICATE`: граф є планарним, сертифікат відсутній.

## Специфікація функцій геометричного розташування

### `planar_graph_schnyder_layout`
Обчислює цілочисельні координати прямолінійного вкладення Шнайдера на дискретній сітці.

:::tabs
```c
typedef struct PlanarPoint2D {
    int x;
    int y;
} PlanarPoint2D;

PlanarResult planar_graph_schnyder_layout(PlanarGraph* graph, PlanarPoint2D* coords);
```
```cpp
struct Point2D {
    int x{0};
    int y{0};
};

[[nodiscard]] std::expected<std::vector<Point2D>, PlanarStatus>
PlanarGraphModel::compute_schnyder_layout();
```
:::

- **Вхідні параметри:** `graph` — планарна тріангуляція з попередньо обчисленим вкладенням.
- **Вихідні параметри:** `coords` — вихідний масив точок розміром `num_vertices`.
- **Гарантія:** Усі координати лежать у межах `0 ≤ x, y ≤ num_vertices - 2`. Усі ребра малюються прямими неперетинними відрізками.

### `planar_graph_tutte_layout`
Обчислює барицентричне опукле розташування Татта шляхом розв'язання системи рівнянь Лапласа.

:::tabs
```c
typedef struct PlanarFloatPoint2D {
    double x;
    double y;
} PlanarFloatPoint2D;

PlanarResult planar_graph_tutte_layout(PlanarGraph* graph, PlanarFloatPoint2D* coords);
```
```cpp
struct FloatPoint2D {
    double x{0.0};
    double y{0.0};
};

[[nodiscard]] std::expected<std::vector<FloatPoint2D>, PlanarStatus>
PlanarGraphModel::compute_tutte_layout();
```
:::

- **Вхідні параметри:** `graph` — 3-зв'язний планарний граф із побудованим комбінаторним вкладенням.
- **Вихідні параметри:** `coords` — масив дійсних координат у діапазоні `[0.0, 1.0]`.
- **Математичний принцип:** Зовнішня грань фіксується у вершинах правильного опуклого багатокутника на одиничному колі, а внутрішні вершини розміщуються у центрах мас своїх сусідів через розв'язання системи лінійних рівнянь з розрідженою матрицею Кірхгофа (Лапласа) графа методом спряжених градієнтів за час `O(V)`.

### `planar_graph_build_dual`
Генерує комбінаторний двоїстий граф `G*`.

:::tabs
```c
PlanarResult planar_graph_build_dual(const PlanarGraph* primal, PlanarGraph** dual);
```
```cpp
[[nodiscard]] std::expected<std::unique_ptr<PlanarGraphModel>, PlanarStatus>
PlanarGraphModel::build_dual() const;
```
:::

- **Вхідні параметри:** `primal` — вихідний планарний граф із виділеними гранями.
- **Вихідні параметри:** `dual` — адреса для збереження дескриптора двоїстого графа.
- **Топологічні властивості:** Вершини двоїстого графа відповідають граням прямого графа; ребра двоїстого графа сполучають грані, що мають спільні граничні ребра у прямому графі.

## Формати експорту та серіалізації

Бібліотека підтримує інтеграцію із зовнішніми пакетами моделювання та САПР через експорт у стандартизовані текстові формати:

1. **Експорт у формат Graphviz DOT:**
   - Функція серіалізує систему ротацій та координати вершин у директиви `pos="x,y!"`, дозволяючи миттєво рендерити планарні креслення за допомогою утиліти `neato` або `fdp` без додаткових розрахунків.
2. **Експорт у топологічний JSON (GeoJSON / TopoJSON):**
   - Усі грані та зв'язані контури експортуються у вигляді впорядкованих полігональних кілець, що забезпечує пряме завантаження у геоінформаційні платформи (QGIS, ArcGIS, Mapbox) для аналізу територіального розбиття та геодезичних мереж.
3. **Експорт у формат DIMACS / EdgeList:**
   - Для взаємодії із зовнішніми SAT-солверами та пакетами обчислювальної складності підтримується генерація плоских списків ребер без надлишкових метаданих.

## Повний приклад наскрізного використання

Наведений приклад демонструє повний цикл роботи з інтерфейсом: ініціалізацію графа, додавання ребер, лінійну перевірку планарності, побудову комбінаторного вкладення, виділення граней та перевірку формули Ейлера.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

/* Умовний заголовок бібліотеки planar_graph.h */

int main(void) {
    PlanarGraph* g = NULL;
    
    /* Створюємо граф: октаедр (6 вершин, 12 ребер, 8 граней) */
    if (planar_graph_create(&g, 6, 12) != PLANAR_OK) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return EXIT_FAILURE;
    }

    /* Додаємо ребра екваторіального квадрата */
    planar_graph_add_edge(g, 0, 1, NULL);
    planar_graph_add_edge(g, 1, 2, NULL);
    planar_graph_add_edge(g, 2, 3, NULL);
    planar_graph_add_edge(g, 3, 0, NULL);

    /* Додаємо ребра до північного полюса (вершина 4) */
    planar_graph_add_edge(g, 4, 0, NULL);
    planar_graph_add_edge(g, 4, 1, NULL);
    planar_graph_add_edge(g, 4, 2, NULL);
    planar_graph_add_edge(g, 4, 3, NULL);

    /* Додаємо ребра до південного полюса (вершина 5) */
    planar_graph_add_edge(g, 5, 0, NULL);
    planar_graph_add_edge(g, 5, 1, NULL);
    planar_graph_add_edge(g, 5, 2, NULL);
    planar_graph_add_edge(g, 5, 3, NULL);

    /* 1. Лінійна перевірка планарності */
    bool is_planar = false;
    if (planar_graph_check_planarity(g, &is_planar) == PLANAR_OK && is_planar) {
        printf("Граф є планарним!\n");

        /* 2. Побудова комбінаторного вкладення */
        planar_graph_compute_embedding(g);

        /* 3. Виділення граней */
        planar_graph_extract_faces(g);
        printf("Вершин: %d, Ребер: %d, Граней: %d\n",
               g->num_vertices, g->num_edges, g->num_faces);
        printf("Баланс Ейлера V - E + F = %d (очікується 2)\n",
               g->num_vertices - g->num_edges + g->num_faces);
    } else {
        printf("Граф не є планарним!\n");
    }

    /* 4. Звільнення ресурсів */
    planar_graph_destroy(g);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <memory>

int main() {
    // Створюємо граф октаедра (6 вершин)
    auto graph_result = create_planar_graph(6, 12);
    if (!graph_result) {
        std::cerr << "Помилка створення графа\n";
        return 1;
    }

    auto g = std::move(graph_result.value());

    // Екваторіальний контур
    g->add_edge(0, 1);
    g->add_edge(1, 2);
    g->add_edge(2, 3);
    g->add_edge(3, 0);

    // Зв'язки з північним полюсом
    g->add_edge(4, 0);
    g->add_edge(4, 1);
    g->add_edge(4, 2);
    g->add_edge(4, 3);

    // Зв'язки з південним полюсом
    g->add_edge(5, 0);
    g->add_edge(5, 1);
    g->add_edge(5, 2);
    g->add_edge(5, 3);

    // 1. Перевірка планарності
    auto planarity = g->check_planarity();
    if (planarity && *planarity) {
        std::cout << "Граф є планарним!\n";

        // 2. Побудова системи ротацій
        g->compute_embedding();

        // 3. Виділення граней
        auto faces = g->extract_faces();
        if (faces) {
            std::cout << "Вершин: " << g->vertex_count()
                      << ", Ребер: " << g->edge_count()
                      << ", Граней: " << faces->size() << "\n";
            std::cout << "Баланс Ейлера: "
                      << g->vertex_count() - g->edge_count() + faces->size()
                      << " (очікується 2)\n";
        }
    }

    return 0;
}
```
:::

## Обробка граничних та крайових випадків

Програмний інтерфейс спроектовано з урахуванням складних комбінаторних аномалій, що виникають у реальних графових наборах даних:

1. **Ізольовані вершини та незв'язні компоненти:**
   - Якщо граф містить декілька незв'язаних компонент (`k > 1`), кожна компонента вкладається незалежно.
   - Усі компоненти мають спільну необмежену зовнішню грань `f_ext`.
   - Функція `extract_faces` автоматично застосовує модифіковану формулу Ейлера `V - E + F = 1 + k`.
2. **Мости (істмуси, що розділяють одну й ту саму грань):**
   - Якщо ребро `e = (u, v)` є мостом (його видалення збільшує кількість зв'язних компонент), воно омивається однією гранню з обох боків.
   - У структурі DCEL напівребра `h` та `h.twin` отримують однаковий ідентифікатор грані `h.face == h.twin.face`, а в периметр цієї грані міст входить двічі.
3. **Вершини з петлями та кратними ребрами:**
   - Петля `(u, u)` створює внутрішню однореберну грань та зовнішнє огинаюче напівребро.
   - Дві паралельні дуги між `u` та `v` утворюють внутрішню двореберну грань (`deg(f) = 2`).
4. **Великі розріджені графи (`V > 10⁶`):**
   - Для запобігання переповненню системного стека глибинний обхід всередині `check_planarity` використовує динамічний стек у купі, якщо глибина рекурсії перевищує 8192 рівні.

## Правила безпеки пам'яті та багатопоточності

- **Політика володіння пам'яттю (Ownership Model):**
  - У C-інтерфейсі пам'ять виділяється функцією `planar_graph_create` і повністю звільняється викликом `planar_graph_destroy`.
  - Усі внутрішні масиви напівребер, граней та системи ротацій належать структурі `PlanarGraph` і не повинні звільнятися користувачем окремо.
  - У C++ інтерфейсі керування ресурсами реалізовано через семантику переміщення (`std::unique_ptr`), що гарантує відсутність подвійного звільнення або витоків.
- **Ниткобезпечність (Thread-Safety):**
  - Операції тільки для читання (перевірка планарності незмінного графа, обхід граней, обчислення координат) є безпечними для одночасного виклику з декількох потоків над одним спільним екземпляром дескриптора.
  - Модифікації структури (додавання ребер, побудова нового вкладення) не є потокобезпечними і вимагають зовнішньої синхронізації (м'ютексів).
- **Обробка винятків у C++:** Жоден метод класу `PlanarGraphModel` не генерує неперехоплених винятків; усі помилкові стани повертаються явно через тип `std::expected` з кодом `PlanarStatus`.
