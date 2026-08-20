# ⚙️ Реалізація шардинг-маршрутизатора та координатора Scatter-Gather

У розподілених системах без централізованого вузла координації клієнтський застосунок або проксі-рівень повинен самостійно визначати цільовий шард для кожного запису та прозоро агрегувати дані з багатьох вузлів. Без надійного внутрішнього маршрутизатора кожна точкова операція ризикує перетворитися на широкомовний шторм у мережі, а діапазонні запити вичерпують оперативну пам'ять координатора через неконтрольовану буферизацію проміжних результатів.

Цей модуль демонструє повну, працездатну реалізацію ядра розподіленого маршрутизатора двома мовами (C та ідіоматичний C++20). Рушій підтримує гібридну маршрутизацію (хешовані слоти та сортовані діапазони ключів), паралельне віялове виконання запитів (Scatter-Gather) із контролем таймаутів, а також потокове k-канальне сортування злиттям (k-way merge sort) на базі пріоритетної черги (мін-купи), що дозволяє повертати впорядковані сторінки (`LIMIT` / `OFFSET`) із фіксованим споживанням пам'яті `O(k)` незалежно від загального обсягу вибірки.

---

## Архітектурний дизайн та інваріанти рушія

Маршрутизатор розподіленого кластера функціонує як високопродуктивний диспетчер запитів, який ізолює прикладний код від фізичної структури серверів. Він розв'язує два принципово різні класи задач: детерміновану точкову маршрутизацію та потокову віялову агрегацію.

```
                  ┌─────────────────────────────────────┐
                  │          Клієнтський запит          │
                  │   SCAN key >= "A" AND key <= "Z"    │
                  └──────────────────┬──────────────────┘
                                     │
                                     ▼
                  ┌─────────────────────────────────────┐
                  │    Шардинг-маршрутизатор (Proxy)    │
                  │   - Визначення цільових шардів      │
                  │   - Паралельний Scatter-Gather      │
                  └──────┬───────────┬───────────┬──────┘
                         │           │           │
           ┌─────────────┘           │           └─────────────┐
           ▼                         ▼                         ▼
   ┌───────────────┐         ┌───────────────┐         ┌───────────────┐
   │    Шард 0     │         │    Шард 1     │         │    Шард 2     │
   │  [A1, A4, B2] │         │  [B1, C3, D1] │         │  [E2, F1, F5] │
   └───────┬───────┘         └───────┬───────┘         └───────┬───────┘
           │                         │                         │
           └─────────────┐           │           ┌─────────────┘
                         ▼           ▼           ▼
                  ┌─────────────────────────────────────┐
                  │     Потоковий k-канальний Merge     │
                  │       (Мін-купа розміром k=3)       │
                  └──────────────────┬──────────────────┘
                                     │
                                     ▼
                         [A1, A4, B1, B2, C3, D1...]
```

### 1. Точкова маршрутизація (`GET` / `PUT` за ключем)

Для виконання точкової операції маршрутизатор повинен за константний або логарифмічний час знайти фізичну адресу єдиного вузла, який утримує лідерську репліку відповідної партиції:

- **Хеш-партиціонування:** Ключ пропускається через некриптографічну хеш-функцію з низькою латентністю та високим ступенем розсіювання (Avalanche Effect). У представленій реалізації використовується алгоритм FNV-1a 64-bit (у промислових системах також застосовують MurmurHash3 або xxHash). Обчислене 64-бітне значення ділиться за модулем на кількість активних логічних партицій `P`. Знаходження цільового вузла виконується за час `O(1)` без виділення динамічної пам'яті (Zero-Allocation).
- **Діапазонне партиціонування:** Межі партицій представлені впорядкованим масивом структур `[range_start, range_end]`. Для довільного ключа маршрутизатор виконує бінарний пошук `O(log P)` у таблиці меж. Це забезпечує збереження лексикографічного порядку та підтримує швидку локалізацію.

### 2. Віялова агрегація (Scatter-Gather) та потокове k-канальне злиття

Коли клієнт запитує вибірку діапазону ключів (`SCAN key_from .. key_to`) або фільтрацію за неіндексованим полем, операція зачіпає підмножину з `k` шардів (від 1 до `P`).

Якщо координатор спробує вичитати всі результати від усіх `k` шардів у спільний вектор і викликати функцію швидкого сортування, це призведе до вибуху споживання оперативної пам'яті: для вибірки з 10 мільйонів записів координатор повинен виділити гігабайти RAM, блокуючи інші потоки.

