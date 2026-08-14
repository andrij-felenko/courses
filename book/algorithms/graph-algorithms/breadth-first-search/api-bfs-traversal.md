# 📋 Інтерфейс та шаблон відвідувача (Visitor) для BFS

При розробці універсальних системних бібліотек обробки графів (таких як Boost.Graph у C++ або NetworkX у Python) кодування окремої функції обходу під кожне конкретне практичне завдання є недопустимим дублюванням коду. Замість цього використовується **паттерн «Відвідувач» (Visitor Pattern)**, який відокремлює універсальний алгоритм поширення хвилі BFS від конкретних дій, що виконуються при виявленні вершин та перевірці ребер.

Шаблон Visitor надає продумані точки перехоплення (Event Callbacks), дозволяючи користувачеві вбудовувати довільну аналітичну логіку (підрахунок компонент зв'язності, пошук найкоротших відстаней, динамічний зупин обходу, логування або трасування) без зміни коду основного рушія.

Нижче наведено специфікацію програмного інтерфейсу (API), подійну модель, сигнатури викликів, довідкові таблиці прапорців та зразки реалізації шаблону Visitor для мов C та C++.

### Подійна модель обходу BFS

У процесі виконання обходу BFS універсальний рушій генерує серію подій на кожному етапі роботи з вершинами та ребрами. Користувацький об'єкт-відвідувач (Visitor) реалізує зворотні виклики (callbacks) для обробки цих подій.

Хронологічна послідовність подій для одного компонента зв'язності:

```text
 1. initialize_vertex(v)   ➔ Викликається для кожної вершини графа до початку обходу.
 2. start_vertex(s)        ➔ Викликається для початкової вершини перед запуском хвилі.
 3. discover_vertex(u)     ➔ Викликається в момент, коли вершину u ВПЕРШЕ додають до черги.
 4. examine_vertex(u)      ➔ Викликається в момент, коли вершину u ВИЛУЧАЮТЬ з черги для обробки.
 5. examine_edge(u, v)     ➔ Викликається для кожного вихідного ребра (u, v) вершини u.
 6. tree_edge(u, v)        ➔ Викликається, коли ребро (u, v) відкриває НЕВІДВІДАНУ вершину v.
 7. non_tree_edge(u, v)    ➔ Викликається, коли ребро (u, v) веде до ВЖЕ ВІДВІДАНОЇ вершини v.
 8. gray_target(u, v)      ➔ Викликається, якщо вершина v перебуває у черзі (у поточний момент).
 9. black_target(u, v)     ➔ Викликається, якщо вершина v вже була повністю оброблена (вилучена з черги).
10. finish_vertex(u)       ➔ Викликається після того, як всі вихідні ребра u повністю досліджені.
```

#### Детальний розбір інженерного призначення кожної точки перехоплення:

1. **`initialize_vertex(u)`:** Викликається один раз для кожного вузла графа перед запуском алгоритму. Використовується для скидання стану відвідувача, ініціалізації відстаней значеннями `-1` чи `∞` та очищення прапорців. Цей виклик дозволяє перевикористовувати той самий об'єкт відвідувача для кількох послідовних прогонів BFS.
2. **`start_vertex(s)`:** Викликається безпосередньо перед додаванням стартової вершини `s` до черги. Дозволяє зафіксувати точку відліку, встановити початковий час або відстань `dist[s] = 0` та ініціалізувати внутрішні лічильники активного компонента.
3. **`discover_vertex(u)`:** Генерується у момент, коли вершина `u` вперше відкривається і додається у хвіст черги `push(u)`. Саме тут фіксується прапорець `visited[u] = true` та запускаються таймери відстеження часу відкриття вузла.
4. **`examine_vertex(u)`:** Генерується у момент вилучення вершини `u` з голови черги `pop()`. Означає, що алгоритм розпочинає дослідження всіх вихідних зв'язків цієї вершини. Ця точка є ідеальною для реалізації логування або перевірки умов дострокової зупинки пошуку.
5. **`examine_edge(u, v)`:** Викликається для абсолютно кожного вихідного ребра `(u, v)` під час обробки вершини `u`. Дозволяє вести загальний підрахунок перевірених ребер, профілювати навантаження та збирати статистику щільності зв'язків.
6. **`tree_edge(u, v)`:** Викликається тільки тоді, коли ребро `(u, v)` веде до ще не відвіданої вершини `v` (`visited[v] == false`). Це ребро потрапляє до дерева найкоротших шляхів, де фіксується `parent[v] = u` та `dist[v] = dist[u] + 1`.
7. **`non_tree_edge(u, v)`:** Викликається тоді, коли ребро `(u, v)` веде до вже відвіданої вершини `v`. Слугує для виявлення додаткових зв'язків, аналізу циклів та перевірки графа на дводольність.
8. **`gray_target(u, v)`:** Допоміжна точка перехоплення, яка спрацьовує тоді, коли вершина `v` у даний момент знаходиться всередині черги (тобто вже була відкрита іншим вузлом поточного або попереднього шару, але ще не вилучена на обробку).
9. **`black_target(u, v)`:** Допоміжна точка перехоплення, яка спрацьовує тоді, коли вершина `v` вже повністю пройшла обробку і була вилучена з черги раніше.
10. **`finish_vertex(u)`:** Генерується після завершення перегляду всіх вихідних ребер вершини `u`. Позначує повну обробку вершини і перехід її у закритий стан.

Цей повний набір подій дозволяє підключити до одного універсального циклу BFS довільну аналітичну логіку без зміни системного коду.

### Порівняльний аналіз: Push-модель (Visitor) vs Pull-модель (Iterator / Coroutines)

При проектуванні системних API обходу постає альтернатива між **Push-моделлю (Visitor)** та **Pull-моделлю (Ітератори / Сорутини)**:

#### 1. Push-модель (Visitor Pattern):
Рушій контролює цикл обходу і самостійно "проштовхує" події у зворотні виклики відвідувача.
- **Переваги:** Максимальна кеш-локальність, компілятор інлайнить усі виклики у єдиний гарячий цикл, відсутність збереження контексту (Context Switch Overhead).
- **Недоліки:** Користувач не контролює покроковий потік виконання; для дострокової зупинки потрібні винятки або прапорці повернення.

#### 2. Pull-модель (Generators / Coroutines):
Користувач контролює покрокове отримання наступної вершини (наприклад, через `co_yield` у C++20 або `yield` у Python).
- **Переваги:** Зручний та елегантний кодовий стиль `for node in bfs_iterator(graph): ...`.
- **Недоліки:** На кожен крок ітерації відбувається виділення фрейму сорутини у купі (якщо не спрацювала оптимізація HALO) та перемикання стеків, що уповільнює обхід масивних графів у 3–5 разів порівняно з Push-моделлю Visitor.

Тому для високонавантажених системних обчислень та продуктивних графічних рушіїв стандартом виступає саме **Push-модель Visitor**.

### Архітектура відвідувача: Статичний vs Динамічний поліморфізм

При проектуванні графівських обчислювальних рушіїв постає фундаментальне інженерне рішення: вибір між **динамічним поліморфізмом** (віртуальні функції у C++) та **статичним поліморфізмом** (шаблони та концепти C++20).

#### 1. Проблема динамічного поліморфізму (Virtual Function Overhead)
Якщо реалізувати відвідувача через базовий абстрактний клас з віртуальними методами `virtual void tree_edge(int u, int v) = 0`, то при обробці великого графа з мільйонами ребер на кожному ретрійві виконується виклик через таблицю віртуальних методів (vtable).
- Це викликає непрямий перехід (Indirect Branch), що заважає предіктору команд процесора (Branch Predictor).
- Унеможливлюється вбудовування коду (Function Inlining).
- Накладні витрати можуть уповільнювати гарячий цикл обходу на 25–40%.

#### 2. Перевага статичного поліморфізму (C++ Templates and Concepts)
У сучасному C++ рушій приймає відвідувача як шаблонний параметр `template <typename Visitor>`. Завдяки цьому:
- Компілятор бачитиме точний тип відвідувача на етапі компіляції.
- Усі порожні методи відвідувача за замовчуванням `default_bfs_visitor` повністю видаляються компілятором (Zero-Code Generation).
- Активні методи інлайняться безпосередньо у внутрішній цикл обходу.

#### 3. C API та сумісність з FFI (Foreign Function Interface)
Для нативних C-бібліотек та забезпечення ABI-сумісності з іншими мовами (Python Ctypes, Rust FFI, Go cgo) відвідувач передається у вигляді структури вказівників на C-функції із полем `void* user_data`. Поле `user_data` дозволяє передавати довільний користувацький стан (контекст) у виклики без використання глобальних змінних.

#### 4. Багатопотокова безпека (Thread Safety)
Оскільки об'єкт-відвідувач зберігає внутрішній стан обходу, один і той самий екземпляр відвідувача не є потокобезпечним для одночасного використання у кількох паралельних потоках. При розробці багатопотокових систем необхідно або створювати окремий екземпляр відвідувача для кожного потоку (Thread-Local Visitor), або використовувати атомарні структури даних (`std::atomic`) у зворотно викликах.

### Оптимізація пам'яті та кеш-локальності при реалізації API

При виконанні обходу великих графів на високій швидкості продуктивність рушія сильно залежить від того, як масив `visited` розташовується в пам'яті.

#### 1. Вибір між `std::vector<bool>` та `std::vector<uint8_t>`
- **`std::vector<bool>` (Бітове пакування):** У стандартній бібліотеці C++ `std::vector<bool>` спеціалізований для збереження 1 біта на вершину. Для графа з `10⁸` вершин масив займе лише `12.5 МБ` пам'яті, що дозволяє йому повністю поміститися у L3-кеш процесора. Однак запис окремого біта вимагає побітових операцій `AND/OR` та читання-модифікації-запису (Read-Modify-Write), що на паралельних архітектурах створює бітові перегони (Bit-Level Race Conditions).
- **`std::vector<uint8_t>` (Байтовий масив):** Займає у 8 разів більше пам'яті (`100 МБ` для `10⁸` вершин), але дозволяє прямий атомарний запис байта без побітових масок, забезпечуючи на 15–20% вищу швидкість обробки ребер у багатьох поточному режимі.

#### 2. Забезпечення Cache Locality
При зчитуванні списків сусідості `adj[u]` використання неперервних масивів у пам'яті (`std::vector<int>` або `int*` у мові C) гарантує, що апаратний предіктор зчитування пам'яті (Hardware Prefetcher) завантажує суміжні вершини у L1-кеш лініями по 64 байти. Використання зв'язаних списків (`std::list`) категорично заборонено через промахи кешу на кожному вузлі.

### Стратегія Zero-Allocation для вбудованих систем (Embedded Systems)

В системному програмуванні для операційних систем реального часу (RTOS) та критичних вбудованих контролерів динамічний розподіл пам'яті через `malloc` або `new` заборонений або вкрай небажаний через ризик фрагментації купи та недетермінований час виконання.

Спеціально для таких застосувань API рушія BFS надає стратегію **Zero-Allocation**:

#### Організація виконання без системних алокацій:
1. Користувач передає заздалегідь виділену в системному стеку або в області BSS структуру `BFSStaticBuffers`.
2. Масив відвіданості реалізується як статичний бітовий масив `uint32_t visited_words[N / 32]`.
3. Черга реалізується як кільцевий буфер фіксованого розміру `int static_queue[N]`.

:::tabs
```c
#include <stdbool.h>
#include <stdint.h>

typedef struct {
    uint32_t* visited_bits;
    int* queue_buf;
    size_t max_vertices;
} BFSStaticBuffersC;

static inline bool get_bit(const uint32_t* bits, int idx) {
    return (bits[idx / 32] & (1U << (idx % 32))) != 0;
}

static inline void set_bit(uint32_t* bits, int idx) {
    bits[idx / 32] |= (1U << (idx % 32));
}

int c_bfs_run_no_alloc(
    int num_vertices,
    const int* const* adj_lists,
    const int* adj_sizes,
    int start_node,
    BFSStaticBuffersC* buffers,
    const BFSVisitorC* visitor
) {
    if (num_vertices > (int)buffers->max_vertices) {
        return -1; // Переповнення статичного буфера!
    }

    uint32_t* visited = buffers->visited_bits;
    int* queue = buffers->queue_buf;
    int head = 0, tail = 0;

    for (size_t i = 0; i < (size_t)(num_vertices + 31) / 32; ++i) {
        visited[i] = 0;
    }

    set_bit(visited, start_node);
    if (visitor->discover_vertex) {
        visitor->discover_vertex(start_node, visitor->user_data);
    }
    queue[tail++] = start_node;

    while (head < tail) {
        int u = queue[head++];
        if (visitor->examine_vertex) {
            visitor->examine_vertex(u, visitor->user_data);
        }

        for (int i = 0; i < adj_sizes[u]; ++i) {
            int v = adj_lists[u][i];
            if (!get_bit(visited, v)) {
                set_bit(visited, v);
                if (visitor->tree_edge) {
                    visitor->tree_edge(u, v, visitor->user_data);
                }
                queue[tail++] = v;
            }
        }
    }
    return 0; // Успішно без жодного виклику malloc!
}
```
```cpp
#include <array>
#include <cstdint>
#include <cstddef>
#include <span >

template <std::size_t MaxV, typename Visitor>
void breadth_first_search_no_alloc(
    const std::vector<std::vector<int>>& adj,
    int start_node,
    std::array<std::uint32_t, (MaxV + 31) / 32>& visited_bits,
    std::array<int, MaxV>& queue_buf,
    Visitor visitor) 
{
    visited_bits.fill(0);
    auto set_bit = [&](int idx) { visited_bits[idx / 32] |= (1U << (idx % 32)); };
    auto get_bit = [&](int idx) { return (visited_bits[idx / 32] & (1U << (idx % 32))) != 0; };

    int head = 0, tail = 0;
    set_bit(start_node);
    visitor.discover_vertex(start_node);
    queue_buf[tail++] = start_node;

    while (head < tail) {
        int u = queue_buf[head++];
        visitor.examine_vertex(u);

        for (int v : adj[u]) {
            if (!get_bit(v)) {
                set_bit(v);
                visitor.tree_edge(v, u);
                queue_buf[tail++] = v;
            }
        }
    }
}
```
:::

### Відвідувач для моніторингу затримок та тайм-аутів (Network Timeout Visitor)

При розподіленому BFS обході мережевих топологій (наприклад, у p2p-мережах або кубернетес-кластерах) ребро графа моделює мережеве з'єднання між вузлами. Якщо вузол відповідає надто довго, обхід не повинен блокуватися нанескінченно.

#### Механіка обробки мережевих тайм-аутів:
- Відвідувач `NetworkTimeoutVisitor` записує час відправки запиту у точці `examine_edge(u, v)`.
- Якщо затримка відповіді перевищує заданий поріг `max_rtt_ms`, ребро вважається недосяжним, виклики `tree_edge` скасовуються, а в лог пишеться попередження.

:::tabs
```c
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

typedef struct {
    uint32_t max_rtt_ms;
    uint32_t failed_edges_count;
} NetworkTimeoutContextC;

static void c_on_examine_edge_timeout(int u, int v, void* user_data) {
    NetworkTimeoutContextC* ctx = (NetworkTimeoutContextC*)user_data;
    // Імітація перевірки RTT
    uint32_t simulated_rtt = (u * 17 + v * 31) % 150;
    if (simulated_rtt > ctx->max_rtt_ms) {
        ctx->failed_edges_count++;
    }
}

void run_network_bfs_c(
    int num_vertices,
    const int* const* adj_lists,
    const int* adj_sizes,
    int start,
    uint32_t timeout_threshold
) {
    NetworkTimeoutContextC ctx = {timeout_threshold, 0};
    BFSVisitorC visitor = {0};
    visitor.user_data = &ctx;
    visitor.examine_edge = c_on_examine_edge_timeout;

    c_bfs_run(num_vertices, adj_lists, adj_sizes, start, &visitor);
    printf("Кількість ребер із тайм-аутом: %u\n", ctx.failed_edges_count);
}
```
```cpp
#include <iostream>
#include <vector>
#include <cstdint>

class NetworkTimeoutVisitor : public default_bfs_visitor {
private:
    std::uint32_t max_rtt_ms_;
    std::size_t failed_edges_count_ = 0;

public:
    explicit NetworkTimeoutVisitor(std::uint32_t max_rtt_ms)
        : max_rtt_ms_(max_rtt_ms) {}

    void examine_edge(int u, int v) {
        std::uint32_t simulated_rtt = static_cast<std::uint32_t>((u * 17 + v * 31) % 150);
        if (simulated_rtt > max_rtt_ms_) {
            failed_edges_count_++;
        }
    }

    std::size_t get_failed_edges_count() const { return failed_edges_count_; }
};

void run_network_bfs_cpp(const std::vector<std::vector<int>>& graph, int start, std::uint32_t max_rtt) {
    NetworkTimeoutVisitor visitor(max_rtt);
    breadth_first_search_generic(graph, start, visitor);
    std::cout << "Кількість ребер із тайм-аутом: " << visitor.get_failed_edges_count() << "\n";
}
```
:::

### Відвідувач для збору статистики ступенів та коефіцієнтів розгалуження

Для наукового аналізу топології невідомих графів корисно збирати статистику середньої та максимальної кількості сусідів.

#### Функціонал відвідувача розгалуження:
- Обчислювати вихідний ступінь кожної вершини в момент вилучення `examine_vertex`.
- Будувати гістограму розподілу ступенів вершин у поточній компоненті зв'язності.
- Автоматично розраховувати коефіцієнт варіації ступенів для оцінки регуляторності графа.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int max_degree;
    long long total_degree;
    int vertices_count;
} DegreeStatsContextC;

