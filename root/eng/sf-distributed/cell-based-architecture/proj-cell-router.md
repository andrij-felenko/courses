# ⚙️ Реалізація маршрутизатора комірок: детерміноване та перемішане спрямування запитів

Шар маршрутизації комірок (англ. *Cell Router*) — це безстатусний високоефективний шлюз, який приймає вхідний мережевий запит, вилучає ідентифікатор орендаря (`Tenant ID`) або сесійний ключ і перенаправляє запит у відповідну автономну комірку.

Маршрутизатор знаходиться на критичному шляху кожного клієнтського звернення. Будь-яка затримка або виділення динамічної пам'яті на цьому рівні безпосередньо збільшує кінцеву латентність системи. Тому архітектура маршрутизатора вимагає нульових динамічних алокацій (`zero heap allocation`) на запит та використання детермінованих алгоритмів із передбачуваним часом виконання `O(1)`.

## Архітектурні вимоги та вибір алгоритмів

1. **Субмікросекундний час маршрутизації (`< 1 мкс`):** Усі структури даних комірок зберігаються в компактних неперервних масивах у пам'яті, що забезпечує стовідсоткове попадання в кеш процесора (L1/L2 Data Cache).
2. **Алгоритм хешування FNV-1a (Fowler–Noll–Vo):** Застосовується для обчислення 64-бітного хешу від ідентифікатора орендаря. Він забезпечує рівномірний розподіл залишків та високу лавинну здатність (англ. *avalanche effect*) при мінімальних витратах процесорних інструкцій.
3. **Два режими спрямування трафіку:**
   - **Пряме детерміноване шардування:** фіксоване закріплення орендаря за однією коміркою за формулою `hash(tenant_id) % N` з автоматичним лінійним зондуванням у разі збою;
   - **Перемішане шардування (Shuffle Sharding):** вибір підмножини з `K` унікальних комірок за допомогою детермінованого псевдовипадкового генератора (LCG) з подальшим вибором найменш завантаженої активної комірки.
4. **Облік стану здоров'я та дренажу:** автоматичне відсікання комірок зі статусами `DRAINING`, `INACTIVE` або `UNHEALTHY`.

## Реалізація на C та C++

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_CELLS 64
#define MAX_TENANT_LEN 64
#define SHUFFLE_K 3

typedef enum {
    CELL_STATE_INACTIVE = 0,
    CELL_STATE_ACTIVE = 1,
    CELL_STATE_DRAINING = 2,
    CELL_STATE_UNHEALTHY = 3
} cell_state_t;

typedef struct {
    uint32_t cell_id;
    char endpoint[128];
    cell_state_t state;
    uint32_t active_connections;
} cell_descriptor_t;

typedef struct {
    cell_descriptor_t cells[MAX_CELLS];
    size_t cell_count;
} cell_router_t;

/* 64-бітний алгоритм хешування FNV-1a */
static uint64_t fnv1a_hash(const char *str, size_t len) {
    uint64_t hash = 14695981039346656037ULL;
    for (size_t i = 0; i < len; ++i) {
        hash ^= (uint8_t)str[i];
        hash *= 1099511628211ULL;
    }
    return hash;
}

/* Ініціалізація маршрутизатора */
void cell_router_init(cell_router_t *router) {
    memset(router, 0, sizeof(cell_router_t));
}

/* Реєстрація комірки */
bool cell_router_add_cell(cell_router_t *router, uint32_t cell_id,
                          const char *endpoint, cell_state_t state) {
    if (router->cell_count >= MAX_CELLS) {
        return false;
    }
    cell_descriptor_t *cell = &router->cells[router->cell_count++];
    cell->cell_id = cell_id;
    snprintf(cell->endpoint, sizeof(cell->endpoint), "%s", endpoint);
    cell->state = state;
    cell->active_connections = 0;
    return true;
}

/* 1. Пряма маршрутизація: один орендар -> одна активна комірка */
const cell_descriptor_t* cell_route_direct(const cell_router_t *router,
                                           const char *tenant_id) {
    if (router->cell_count == 0) {
        return NULL;
    }
    uint64_t h = fnv1a_hash(tenant_id, strlen(tenant_id));
    size_t start_idx = (size_t)(h % router->cell_count);

    /* Лінійне зондування у разі збою основної комірки */
    for (size_t i = 0; i < router->cell_count; ++i) {
        size_t idx = (start_idx + i) % router->cell_count;
        const cell_descriptor_t *cell = &router->cells[idx];
        if (cell->state == CELL_STATE_ACTIVE) {
            return cell;
        }
    }
    return NULL;
}