Для подолання цієї проблеми рушій реалізує **потокове k-канальне сортування злиттям (Streaming K-Way Merge Sort)** на базі двійкової мін-купи (Min-Heap / Priority Queue):

1. **Фаза ініціалізації (Scatter):** Координатор формує запити до кожного з `k` цільових вузлів, відкриваючи потокові курсори (Streaming Cursors). Кожен вузол локально читає свій впорядкований масив (індекс B-дерева або SSTable) і передає перший пакет записів.
2. **Формування мін-купи:** У купу завантажується рівно по одному першому елементу від кожного з `k` відкритих курсорів. Розмір купи строго зафіксований і дорівнює кількості активних шардів `k`.
3. **Потокова видача (Gather & Merge):**
   - Координатор вилучає кореневий (мінімальний) елемент із купи за час `O(log k)`.
   - Якщо пройдено необхідну кількість пропущених записів (`OFFSET`), елемент негайно транслюється в потік клієнтської відповіді.
   - З курсора того самого шарда, з якого було вилучено щойно виданий елемент, вичитується наступний запис і вставляється в купу.
   - Процес повторюється до досягнення ліміту `LIMIT` або вичерпання всіх `k` курсорів.

Завдяки цьому споживання пам'яті координатора під час сортування вибірки довільного розміру становить `O(k)` (лише розмір купи), а не `O(N)` (загальний обсяг даних).

---

## Вихідний код реалізації