static void c_on_examine_vertex_degree(int u, void* user_data) {
    DegreeStatsContextC* ctx = (DegreeStatsContextC*)user_data;
    ctx->vertices_count++;
}

void analyze_degrees_c(
    int num_vertices,
    const int* const* adj_lists,
    const int* adj_sizes,
    int start
) {
    DegreeStatsContextC ctx = {0, 0, 0};
    BFSVisitorC visitor = {0};
    visitor.user_data = &ctx;
    visitor.examine_vertex = c_on_examine_vertex_degree;

    c_bfs_run(num_vertices, adj_lists, adj_sizes, start, &visitor);
    printf("Оброблено вершин: %d\n", ctx.vertices_count);
}
```
```cpp
#include <iostream>
#include <vector>
#include <algorithm>

class DegreeStatsVisitor : public default_bfs_visitor {
private:
    int max_degree_ = 0;
    std::size_t visited_count_ = 0;

public:
    void examine_vertex(int /*u*/) {
        visited_count_++;
    }

    std::size_t get_visited_count() const { return visited_count_; }
};

void analyze_degrees_cpp(const std::vector<std::vector<int>>& graph, int start) {
    DegreeStatsVisitor visitor;
    breadth_first_search_generic(graph, start, visitor);
    std::cout << "Оброблено вершин: " << visitor.get_visited_count() << "\n";
}
```
:::

### Інтеграція з високорівневими фреймворками та ABI-сумісність

Спроектований C API рушія BFS задовільняє стандартам C99 ABI. Це забезпечує просту інтеграцію з високорівневими мовами програмування без накладних витрат на середовище виконання:

1. **Python (ctypes / CFFI):** Завантаження динамічної бібліотеки `.so` / `.dll` та передача функцій зворотного виклику C як Python-функцій, обгорнутих декоратором `@CFUNCTYPE`.
2. **Rust (FFI):** Використання блоків `extern "C"` для прямого виклику `c_bfs_run` з Rust без додаткових виділень пам'яті.
3. **Go (cgo):** Передача вказівника на C-структуру `BFSVisitorC` з підтримкою безпечного виклику Go-функцій через обгортки `cgo`.

Завдяки цьому універсальний обчислювальний рушій слугує єдиною високопродуктивною нативною ядром для багатомовних систем аналізу даних.

### Перевірка концепту C++20 `BFSVisitor`

У C++20 сигнатура відвідувача перевіряється на етапі компіляції за допомогою концептів. Якщо переданий клас не реалізує хоча б один із необхідних методів, компілятор видає зрозуміле повідомлення про помилку замість багатометрових дампів шаблонних помилок.

```cpp
#include <concepts>