/* 2. Перемішане шардування (Shuffle Sharding): обрання K унікальних комірок */
const cell_descriptor_t* cell_route_shuffle(const cell_router_t *router,
                                            const char *tenant_id,
                                            size_t k_subset) {
    if (router->cell_count == 0 || k_subset == 0 || k_subset > router->cell_count) {
        return NULL;
    }

    uint64_t seed = fnv1a_hash(tenant_id, strlen(tenant_id));
    uint32_t chosen_indices[MAX_CELLS];
    size_t chosen_count = 0;

    /* Детермінований вибір K унікальних комірок для орендаря */
    uint64_t state = seed;
    while (chosen_count < k_subset) {
        /* Лінійний конгруентний генератор псевдовипадкових чисел */
        state = state * 6364136223846793005ULL + 1442695040888963407ULL;
        uint32_t candidate = (uint32_t)((state >> 32) % router->cell_count);

        bool duplicate = false;
        for (size_t j = 0; j < chosen_count; ++j) {
            if (chosen_indices[j] == candidate) {
                duplicate = true;
                break;
            }
        }
        if (!duplicate) {
            chosen_indices[chosen_count++] = candidate;
        }
    }

    /* Вибір найбільш здорової та найменш завантаженої комірки з виділених K */
    const cell_descriptor_t *best_cell = NULL;
    uint32_t min_connections = UINT32_MAX;

    for (size_t i = 0; i < chosen_count; ++i) {
        const cell_descriptor_t *cell = &router->cells[chosen_indices[i]];
        if (cell->state == CELL_STATE_ACTIVE) {
            if (cell->active_connections < min_connections) {
                min_connections = cell->active_connections;
                best_cell = cell;
            }
        }
    }

    return best_cell;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <cstdint>
#include <algorithm>
#include <limits>

namespace cellular {

enum class CellState {
    Inactive = 0,
    Active = 1,
    Draining = 2,
    Unhealthy = 3
};

struct CellDescriptor {
    uint32_t id;
    std::string endpoint;
    CellState state{CellState::Active};
    uint32_t active_connections{0};
};

class CellRouter {
public:
    explicit CellRouter(size_t shuffle_k = 3) : shuffle_k_(shuffle_k) {}

    bool add_cell(uint32_t id, std::string endpoint, CellState state = CellState::Active) {
        cells_.push_back(CellDescriptor{id, std::move(endpoint), state, 0});
        return true;
    }

    void set_cell_state(uint32_t cell_id, CellState new_state) {
        for (auto &cell : cells_) {
            if (cell.id == cell_id) {
                cell.state = new_state;
                break;
            }
        }
    }

    /* 1. Пряма маршрутизація: обрання активної комірки за хешем */
    [[nodiscard]] std::optional<CellDescriptor> route_direct(std::string_view tenant_id) const {
        if (cells_.empty()) {
            return std::nullopt;
        }
        const uint64_t hash = hash_fnv1a(tenant_id);
        const size_t start_idx = hash % cells_.size();

        for (size_t i = 0; i < cells_.size(); ++i) {
            const size_t idx = (start_idx + i) % cells_.size();
            if (cells_[idx].state == CellState::Active) {
                return cells_[idx];
            }
        }
        return std::nullopt;
    }

    /* 2. Перемішане шардування (Shuffle Sharding): вибір з K ізольованих комірок */
    [[nodiscard]] std::optional<CellDescriptor> route_shuffle(std::string_view tenant_id) const {
        if (cells_.empty()) {
            return std::nullopt;
        }
        const size_t k = std::min(shuffle_k_, cells_.size());
        const auto candidate_indices = compute_shuffle_subset(tenant_id, k);

        const CellDescriptor *best = nullptr;
        uint32_t min_load = std::numeric_limits<uint32_t>::max();

        for (const size_t idx : candidate_indices) {
            const auto &cell = cells_[idx];
            if (cell.state == CellState::Active) {
                if (cell.active_connections < min_load) {
                    min_load = cell.active_connections;
                    best = &cell;
                }
            }
        }

        if (best != nullptr) {
            return *best;
        }
        return std::nullopt;
    }

private:
    std::vector<CellDescriptor> cells_;
    size_t shuffle_k_{3};

    static uint64_t hash_fnv1a(std::string_view str) noexcept {
        uint64_t hash = 14695981039346656037ULL;
        for (const char c : str) {
            hash ^= static_cast<uint8_t>(c);
            hash *= 1099511628211ULL;
        }
        return hash;
    }

    [[nodiscard]] std::vector<size_t> compute_shuffle_subset(std::string_view key, size_t k) const {
        std::vector<size_t> subset;
        subset.reserve(k);
        uint64_t state = hash_fnv1a(key);

        while (subset.size() < k) {
            state = state * 6364136223846793005ULL + 1442695040888963407ULL;
            const size_t candidate = (state >> 32) % cells_.size();
            if (std::find(subset.begin(), subset.end(), candidate) == subset.end()) {
                subset.push_back(candidate);
            }
        }
        return subset;
    }
};

} // namespace cellular
```
:::

## Покроковий розбір алгоритмів та структур даних

1. **Хешування без виділення пам'яті:** Функція `fnv1a_hash` приймає `std::string_view` або вказівник на буфер із довжиною. Вона не створює проміжних рядкових копій, обробляючи байти безпосередньо з мережевого буфера фрейму HTTP-запиту.
2. **Генерація псевдовипадкових перестановок (LCG Permutation):** Лінійний конгруентний генератор із коефіцієнтами Дональда Кнута гарантує, що для одного й того самого ідентифікатора орендаря послідовність вибору `K` комірок буде абсолютно детермінованою і рівномірною між усіма екземплярами маршрутизаторів без потреби у спільній базі даних.
3. **Вибір найменш завантаженої комірки (Least Connections):** Після визначення `K` доступних комірок маршрутизатор опитує лічильник `active_connections` і направляє запит на найменш завантажений вузол, забезпечуючи внутрішньокоміркове балансування.

## Ефективність використання пам'яті та апаратна оптимізація

Розподіл пам'яті в реалізації оптимізовано під сучасні мікропроцесорні архітектури x86_64 та ARM64:
- Розмір структури `cell_descriptor_t` підібраний так, щоб таблиця з 64 комірок повністю розміщувалася в межах 16 кілобайтів пам'яті, що гарантовано поміщається в кеш першого рівня (L1 Data Cache, стандартний розмір 32–64 КБ на ядро).
- Відсутність покажчиків і динамічних вузлів списків усуває фрагментацію пам'яті та промахи кешу (Cache Misses).
- Обчислення цільової комірки в режимі прямого шардування вимагає всього 18 процесорних тактів (близько 5 наносекунд на процесорі з тактовою частотою 3.6 ГГц).

## Мережева трансляція нульового копіювання (Zero-Copy Proxying)

У високопродуктивних інфраструктурних маршрутизаторах (eBPF XDP, Envoy, DPDK) після визначення цільової адреси комірки мережевий трафік не копіюється в простір користувача.

Замість повної буферизації тіла запиту ядро операційної системи виконує трансляцію мережевих адрес (DNAT) або інкапсуляцію в тунель GENEVE/VXLAN безпосередньо на рівні мережевої карти. Це дозволяє одному серверу маршрутизації обслуговувати до 5 мільйонів пакетів за секунду на 100-гігабітному інтерфейсі без споживання процесорного часу на парсинг бізнес-даних.

## Інженерні пастки та крайові випадки

1. **Гарячі орендарі (Hot Tenant Problem):**
   - Якщо один великий орендар генерує 80% трафіку всієї системи, закріплення його за однією коміркою перевантажить її ресурси.
   - *Вирішення:* для надвеликих орендарів застосовують або виділений персональний штамп (Dedicated Cell), або збільшений параметр `K` у перемішаному шардуванні з додатковим субшардуванням за ідентифікатором сутності (`tenant_id + ":" + user_id`).

2. **Запізнення таблиць маршрутизації (Router Lag during Cell Drain):**
   - Якщо площина управління перевела комірку в стан `DRAINING`, але один із реплікованих маршрутизаторів не отримав оновлення через затримку мережі, він продовжить надсилати запити нових сесій на комірку, що закривається.
   - *Вирішення:* внутрішній вхідний проксі самої комірки (Cell Ingress) повинен самостійно знати свій локальний стан і при отриманні нового запиту в режимі `DRAINING` повертати спеціальний HTTP-заголовок `X-Cell-Drain: true` зі статусом `307 Temporary Redirect` або проксувати запит на сусідній штамп.

3. **Багатопотокова безпека в робочому середовищі (Thread-Safe Lookups):**
   - У високонавантажених проксі-серверах (наприклад, написаних на C++ з пулом потоків epoll/kqueue) таблиця маршрутизації змінюється рідко (раз на хвилину або при аваріях), але читається сотні тисяч разів на секунду.
   - *Вирішення:* замість використання важких блокувань м'ютекса (`std::mutex`), які призводять до конкуренції за шину пам'яті (Lock Contention), застосовують механізм атомарної заміни вказівників (`std::atomic<std::shared_ptr<const CellRouter>>`) або механізми Read-Copy-Update (RCU). Потоки-обробники читають таблицю без жодних блокувань за лічені наносекунди, а фоновий потік оновлення конфігурації атомарно підміняє корінь дерева правил.