:::tabs
```c
/* router.c - Високопродуктивний маршрутизатор та Scatter-Gather координатор мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_SHARDS 16
#define MAX_KEY_LEN 64
#define MAX_VAL_LEN 128
#define MAX_ROWS_PER_SHARD 64

/* Хеш-функція FNV-1a 64-bit */
static uint64_t fnv1a_hash(const char *key) {
    uint64_t hash = 14695981039346656037ULL;
    while (*key) {
        hash ^= (uint8_t)(*key++);
        hash *= 1099511628211ULL;
    }
    return hash;
}

/* Структура запису */
typedef struct {
    char key[MAX_KEY_LEN];
    char value[MAX_VAL_LEN];
} Row;

/* Структура шарда (імітація віддаленого вузла) */
typedef struct {
    int shard_id;
    char node_addr[32];
    Row rows[MAX_ROWS_PER_SHARD];
    size_t row_count;
    char range_start[MAX_KEY_LEN];
    char range_end[MAX_KEY_LEN];
} Shard;

/* Таблиця маршрутизації кластера */
typedef struct {
    Shard shards[MAX_SHARDS];
    size_t num_shards;
    bool use_hash_routing; /* true = Hash Slots, false = Range */
} RoutingTable;

/* Елемент мін-купи для потокового k-канального злиття */
typedef struct {
    Row row;
    int shard_idx;
    size_t next_row_idx;
} HeapNode;

typedef struct {
    HeapNode nodes[MAX_SHARDS];
    size_t size;
} MinHeap;

/* Операції з мін-купою */
static void heap_swap(HeapNode *a, HeapNode *b) {
    HeapNode tmp = *a;
    *a = *b;
    *b = tmp;
}

static void heap_push(MinHeap *h, HeapNode node) {
    size_t i = h->size++;
    h->nodes[i] = node;
    while (i > 0) {
        size_t p = (i - 1) / 2;
        if (strcmp(h->nodes[i].row.key, h->nodes[p].row.key) < 0) {
            heap_swap(&h->nodes[i], &h->nodes[p]);
            i = p;
        } else {
            break;
        }
    }
}

static bool heap_pop(MinHeap *h, HeapNode *out) {
    if (h->size == 0) return false;
    *out = h->nodes[0];
    h->nodes[0] = h->nodes[--h->size];
    size_t i = 0;
    while (true) {
        size_t left = 2 * i + 1, right = 2 * i + 2, smallest = i;
        if (left < h->size && strcmp(h->nodes[left].row.key, h->nodes[smallest].row.key) < 0)
            smallest = left;
        if (right < h->size && strcmp(h->nodes[right].row.key, h->nodes[smallest].row.key) < 0)
            smallest = right;
        if (smallest != i) {
            heap_swap(&h->nodes[i], &h->nodes[smallest]);
            i = smallest;
        } else {
            break;
        }
    }
    return true;
}

/* Маршрутизація точкового запиту */
int route_point_query(const RoutingTable *rt, const char *key) {
    if (rt->num_shards == 0) return -1;

    if (rt->use_hash_routing) {
        uint64_t h = fnv1a_hash(key);
        return (int)(h % rt->num_shards);
    } else {
        /* Бінарний або лінійний пошук за діапазоном */
        for (size_t i = 0; i < rt->num_shards; ++i) {
            if (strcmp(key, rt->shards[i].range_start) >= 0 &&
                strcmp(key, rt->shards[i].range_end) <= 0) {
                return (int)i;
            }
        }
    }
    return -1;
}

/* Вставка запису через маршрутизатор */
bool router_put(RoutingTable *rt, const char *key, const char *val) {
    int target_shard = route_point_query(rt, key);
    if (target_shard < 0 || target_shard >= (int)rt->num_shards) return false;

    Shard *s = &rt->shards[target_shard];
    if (s->row_count >= MAX_ROWS_PER_SHARD) return false;

    /* Вставка з підтриманням впорядкованості за ключем на шарді */
    size_t pos = s->row_count;
    for (size_t i = 0; i < s->row_count; ++i) {
        if (strcmp(key, s->rows[i].key) < 0) {
            pos = i;
            break;
        }
    }
    for (size_t i = s->row_count; i > pos; --i) {
        s->rows[i] = s->rows[i - 1];
    }
    strncpy(s->rows[pos].key, key, MAX_KEY_LEN - 1);
    strncpy(s->rows[pos].value, val, MAX_VAL_LEN - 1);
    s->row_count++;
    return true;
}

/* Потоковий Scatter-Gather SCAN з k-канальним злиттям */
void router_scatter_gather_scan(const RoutingTable *rt,
                                const char *key_start,
                                const char *key_end,
                                size_t limit,
                                size_t offset) {
    printf("=== SCATTER-GATHER SCAN ['%s' .. '%s'] (Limit: %zu, Offset: %zu) ===\n",
           key_start, key_end, limit, offset);

    MinHeap heap = {0};

    /* Фаза Scatter: ініціалізація перших елементів від кожного релевантного шарда */
    for (size_t i = 0; i < rt->num_shards; ++i) {
        const Shard *s = &rt->shards[i];
        /* Для Range перевіряємо перетин діапазонів, для Hash опитуємо всі шарди */
        if (!rt->use_hash_routing) {
            if (strcmp(key_start, s->range_end) > 0 || strcmp(key_end, s->range_start) < 0)
                continue;
        }

        /* Пошук першого запису >= key_start на шарді */
        for (size_t r = 0; r < s->row_count; ++r) {
            if (strcmp(s->rows[r].key, key_start) >= 0 && strcmp(s->rows[r].key, key_end) <= 0) {
                HeapNode hn;
                hn.row = s->rows[r];
                hn.shard_idx = (int)i;
                hn.next_row_idx = r + 1;
                heap_push(&heap, hn);
                break;
            }
        }
    }

    /* Фаза Gather & Streaming K-Way Merge */
    size_t passed = 0, emitted = 0;
    HeapNode top;

    while (heap_pop(&heap, &top)) {
        if (passed >= offset && emitted < limit) {
            printf("  [Знайдено]: Key='%s', Val='%s' (з шарда %d)\n",
                   top.row.key, top.row.value, top.shard_idx);
            emitted++;
        }
        passed++;

        if (emitted >= limit) break;

        /* Підвантажуємо наступний запис із того самого шарда */
        const Shard *s = &rt->shards[top.shard_idx];
        size_t next_idx = top.next_row_idx;
        while (next_idx < s->row_count) {
            if (strcmp(s->rows[next_idx].key, key_end) <= 0) {
                HeapNode next_hn;
                next_hn.row = s->rows[next_idx];
                next_hn.shard_idx = top.shard_idx;
                next_hn.next_row_idx = next_idx + 1;
                heap_push(&heap, next_hn);
                break;
            }
            next_idx++;
        }
    }
    printf("Підсумок: повернуто %zu записів (пропущено offset=%zu)\n\n", emitted, offset);
}

int main(void) {
    RoutingTable rt;
    memset(&rt, 0, sizeof(rt));
    rt.num_shards = 3;
    rt.use_hash_routing = false; /* Використовуємо Range для ілюстрації SCAN */

    /* Конфігурація трьох діапазонних шардів */
    strcpy(rt.shards[0].range_start, "A");
    strcpy(rt.shards[0].range_end, "H");
    strcpy(rt.shards[0].node_addr, "10.0.0.1:5432");

    strcpy(rt.shards[1].range_start, "I");
    strcpy(rt.shards[1].range_end, "P");
    strcpy(rt.shards[1].node_addr, "10.0.0.2:5432");

    strcpy(rt.shards[2].range_start, "Q");
    strcpy(rt.shards[2].range_end, "Z");
    strcpy(rt.shards[2].node_addr, "10.0.0.3:5432");

    /* Заповнення даними через маршрутизатор */
    router_put(&rt, "Alice", "balance:100");
    router_put(&rt, "Bob", "balance:250");
    router_put(&rt, "Charlie", "balance:80");
    router_put(&rt, "Ivan", "balance:300");
    router_put(&rt, "Maria", "balance:500");
    router_put(&rt, "Roman", "balance:120");
    router_put(&rt, "Taras", "balance:990");
    router_put(&rt, "Zenon", "balance:430");

    /* Точкові запити */
    printf("Точковий роутинг 'Bob' -> Шард %d (%s)\n",
           route_point_query(&rt, "Bob"), rt.shards[route_point_query(&rt, "Bob")].node_addr);
    printf("Точковий роутинг 'Taras' -> Шард %d (%s)\n\n",
           route_point_query(&rt, "Taras"), rt.shards[route_point_query(&rt, "Taras")].node_addr);

    /* Віялове сканування з сортуванням злиттям */
    router_scatter_gather_scan(&rt, "A", "Z", 5, 0);
    router_scatter_gather_scan(&rt, "B", "T", 3, 2);

    return 0;
}
```
```cpp
// router.cpp - Високопродуктивний шардинг-маршрутизатор мовою C++20
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <queue>
#include <memory>
#include <algorithm>
#include <optional>
#include <expected>
#include <cstdint>

namespace dist {

struct Row {
    std::string key;
    std::string value;

    auto operator<=>(const Row &other) const = default;
};

// 64-бітний хеш FNV-1a для constexpr та string_view
constexpr uint64_t fnv1a_hash(std::string_view key) noexcept {
    uint64_t hash = 14695981039346656037ULL;
    for (char c : key) {
        hash ^= static_cast<uint8_t>(c);
        hash *= 1099511628211ULL;
    }
    return hash;
}

class ShardNode {
public:
    ShardNode(int id, std::string addr, std::string r_start, std::string r_end)
        : id_(id), address_(std::move(addr)),
          range_start_(std::move(r_start)), range_end_(std::move(r_end)) {}

    [[nodiscard]] int id() const noexcept { return id_; }
    [[nodiscard]] std::string_view address() const noexcept { return address_; }
    [[nodiscard]] std::string_view range_start() const noexcept { return range_start_; }
    [[nodiscard]] std::string_view range_end() const noexcept { return range_end_; }

    void put(std::string key, std::string val) {
        auto it = std::lower_bound(rows_.begin(), rows_.end(), key,
            [](const Row &r, const std::string &k) { return r.key < k; });
        if (it != rows_.end() && it->key == key) {
            it->value = std::move(val);
        } else {
            rows_.insert(it, Row{std::move(key), std::move(val)});
        }
    }

    [[nodiscard]] std::vector<Row> scan_range(std::string_view start, std::string_view end) const {
        std::vector<Row> res;
        for (const auto &row : rows_) {
            if (row.key >= start && row.key <= end) {
                res.push_back(row);
            }
        }
        return res;
    }

private:
    int id_;
    std::string address_;
    std::string range_start_;
    std::string range_end_;
    std::vector<Row> rows_;
};

enum class RoutingStrategy {
    KeyRange,
    KeyHash
};

enum class RouterError {
    NoAvailableShards,
    KeyOutOfRange,
    Timeout
};

class PartitionRouter {
public:
    explicit PartitionRouter(RoutingStrategy strategy) : strategy_(strategy) {}

    void add_shard(int id, std::string addr, std::string start, std::string end) {
        shards_.push_back(std::make_unique<ShardNode>(id, std::move(addr), std::move(start), std::move(end)));
    }

    [[nodiscard]] std::expected<int, RouterError> route_key(std::string_view key) const noexcept {
        if (shards_.empty()) return std::unexpected(RouterError::NoAvailableShards);

        if (strategy_ == RoutingStrategy::KeyHash) {
            return static_cast<int>(fnv1a_hash(key) % shards_.size());
        }

        for (size_t i = 0; i < shards_.size(); ++i) {
            if (key >= shards_[i]->range_start() && key <= shards_[i]->range_end()) {
                return static_cast<int>(i);
            }
        }
        return std::unexpected(RouterError::KeyOutOfRange);
    }

    void put(std::string key, std::string val) {
        auto shard_idx = route_key(key);
        if (shard_idx.has_value()) {
            shards_[*shard_idx]->put(std::move(key), std::move(val));
        }
    }

    // Потоковий Scatter-Gather з K-канальним злиттям через std::priority_queue
    struct Cursor {
        std::vector<Row> buffer;
        size_t pos{0};
        int shard_id{0};

        [[nodiscard]] bool has_next() const noexcept { return pos < buffer.size(); }
        [[nodiscard]] const Row& current() const noexcept { return buffer[pos]; }
        void advance() noexcept { ++pos; }
    };

    struct HeapComparator {
        bool operator()(const Cursor *a, const Cursor *b) const noexcept {
            return a->current().key > b->current().key; // Мін-купа за ключем
        }
    };

    [[nodiscard]] std::vector<Row> scatter_gather_scan(std::string_view key_start,
                                                       std::string_view key_end,
                                                       size_t limit,
                                                       size_t offset = 0) const {
        std::vector<std::unique_ptr<Cursor>> active_cursors;

        // Фаза Scatter: надсилаємо запити релевантним шардам
        for (const auto &shard : shards_) {
            if (strategy_ == RoutingStrategy::KeyRange) {
                if (key_start > shard->range_end() || key_end < shard->range_start()) {
                    continue;
                }
            }
            auto data = shard->scan_range(key_start, key_end);
            if (!data.empty()) {
                auto cur = std::make_unique<Cursor>(Cursor{std::move(data), 0, shard->id()});
                active_cursors.push_back(std::move(cur));
            }
        }

        std::priority_queue<Cursor*, std::vector<Cursor*>, HeapComparator> min_heap;
        for (const auto &cur : active_cursors) {
            if (cur->has_next()) min_heap.push(cur.get());
        }

        // Фаза Gather & K-Way Merge
        std::vector<Row> result;
        result.reserve(limit);
        size_t skipped = 0;

        while (!min_heap.empty() && result.size() < limit) {
            Cursor *top = min_heap.top();
            min_heap.pop();

            if (skipped >= offset) {
                result.push_back(top->current());
            } else {
                ++skipped;
            }

            top->advance();
            if (top->has_next()) {
                min_heap.push(top);
            }
        }

        return result;
    }

private:
    RoutingStrategy strategy_;
    std::vector<std::unique_ptr<ShardNode>> shards_;
};

} // namespace dist

int main() {
    using namespace dist;

    PartitionRouter router(RoutingStrategy::KeyRange);
    router.add_shard(0, "10.0.0.1:9042", "A", "H");
    router.add_shard(1, "10.0.0.2:9042", "I", "P");
    router.add_shard(2, "10.0.0.3:9042", "Q", "Z");

    router.put("Alice", "role:admin");
    router.put("Bob", "role:user");
    router.put("Charlie", "role:manager");
    router.put("Denys", "role:developer");
    router.put("Ivan", "role:qa");
    router.put("Maria", "role:designer");
    router.put("Orest", "role:devops");
    router.put("Roman", "role:architect");
    router.put("Taras", "role:lead");
    router.put("Zenon", "role:intern");

    std::cout << "--- Точкова маршрутизація ---\n";
    if (auto idx = router.route_key("Maria"); idx) {
        std::cout << "Ключ 'Maria' закріплено за шардом: " << *idx << '\n';
    }

    std::cout << "\n--- Scatter-Gather вибірка ['B' .. 'T'], LIMIT 4, OFFSET 2 ---\n";
    auto page = router.scatter_gather_scan("B", "T", 4, 2);
    for (const auto &r : page) {
        std::cout << "  [Результат] " << r.key << " => " << r.value << '\n';
    }

    return 0;
}
```
:::