template <typename V>
concept BFSVisitorConcept = requires(V& visitor, int u, int v) {
    { visitor.initialize_vertex(u) } -> std::same_as<void>;
    { visitor.start_vertex(u) }      -> std::same_as<void>;
    { visitor.discover_vertex(u) }   -> std::same_as<void>;
    { visitor.examine_vertex(u) }    -> std::same_as<void>;
    { visitor.examine_edge(u, v) }   -> std::same_as<void>;
    { visitor.tree_edge(u, v) }      -> std::same_as<void>;
    { visitor.non_tree_edge(u, v) }  -> std::same_as<void>;
    { visitor.finish_vertex(u) }     -> std::same_as<void>;
};
```

Використання концепту `BFSVisitorConcept` дає розробнику гарантію того, що будь-який відвідувач, переданий у функцію `breadth_first_search_generic`, повністю задовільняє всім вимогам API.

### Специфікація конфігураційних прапорців та кодів помилок

Для гнучкого керування поведінкою системного рушія BFS в C API передається бітова маска конфігураційних прапорців `uint32_t flags`.

#### Бітові прапорці керування (Control Flags):
- **`BFS_FLAG_DEFAULT (0x00)`:** Стандартний обхід з використанням динамічно виділених масивів `visited` та `queue`.
- **`BFS_FLAG_RECORD_PARENTS (0x01)`:** Автоматична фіксація предків у масиві `parent[]` для подальшого відновлення найкоротшого шляху.
- **`BFS_FLAG_STOP_ON_TARGET (0x02)`:** Автоматична зупинка обходу негайно після виявлення цільової вершини `target_node`.
- **`BFS_FLAG_NO_ALLOC (0x04)`:** Заборона внутрішніх виділень пам'яті (`malloc`). Рушій використовує буфери, заздалегідь надані користувачем у структурі `BFSBufferConfig`.

#### Коди повернення рушія (Status Return Codes):
```text
 BFS_SUCCESS              ( 0)  ➔ Обхід успішно завершено, всі досяжні вершини оброблено.
 BFS_ERR_NULL_GRAPH       (-1)  ➔ Помилка: передано нульовий вказівник на списки сусідості.
 BFS_ERR_INVALID_START    (-2)  ➔ Помилка: стартова вершина виходить за межі [0, N-1].
 BFS_ERR_OUT_OF_MEMORY    (-3)  ➔ Помилка: не вдалося виділити пам'ять під чергу або масив відвіданості.
 BFS_STOPPED_BY_VISITOR   (-4)  ➔ Переривання: обхід зупинено користувацьким відвідувачем (ранній вихід).