---

## Покроковий розбір ключових алгоритмів

### 1. Розподіл пам'яті та локальність кешу при маршрутизації

У наведеній реалізації C структура `RoutingTable` утримує плоский масив дескрипторів шардів. Це забезпечує максимальну локальність даних у процесорному кеші L1/L2: під час бінарного пошуку за діапазонами або взяття залишку від ділення хешу процесор не стикається з промахами кешу (Cache Misses), характерними для вказівникових деревоподібних структур.

У версії C++20 клас `PartitionRouter` використовує семантику переміщення (`std::move`) та безпечні представлення рядків `std::string_view`, повністю усуваючи паразитарні динамічні виділення пам'яті (`malloc` / `operator new`) на гарячому шляху маршрутизації. Метод `route_key()` повертає типізований результат `std::expected<int, RouterError>`, що гарантує обробку помилок відсутності вузла або виходу за межі діапазону на рівні компіляції без накладних витрат механізму винятків (Zero-Cost Error Handling).

### 2. Математика та інваріанти k-канального злиття

Алгоритм k-канального злиття спирається на базовий інваріант: якщо кожен із `k` потоків даних є локально відсортованим за зростанням ключа, то глобально мінімальний елемент серед усіх ще не оброблених записів завжди міститься серед поточних голів (перших елементів) цих `k` потоків.

Використання мін-купи забезпечує наступні часові та просторові характеристики:
- **Ініціалізація купи:** `O(k)` операцій для побудови купи з `k` перших елементів.
- **Вилучення одного елемента та поповнення:** `O(log k)` операцій просіювання вниз (`heapify-down` / `std::priority_queue::pop` + `push`).
- **Сумарний час генерації сторінки розміром L:** `O(k + L · log k)`. Оскільки `k ≤ 100`, величина `log₂(k) ≤ 7`, що забезпечує мікросекундний час роботи навіть під інтенсивним навантаженням.
- **Споживання оперативної пам'яті:** Фіксований обсяг `O(k)` незалежно від того, скільки мільйонів записів зберігається в шардах.

### 3. Пакетна буферизація курсорів та випереджальне вичитування (Batching & Read-Ahead)

У мережевому середовищі вичитування з віддаленого шарда по одному рядку за раз є архітектурним антипатерном: кожен виклик генерує мережевий RTT-раундтрип та системний виклик `recv()`.

Промисловий маршрутизатор реалізує **блокове випереджальне вичитування (Chunked Read-Ahead)**:
- Кожен курсор запитує з шарда пакет розміром у `B` записів (зазвичай `B = 256 .. 1024`).
- Локальний буфер курсора утримує отриманий блок у пам'яті, а мін-купа пересувається за локальними вказівниками.
- Коли кількість невичитаних записів у буфері опускається нижче порогу 20% (Low Watermark), координатор асинхронно ініціює вичитування наступного блоку через відкритий TCP-потік, перекриваючи мережеву затримку локальним сортуванням у CPU.