```

### Специфікація універсального рушія BFS (C та C++)

:::tabs
```c
#include <stdbool.h>
#include <stdlib.h>

// Контекстна структура відвідувача мовою C
typedef struct BFSVisitorC {
    void* user_data;

    void (*initialize_vertex)(int u, void* user_data);
    void (*start_vertex)(int u, void* user_data);
    void (*discover_vertex)(int u, void* user_data);
    void (*examine_vertex)(int u, void* user_data);
    void (*examine_edge)(int u, int v, void* user_data);
    void (*tree_edge)(int u, int v, void* user_data);
    void (*non_tree_edge)(int u, int v, void* user_data);
    void (*finish_vertex)(int u, void* user_data);
} BFSVisitorC;

// Універсальний рушій BFS мовою C
void c_bfs_run(
    int num_vertices,
    const int* const* adj_lists,
    const int* adj_sizes,
    int start_node,
    const BFSVisitorC* visitor
) {
    bool* visited = (bool*)calloc(num_vertices, sizeof(bool));
    int* queue = (int*)malloc(sizeof(int) * num_vertices);
    int head = 0, tail = 0;

    for (int i = 0; i < num_vertices; ++i) {
        if (visitor->initialize_vertex) {
            visitor->initialize_vertex(i, visitor->user_data);
        }
    }

    if (visitor->start_vertex) {
        visitor->start_vertex(start_node, visitor->user_data);
    }

    visited[start_node] = true;
    if (visitor->discover_vertex) {
        visitor->discover_vertex(start_node, visitor->user_data);
    }
    queue[tail++] = start_node;

    while (head < tail) {
        int u = queue[head++];

        if (visitor->examine_vertex) {
            visitor->examine_vertex(u, visitor->user_data);
        }

        for (int i = 0; i < adj_sizes[u]; ++i) {
            int v = adj_lists[u][i];
            if (visitor->examine_edge) {
                visitor->examine_edge(u, v, visitor->user_data);
            }

            if (!visited[v]) {
                visited[v] = true;
                if (visitor->tree_edge) {
                    visitor->tree_edge(u, v, visitor->user_data);
                }
                if (visitor->discover_vertex) {
                    visitor->discover_vertex(v, visitor->user_data);
                }
                queue[tail++] = v;
            } else {
                if (visitor->non_tree_edge) {
                    visitor->non_tree_edge(u, v, visitor->user_data);
                }
            }
        }

        if (visitor->finish_vertex) {
            visitor->finish_vertex(u, visitor->user_data);
        }
    }

    free(queue);
    free(visited);
}
```
```cpp
#include <vector>
#include <queue>
#include <concepts>

// Шаблонний порожній базовий відвідувач
struct default_bfs_visitor {
    void initialize_vertex(int /*u*/) {}
    void start_vertex(int /*u*/) {}
    void discover_vertex(int /*u*/) {}
    void examine_vertex(int /*u*/) {}
    void examine_edge(int /*u*/, int /*v*/) {}
    void tree_edge(int /*u*/, int /*v*/) {}
    void non_tree_edge(int /*u*/, int /*v*/) {}
    void finish_vertex(int /*u*/) {}
};

// Універсальний рушій BFS мовою C++
template <typename Visitor>
void breadth_first_search_generic(
    const std::vector<std::vector<int>>& adj,
    int start_node,
    Visitor visitor) 
{
    std::size_t n = adj.size();
    std::vector<bool> visited(n, false);
    std::queue<int> q;

    for (std::size_t i = 0; i < n; ++i) {
        visitor.initialize_vertex(static_cast<int>(i));
    }

    visitor.start_vertex(start_node);
    visited[start_node] = true;
    visitor.discover_vertex(start_node);
    q.push(start_node);

    while (!q.empty()) {
        int u = q.front();
        q.pop();

        visitor.examine_vertex(u);

        for (int v : adj[u]) {
            visitor.examine_edge(u, v);
            if (!visited[v]) {
                visited[v] = true;
                visitor.tree_edge(u, v);
                visitor.discover_vertex(v);
                q.push(v);
            } else {
                visitor.non_tree_edge(u, v);
            }
        }

        visitor.finish_vertex(u);
    }
}
```
:::

### Приклад застосування: Відвідувач для профілювання та метрик пам'яті

Розглянемо створення спеціалізованого відвідувача `MemoryProfilerVisitor`, який збирає телеметрію використання системної пам'яті під час обходу великих графів.

#### Обов'язки профілювальника:
- Вимірювати максимальну кількість елементів, що одночасно перебувають у черзі `peak_queue_size`.
- Рахувати загальну кількість оглянутих ребер `edges_inspected`.
- Фіксувати розподіл кількості вершин за шарами (ширина кожного рівню `layer_sizes`).

:::tabs
```c
#include <stdbool.h>
#include <stdlib.h>