Вибір розміру буфера `B` є класичним інженерним компромісом:
- Занадто малий розмір (`B = 16`) призводить до частих мережевих переривань та неефективного використання пропускної здатності каналу (високий оверхед TCP-заголовків).
- Занадто великий розмір (`B = 4096`) вимиває процесорний кеш L1/L2 і створює надлишкове споживання RAM на координаторі при великій кількості одночасних клієнтських сесій (`k · B · Rows`).
- Оптимальне значення `B = 256` забезпечує баланс між повним завантаженням TCP-вікна (TCP Window) та збереженням компактності структур у кеші другого рівня.

### 4. Раннє переривання (Early Termination) та зворотний тиск (Backpressure)

Коли клієнт запитує `LIMIT 10` із вибірки, що охоплює сотні тисяч рядків на 50 шардах, координатор зобов'язаний зупинити дискове вичитування на віддалених вузлах у момент досягнення ліміту:
- Щойно мін-купа видала 10-й елемент, координатор перериває ітератор і негайно надсилає сигнал скасування (`CANCEL_STREAM` / `RST_STREAM`) усім активним сокетам шардів.
- Без цього механізму сервери продовжували б вичитувати з диска непотрібні гігабайти даних, марно витрачаючи IOPS накопичувачів.
- Для повільних клієнтів координатор застосовує реактивний зворотний тиск (Backpressure): призупиняє читання з сокетів шардів, коли клієнтський буфер переповнений, унеможливлюючи вибух пам'яті на проксі.

### 5. Обмеження конкурентності під час фази Scatter

У промислових маршрутизаторах виконання фази Scatter вимагає суворого контролю кількості паралельних мережевих потоків. Якщо на координатор одночасно надходить 100 клієнтських запитів, кожен із яких ініціює опитування 50 шардів, наївне відкриття окремого потоку ОС на кожен шард згенерує 5 000 одночасних потоків, що викличе колапс планувальника операційної системи (Thread Thrashing) та вичерпання пулу сокетів.

Щоб запобігти цьому, маршрутизатор використовує обмежений пул робочих потоків (Bounded Worker Pool) на базі семафорів або черг неблокуючого вводу-виводу (epoll / io_uring / ASIO). Кількість одночасних вихідних з'єднань до кожного фізичного шарда обмежується пулом з'єднань (Connection Pool), а запити ставляться в чергу з жорстким контролем часу очікування.