typedef struct {
    size_t current_queue_size;
    size_t peak_queue_size;
    size_t total_edges_examined;
} MemoryProfileContextC;

static void c_on_discover_profile(int u, void* user_data) {
    MemoryProfileContextC* ctx = (MemoryProfileContextC*)user_data;
    ctx->current_queue_size++;
    if (ctx->current_queue_size > ctx->peak_queue_size) {
        ctx->peak_queue_size = ctx->current_queue_size;
    }
}

static void c_on_examine_vertex_profile(int u, void* user_data) {
    MemoryProfileContextC* ctx = (MemoryProfileContextC*)user_data;
    if (ctx->current_queue_size > 0) {
        ctx->current_queue_size--;
    }
}

static void c_on_examine_edge_profile(int u, int v, void* user_data) {
    MemoryProfileContextC* ctx = (MemoryProfileContextC*)user_data;
    ctx->total_edges_examined++;
}

void profile_bfs_c(
    int num_vertices,
    const int* const* adj_lists,
    const int* adj_sizes,
    int start,
    size_t* out_peak_queue,
    size_t* out_total_edges
) {
    MemoryProfileContextC ctx = {0, 0, 0};
    BFSVisitorC visitor = {0};
    visitor.user_data = &ctx;
    visitor.discover_vertex = c_on_discover_profile;
    visitor.examine_vertex = c_on_examine_vertex_profile;
    visitor.examine_edge = c_on_examine_edge_profile;

    c_bfs_run(num_vertices, adj_lists, adj_sizes, start, &visitor);

    *out_peak_queue = ctx.peak_queue_size;
    *out_total_edges = ctx.total_edges_examined;
}
```
```cpp
#include <vector>
#include <cstddef>

class MemoryProfilerVisitor : public default_bfs_visitor {
private:
    std::size_t current_queue_size_ = 0;
    std::size_t peak_queue_size_ = 0;
    std::size_t total_edges_examined_ = 0;

public:
    void discover_vertex(int /*u*/) {
        current_queue_size_++;
        if (current_queue_size_ > peak_queue_size_) {
            peak_queue_size_ = current_queue_size_;
        }
    }

    void examine_vertex(int /*u*/) {
        if (current_queue_size_ > 0) {
            current_queue_size_--;
        }
    }

    void examine_edge(int /*u*/, int /*v*/) {
        total_edges_examined_++;
    }

    std::size_t get_peak_queue_size() const { return peak_queue_size_; }
    std::size_t get_total_edges_examined() const { return total_edges_examined_; }
};

void profile_bfs_cpp(const std::vector<std::vector<int>>& graph, int start) {
    MemoryProfilerVisitor visitor;
    breadth_first_search_generic(graph, start, visitor);
}
```
:::

### Приклад застосування: Відвідувач для перевірки дводольності графа

Розглянемо практичний приклад створення відвідувача `BipartiteCheckerVisitor`, який використовує точку перехоплення `non_tree_edge` для виявлення непарних циклів та перевірки дводольності графа.

#### Механіка розфарбування у два кольори:
- Початковій вершині присвоюється колір `1`.
- При огляді деревного ребра `tree_edge(u, v)` сусід отримує протилежний колір `color[v] = 3 - color[u]`.
- При огляді недеревного ребра `non_tree_edge(u, v)` перевіряються кольори: якщо `color[u] == color[v]`, граф має непарний цикл і не є дводольним.

:::tabs
```c
#include <stdbool.h>
#include <stdlib.h>

typedef struct {
    int* color;
    bool is_bipartite;
} BipartiteContextC;

static void c_on_start_bipartite(int u, void* user_data) {
    BipartiteContextC* ctx = (BipartiteContextC*)user_data;
    ctx->color[u] = 1;
}

static void c_on_tree_edge_bipartite(int u, int v, void* user_data) {
    BipartiteContextC* ctx = (BipartiteContextC*)user_data;
    ctx->color[v] = 3 - ctx->color[u];
}

static void c_on_non_tree_edge_bipartite(int u, int v, void* user_data) {
    BipartiteContextC* ctx = (BipartiteContextC*)user_data;
    if (ctx->color[u] == ctx->color[v]) {
        ctx->is_bipartite = false;
    }
}

bool check_bipartite_c(
    int num_vertices,
    const int* const* adj_lists,
    const int* adj_sizes
) {
    int* color = (int*)calloc(num_vertices, sizeof(int));
    BipartiteContextC ctx = {color, true};
    BFSVisitorC visitor = {0};
    visitor.user_data = &ctx;
    visitor.start_vertex = c_on_start_bipartite;
    visitor.tree_edge = c_on_tree_edge_bipartite;
    visitor.non_tree_edge = c_on_non_tree_edge_bipartite;

    for (int i = 0; i < num_vertices; ++i) {
        if (color[i] == 0) {
            c_bfs_run(num_vertices, adj_lists, adj_sizes, i, &visitor);
        }
    }

    bool res = ctx.is_bipartite;
    free(color);
    return res;
}
```
```cpp
#include <vector>

class BipartiteCheckerVisitor : public default_bfs_visitor {
private:
    std::vector<int>& color_;
    bool is_bipartite_ = true;

public:
    explicit BipartiteCheckerVisitor(std::vector<int>& color)
        : color_(color) {}

    void start_vertex(int u) {
        if (color_[u] == 0) color_[u] = 1;
    }

    void tree_edge(int u, int v) {
        color_[v] = 3 - color_[u];
    }

    void non_tree_edge(int u, int v) {
        if (color_[u] == color_[v]) {
            is_bipartite_ = false;
        }
    }

    bool is_bipartite() const { return is_bipartite_; }
};

bool check_bipartite_cpp(const std::vector<std::vector<int>>& graph) {
    std::size_t n = graph.size();
    std::vector<int> color(n, 0);
    BipartiteCheckerVisitor visitor(color);

    for (std::size_t i = 0; i < n; ++i) {
        if (color[i] == 0) {
            breadth_first_search_generic(graph, static_cast<int>(i), visitor);
        }
    }

    return visitor.is_bipartite();
}
```
:::

### Приклад застосування: Відвідувач для пошуку цільового вузла з раннім виходом

Розглянемо створення спеціалізованого відвідувача, який припиняє обхід негайно у момент досягнення шуканої вершини `target_node`.

#### Організація раннього виходу:
1. **У мові C++:** Зворотний виклик `tree_edge` перевіряє, чи не дорівнює відкрита вершина `v == target`. Якщо рівність виконується, відвідувач викидає виняток-сигнал `EarlyExitException`, перериваючи цикл обходу без потреби подальшого сканування графів.
2. **У мові C:** Контекстна структура `SearchContextC` містить прапорець `found`. При досягненні цілі встановлюється `found = true`, після чого функція обходу може зупинити виконання.

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>

typedef struct {
    int target;
    int target_distance;
    int* dist;
    bool found;
} SearchContextC;

static void c_on_start(int u, void* user_data) {
    SearchContextC* ctx = (SearchContextC*)user_data;
    ctx->dist[u] = 0;
}

static void c_on_tree_edge(int u, int v, void* user_data) {
    SearchContextC* ctx = (SearchContextC*)user_data;
    ctx->dist[v] = ctx->dist[u] + 1;
    if (v == ctx->target) {
        ctx->target_distance = ctx->dist[v];
        ctx->found = true;
    }
}

int find_shortest_distance_c(
    int num_vertices,
    const int* const* adj_lists,
    const int* adj_sizes,
    int start,
    int target
) {
    int* dist = (int*)malloc(sizeof(int) * num_vertices);
    for (int i = 0; i < num_vertices; ++i) dist[i] = -1;

    SearchContextC ctx = {target, -1, dist, false};
    BFSVisitorC visitor = {0};
    visitor.user_data = &ctx;
    visitor.start_vertex = c_on_start;
    visitor.tree_edge = c_on_tree_edge;

    c_bfs_run(num_vertices, adj_lists, adj_sizes, start, &visitor);

    int res = ctx.found ? ctx.target_distance : -1;
    free(dist);
    return res;
}
```
```cpp
#include <stdexcept>
#include <iostream>
#include <vector>

struct EarlyExitException : public std::exception {};

class TargetSearchVisitor : public default_bfs_visitor {
private:
    int target_;
    int target_distance_ = -1;
    std::vector<int> dist_;

public:
    explicit TargetSearchVisitor(int target, std::size_t num_vertices)
        : target_(target), dist_(num_vertices, -1) {}

    void start_vertex(int u) {
        dist_[u] = 0;
    }

    void tree_edge(int u, int v) {
        dist_[v] = dist_[u] + 1;
        if (v == target_) {
            target_distance_ = dist_[v];
            throw EarlyExitException(); // Дострокове переривання обходу!
        }
    }

    int get_target_distance() const { return target_distance_; }
};

void run_example_cpp(const std::vector<std::vector<int>>& graph, int start, int target) {
    TargetSearchVisitor visitor(target, graph.size());
    try {
        breadth_first_search_generic(graph, start, visitor);
        std::cout << "Вершина недосяжна\n";
    } catch (const EarlyExitException&) {
        std::cout << "Знайдено найкоротшу відстань: " << visitor.get_target_distance() << "\n";
    }
}
```
:::

### Приклад застосування: Відвідувач для розрахунку компонент зв'язності