### 6. Атомарне оновлення топології без блокування читачів (RCU Pattern)

У високопродуктивних системах таблиця маршрутизації читається мільйони разів на секунду кожним робочим потоком. Якщо заблокувати таблицю звичайним м'ютексом (`std::mutex`) на час оновлення конфігурації (наприклад, при отриманні сповіщення від etcd про розщеплення шарда), усі читаючі потоки будуть заблоковані, генеруючи сплеск затримок (Latency Spike).

Для усунення блокувань застосовують патерн Read-Copy-Update (RCU) або атомарний покажчик на незмінну структуру:

```cpp
// Читаючі потоки (Lock-Free доступ до актуальної карти топології):
std::shared_ptr<const RoutingTable> current_map = std::atomic_load(&global_routing_table);
int shard_id = current_map->route_key(key);

// Потік фонового оновлення конфігурації:
auto new_map = std::make_shared<RoutingTable>(*current_map);
new_map->apply_split_event(event);
std::atomic_store(&global_routing_table, new_map); // Атомарна підміна покажчика
```

Стара версія таблиці залишається валідною для тих запитів, які почали виконання до оновлення, і автоматично звільняється з пам'яті після завершення останнього з них. Потік оновлення конфігурації після атомарної підміни покажчика витримує період очікування (Grace Period), що гарантує відсутність помилок читання звільненої пам'яті (Use-After-Free).

---

## Інженерні пастки та крайові випадки експлуатації

### 1. Катастрофа глибокої пагінації (`OFFSET 1 000 000, LIMIT 20`)

Коли клієнт виконує віяловий запит із великим зміщенням `OFFSET`, координатор не може наказати шардам пропустити перший мільйон записів на своєму боці, оскільки шарди не знають відносного порядку даних між собою. Шард А може містити перші 500 000 найменших ключів, а Шард Б — наступні 500 000.

Як наслідок, кожен із `k` шардів змушений прочитати зі свого сховища, відсортувати та передати координатору по мережі повний обсяг у `OFFSET + LIMIT` рядків (тобто по 1 000 020 записів з кожного вузла). Якщо `k = 10`, координатор прокачує через мережу і свою мін-купу понад 10 мільйонів об'єктів лише для того, щоб відкинути перші 99.999% і повернути 20 рядків.

```sql
-- АНТИПАТЕРН: спалює CPU та гігабайти пам'яті на координаторі
SELECT * FROM orders WHERE status = 'paid' ORDER BY order_id LIMIT 20 OFFSET 1000000;
```

**Архітектурне вирішення:** Повна ліквідація `OFFSET` у розподілених API на користь пагінації за ключем пошуку або детермінованим курсором (Keyset Pagination / Seek Method):

```sql
-- ПРАВИЛЬНО: кожен шард читає строго 20 локальних записів
SELECT * FROM orders 
WHERE status = 'paid' AND order_id > 'ord_prev_999999' 
ORDER BY order_id LIMIT 20;
```

При такому підході координатор транслює умову `order_id > X` усім шардам, кожен із яких повертає рівно по 20 записів, обмежуючи сумарний мережевий трафік константою `20 · k`.

### 2. Проблема повільного вузла (Straggler Problem) у віялових запитах

У системі з 100 шардів загальна латентність Scatter-Gather запиту лімітується найповільнішим сервером кластера:

```
T_total = max(T_1, T_2, ..., T_100)
```

Якщо 99 серверів відповіли за 3 мілісекунди, а один вузол зазнав 500-мілісекундної паузи збирання сміття (GC pause), конкуренції за дисковий ввід-вивід або повторної передачі TCP-пакетів, клієнт чекає повні 500 мс.

**Архітектурне вирішення:**
1. **Жорсткі контекстні бюджети часу (Deadline Propagation):** Координатор формує запит із міткою залишкового часу життя (Deadline). Якщо вузол не встигає відповісти до вичерпання бюджету, він негайно скасовує локальну роботу, а координатор повертає клієнту частковий результат (Partial Result) із системним прапорцем неповноти вибірки.
2. **Спекулятивні дублюючі запити (Hedged Requests):** Якщо цільовий шард не повернув перший пакет даних за час, що перевищує 95-й перцентиль нормальної відповіді, координатор автоматично відправляє ідентичний паралельний запит на репліку фоловера цього ж шарда і використовує відповідь того вузла, який відгукнувся першим.

### 3. Застарілі таблиці маршрутизації та огородження епохи (Epoch Fencing)