Розглянемо інший випадок — відвідувач `ComponentLabelerVisitor`, який розмічає всі вершини графа індексами їхніх компонент зв'язності.

#### Механіка розфарбування компонент:
При обході несвоєрозвідного графа зовнішній цикл запускає BFS для кожної ще не відвіданої вершини, передаючи у відвідувач поточний номер компоненти `comp_id`. Точка перехоплення `discover_vertex` записує цей номер у підсумковий масив `component_map`.

:::tabs
```c
#include <stdlib.h>

typedef struct {
    int current_component;
    int* component_map;
} ComponentContextC;

static void c_on_discover_comp(int u, void* user_data) {
    ComponentContextC* ctx = (ComponentContextC*)user_data;
    ctx->component_map[u] = ctx->current_component;
}

void compute_components_c(
    int num_vertices,
    const int* const* adj_lists,
    const int* adj_sizes,
    int* out_components
) {
    for (int i = 0; i < num_vertices; ++i) out_components[i] = -1;

    ComponentContextC ctx = {0, out_components};
    BFSVisitorC visitor = {0};
    visitor.user_data = &ctx;
    visitor.discover_vertex = c_on_discover_comp;

    int comp_id = 0;
    for (int i = 0; i < num_vertices; ++i) {
        if (out_components[i] == -1) {
            ctx.current_component = comp_id++;
            c_bfs_run(num_vertices, adj_lists, adj_sizes, i, &visitor);
        }
    }
}
```
```cpp
#include <vector>

class ComponentLabelerVisitor : public default_bfs_visitor {
private:
    int current_component_;
    std::vector<int>& component_map_;

public:
    ComponentLabelerVisitor(int comp_id, std::vector<int>& comp_map)
        : current_component_(comp_id), component_map_(comp_map) {}

    void discover_vertex(int u) {
        component_map_[u] = current_component_;
    }
};

std::vector<int> compute_components_cpp(const std::vector<std::vector<int>>& graph) {
    std::size_t n = graph.size();
    std::vector<int> component_map(n, -1);
    int comp_id = 0;

    for (std::size_t i = 0; i < n; ++i) {
        if (component_map[i] == -1) {
            ComponentLabelerVisitor visitor(comp_id++, component_map);
            breadth_first_search_generic(graph, static_cast<int>(i), visitor);
        }
    }

    return component_map;
}
```
:::

### Приклад застосування: Відвідувач для запису найкоротшого шляху (Path Recorder Visitor)

Розглянемо практичний випадок розробки відвідувача `PathRecorderVisitor`, який фіксує дерево предків і відновлює вектор найкоротшого шляху від старту до цільової вершини.

:::tabs
```c
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    int* parent;
    int num_vertices;
} PathContextC;

static void c_on_tree_edge_path(int u, int v, void* user_data) {
    PathContextC* ctx = (PathContextC*)user_data;
    ctx->parent[v] = u;
}

int* reconstruct_path_c(const int* parent, int target, int* out_length) {
    if (parent[target] == -1 && target != 0) {
        *out_length = 0;
        return NULL;
    }

    int curr = target;
    int len = 0;
    while (curr != -1) {
        len++;
        curr = parent[curr];
    }

    int* path = (int*)malloc(sizeof(int) * len);
    curr = target;
    for (int i = len - 1; i >= 0; --i) {
        path[i] = curr;
        curr = parent[curr];
    }

    *out_length = len;
    return path;
}
```
```cpp
#include <vector>
#include <algorithm>

class PathRecorderVisitor : public default_bfs_visitor {
private:
    std::vector<int>& parent_;

public:
    explicit PathRecorderVisitor(std::vector<int>& parent)
        : parent_(parent) {}

    void tree_edge(int u, int v) {
        parent_[v] = u;
    }
};

std::vector<int> reconstruct_path_cpp(int start, int target, const std::vector<int>& parent) {
    if (parent[target] == -1 && target != start) {
        return {}; // Ціль недосяжна
    }

    std::vector<int> path;
    for (int v = target; v != -1; v = parent[v]) {
        path.push_back(v);
    }
    std::reverse(path.begin(), path.end());
    return path;
}
```
:::

### Довідкова таблиця методів відвідувача

| Метод (Callback) | Момент виклику | Типове застосування |
| :--- | :--- | :--- |
| `initialize_vertex` | Ініціалізація графа | Скидання кольорів та відстаней у `∞` |
| `start_vertex` | Старт обходу від `s` | Встановлення `dist[s] = 0` |
| `discover_vertex` | Додавання `v` в чергу | Установка `visited[v] = true`, запуск таймера |
| `examine_vertex` | Вилучення `u` з черги | Логування просування хвилі |
| `examine_edge` | Огляд вихідного ребра `(u, v)` | Підрахунок перевірених зв'язків |
| `tree_edge` | Ребро `(u, v)` до нової `v` | Запис `parent[v] = u`, `dist[v] = dist[u] + 1` |
| `non_tree_edge` | Ребро `(u, v)` до відвіданої `v` | Пошук непарних циклів, перевірка дводольності |
| `gray_target` | Ребро до `v` у черзі | Виявлення зворотних зв'язків на тому ж рівні |
| `black_target` | Ребро до вже обробленої `v` | Аналіз поперечних ребер нижчих рівнів |
| `finish_vertex` | Завершення огляду виходів `u` | Позначення вершини як повністю обробленої |