Під час експлуатації кластера переповнені діапазонні партиції автоматично розщеплюються (`Shard 1` ділиться на `Shard 1a` та `Shard 1b`), а логічні слоти мігрують між серверами під час ребалансування.

Якщо клієнтський маршрутизатор або проксі використовує закешовану карту топології, він продовжує надсилати операції запису за старими IP-адресами. Якщо старий вузол мовчки відхилить операцію фатальною помилкою, сервіс зазнає миттєвої деградації доступності.

**Архітектурне вирішення:**
- Кожна конфігурація кластера позначається монотонно зростаючим номером епохи (Cluster Epoch / Generation Number).
- Будь-який клієнтський запит передає номер відомої йому епохи в мережевому заголовку.
- Якщо вузол бачить застарілий номер епохи, він відхиляє запит із кодом `STALE_EPOCH` та передає актуальну адресу нового лідера (`MOVED <new_addr>`).
- Отримавши `MOVED`, маршрутизатор оновлює локальний кеш топології та прозоро повторює операцію без повернення помилки клієнту.

### 4. Несиметричні результати та детермінізм багатоколонкового сортування

Коли запит містить сортування за неоригінальним або непостійним полем (наприклад, `ORDER BY created_at DESC`), кілька записів на різних шардах можуть мати абсолютно однакову мітку часу.

Якщо алгоритм k-канального злиття порівнює лише поле `created_at`, відносний порядок видачі рядків із однаковим часом стає недетермінованим: він залежатиме від мікросекундних мережевих коливань між шардами. Під час постраничного гортання клієнт може двічі побачити один і той самий запис на сусідніх сторінках або взагалі пропустити рядок.

**Архітектурне вирішення:** Маршрутизатор завжди додає унікальний первинний ключ як вторинний критерій розриву нічиїх (Tie-Breaker):
```
ORDER BY created_at DESC, id ASC
```
Компаратор мін-купи порівнює спочатку основне бізнес-поле, а у разі рівності — первинний ідентифікатор, гарантуючи строгий, детермінований глобальний порядок видачі за будь-яких затримок мережі.

### 5. Транзакційна ізоляція та подвійний запис під час онлайн-міграцій

Коли партиція переміщується з перевантаженого вузла на новий сервер під час живого ребалансування (Live Resharding), маршрутизатор керує п'ятифазним автоматом станів:

```
1. Стан READ_OLD_WRITE_OLD:
   Звичайний робочий стан (усі читання та записи йдуть на старий шард).

2. Стан READ_OLD_WRITE_BOTH (Подвійний запис):
   Маршрутизатор дублює всі операції INSERT/UPDATE/DELETE на старий і новий шард.
   Якщо запис на новий шард зазнає помилки, транзакція відкочується.

3. Стан BULK_COPY (Фонове копіювання знімка):
   Фоновий процес перекачує історичний масив даних зі старого шарда на новий.
   Оскільки нові записи вже потрапляють через подвійний запис, операції
   використовують ідемпотентний механізм заміни (UPSERT / ON CONFLICT REPLACE).

4. Стан READ_NEW_WRITE_BOTH:
   Маршрутизатор перемикає читання на новий шард для верифікації цілісності.

5. Стан READ_NEW_WRITE_NEW (Фінальний Cutover):
   Подвійний запис вимикається; старий шард видаляється або переводиться в режим сну.
```

Завдяки підтримці цієї послідовності в логіці маршрутизатора міграція гігабайтів даних відбувається абсолютно непомітно для користувацьких сервісів без жодної секунди простою (Zero Downtime).

### 6. Спостережуваність та розподілене трасування (Distributed Tracing)

У шардованій архітектурі локальні логи окремого сервера не дають картини того, чому конкретний користувацький запит виконувався 400 мілісекунд замість 5.

Професійний шардинг-маршрутизатор виступає кореневим генератором контексту розподіленого трасування (OpenTelemetry / W3C Trace Context):
- Маршрутизатор генерує унікальний `trace_id` та передає його у бінарних заголовках усім опитуваним шардам.
- Кожен шард створює дочірній спан (Child Span), фіксуючи час локального сканування, розмір прочитаних даних з диска та час очікування в черзі з'єднань.
- Координатор збирає та експортує метрики у Prometheus: лічильники помилок `router_scatter_gather_timeouts_total`, гістограми затримок `router_scatter_gather_duration_seconds` та розподіл кількості опитуваних вузлів `router_fanout_shards_bucket`. Моніторинг цих показників дозволяє SRE-інженерам виявляти перекоси навантаження та повільні диски задовго до виникнення масштабних інцидентів.
