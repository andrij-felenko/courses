# ⚙️ Реалізація рушія збіжних станів: векторні годинники, MV-регістр та OR-Set

Реалізація надійних розподілених сховищ вимагає переходу від теоретичних алгебраїчних структур до високоефективних структур даних у пам'яті, що коректно відстежують причинність, розв'язують паралельні конфлікти та очищають застарілі метадані.

У практичній інженерії виникає три ключові задачі:
1. **Відстеження причинності без центрального лічильника:** виявлення того, чи є один стан предком іншого, або ж вони виникли конкурентно в паралельних гілках історії;
2. **Збереження конкурентних гілок (Multi-Value):** недопущення мовчазного затирання даних за наявності паралельних модифікацій до моменту їхнього явного об'єднання;
3. **Підтримка динамічних множин із семантикою Add-Wins:** можливість вільного додавання та видалення елементів в офлайн-режимі без ризику незворотного блокування через застарілі надгробки.

Нижче наведено промислову реалізацію трьох фундаментальних будівельних блоків розподіленої збіжності з повним збереженням системних інваріантів.

---

### 1. Реалізація векторного годинника

Векторний годинник відображає ідентифікатор вузла (`node_id`) на монотонний цілочисельний лічильник. Порівняння двох векторів вимагає покомпонентної перевірки умови `∀ k: V_1[k] ≤ V_2[k]` з обов'язковою наявністю хоча б одного строго меншого елемента для встановлення строгого причинного порядку.

Якщо жоден із двох векторів не перекриває інший за всіма компонентами (наприклад, у першому векторі більша перша координата, а в другому — друга), функція повертає статус конкурентності (`VC_CONCURRENT` / `ClockRelation::Concurrent`), що сигналізує про виникнення конфлікту гілок.

:::tabs
```c
/* vector_clock.h / vector_clock.c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_NODES 16
#define ID_LEN 32

typedef struct {
    char node_id[ID_LEN];
    uint64_t counter;
} vc_entry_t;

typedef struct {
    vc_entry_t entries[MAX_NODES];
    size_t count;
} vector_clock_t;

typedef enum {
    VC_EQUAL,       /* V1 == V2 */
    VC_BEFORE,      /* V1 < V2  (V1 causal ancestor of V2) */
    VC_AFTER,       /* V1 > V2  (V1 causal descendant of V2) */
    VC_CONCURRENT   /* V1 || V2 (conflict / concurrent branch) */
} vc_relation_t;

void vc_init(vector_clock_t *vc) {
    vc->count = 0;
}

uint64_t vc_get(const vector_clock_t *vc, const char *node_id) {
    for (size_t i = 0; i < vc->count; ++i) {
        if (strncmp(vc->entries[i].node_id, node_id, ID_LEN) == 0) {
            return vc->entries[i].counter;
        }
    }
    return 0;
}

void vc_set(vector_clock_t *vc, const char *node_id, uint64_t val) {
    for (size_t i = 0; i < vc->count; ++i) {
        if (strncmp(vc->entries[i].node_id, node_id, ID_LEN) == 0) {
            vc->entries[i].counter = val;
            return;
        }
    }
    if (vc->count < MAX_NODES) {
        strncpy(vc->entries[vc->count].node_id, node_id, ID_LEN - 1);
        vc->entries[vc->count].node_id[ID_LEN - 1] = '\0';
        vc->entries[vc->count].counter = val;
        vc->count++;
    }
}

void vc_increment(vector_clock_t *vc, const char *node_id) {
    uint64_t cur = vc_get(vc, node_id);
    vc_set(vc, node_id, cur + 1);
}

void vc_merge(vector_clock_t *dst, const vector_clock_t *src) {
    for (size_t i = 0; i < src->count; ++i) {
        uint64_t cur = vc_get(dst, src->entries[i].node_id);
        if (src->entries[i].counter > cur) {
            vc_set(dst, src->entries[i].node_id, src->entries[i].counter);
        }
    }
}

vc_relation_t vc_compare(const vector_clock_t *a, const vector_clock_t *b) {
    bool a_has_greater = false;
    bool b_has_greater = false;

    /* Перевіряємо всі ключі з a */
    for (size_t i = 0; i < a->count; ++i) {
        uint64_t ca = a->entries[i].counter;
        uint64_t cb = vc_get(b, a->entries[i].node_id);
        if (ca > cb) a_has_greater = true;
        if (cb > ca) b_has_greater = true;
    }

    /* Перевіряємо ключі з b, яких могло не бути в a */
    for (size_t i = 0; i < b->count; ++i) {
        uint64_t cb = b->entries[i].counter;
        uint64_t ca = vc_get(a, b->entries[i].node_id);
        if (cb > ca) b_has_greater = true;
        if (ca > cb) a_has_greater = true;
    }

    if (!a_has_greater && !b_has_greater) return VC_EQUAL;
    if (a_has_greater && !b_has_greater)  return VC_AFTER;
    if (!a_has_greater && b_has_greater)  return VC_BEFORE;
    return VC_CONCURRENT;
}
```
```cpp
// VectorClock.hpp
#pragma once
#include <string>
#include <string_view>
#include <unordered_map>
#include <algorithm>
#include <cstdint>

enum class ClockRelation {
    Equal,       // A == B
    Before,      // A < B (A causal ancestor of B)
    After,       // A > B (A causal descendant of B)
    Concurrent   // A || B (Conflict)
};

class VectorClock {
public:
    using NodeId = std::string;
    using Counter = uint64_t;

    [[nodiscard]] Counter get(std::string_view node_id) const noexcept {
        auto it = clock_.find(std::string(node_id));
        return it != clock_.end() ? it->second : 0;
    }

    void set(std::string_view node_id, Counter value) {
        clock_[std::string(node_id)] = value;
    }

    Counter increment(std::string_view node_id) {
        return ++clock_[std::string(node_id)];
    }

    void merge(const VectorClock& other) {
        for (const auto& [node, count] : other.clock_) {
            clock_[node] = std::max(clock_[node], count);
        }
    }

    [[nodiscard]] ClockRelation compare(const VectorClock& other) const noexcept {
        bool this_greater = false;
        bool other_greater = false;

        for (const auto& [node, count] : clock_) {
            const auto other_count = other.get(node);
            if (count > other_count) this_greater = true;
            if (count < other_count) other_greater = true;
        }

        for (const auto& [node, other_count] : other.clock_) {
            if (!clock_.contains(node)) {
                if (other_count > 0) other_greater = true;
            }
        }

        if (!this_greater && !other_greater) return ClockRelation::Equal;
        if (this_greater && !other_greater)  return ClockRelation::After;
        if (!this_greater && other_greater)  return ClockRelation::Before;
        return ClockRelation::Concurrent;
    }

    [[nodiscard]] const std::unordered_map<NodeId, Counter>& entries() const noexcept {
        return clock_;
    }

private:
    std::unordered_map<NodeId, Counter> clock_;
};
```
:::

---

### 2. Багатозначний регістр (MV-Register)

MV-Register зберігає список пар `(значення, версійний_вектор)`. При встановленні нового значення клієнт передає свій поточний причинний контекст. 

Розгляньмо покроковий механізм витіснення застарілих версій:
1. **Ініціалізація:** клієнт читає стан регістра і отримує поточний вектор `VC_read`.
2. **Локальний запис:** клієнт відправляє нове значення `val_new` разом із `VC_read`. Регістр інкрементує позицію координатора у векторі: `VC_write = VC_read; VC_write[actor]++`.
3. **Фільтрація:** усі збережені версії, вектори яких задовольняють умову `VC_stored < VC_write`, визнаються причинними предками нового запису і негайно видаляються.
4. **Паралельні записи:** якщо в регістрі існують версії, для яких `VC_stored ∥ VC_write`, вони зберігаються поруч.

Під час операції `merge` регістр виконує двосторонній фільтр домінування: видаляються лише ті версії, для яких у протилежній репліці знайдено строго новішого причинного нащадка.

:::tabs
```cpp
// MVRegister.hpp
#pragma once
#include "VectorClock.hpp"
#include <vector>
#include <string>
#include <ranges>

template <typename T>
class MVRegister {
public:
    struct VersionedValue {
        T value;
        VectorClock clock;
    };

    // Запис нового значення із причинним контекстом клієнта
    void write(T value, const std::string& actor_id, VectorClock context) {
        context.increment(actor_id);
        
        std::vector<VersionedValue> next_versions;
        next_versions.push_back(VersionedValue{
            .value = std::move(value),
            .clock = context
        });

        // Залишаємо лише ті старі версії, які НЕ є предками нового запису
        for (auto& entry : versions_) {
            auto rel = entry.clock.compare(context);
            if (rel == ClockRelation::Concurrent || rel == ClockRelation::After) {
                next_versions.push_back(std::move(entry));
            }
        }
        versions_ = std::move(next_versions);
    }

    // Злиття станів двох MV-регістрів
    void merge(const MVRegister<T>& other) {
        std::vector<VersionedValue> merged;

        // Перевіряємо кожну версію з поточного регістра
        for (const auto& local : versions_) {
            bool overwritten = false;
            for (const auto& remote : other.versions_) {
                if (local.clock.compare(remote.clock) == ClockRelation::Before) {
                    overwritten = true;
                    break;
                }
            }
            if (!overwritten) {
                merged.push_back(local);
            }
        }

        // Додаємо віддалені версії, якщо вони не перезаписані локальними
        for (const auto& remote : other.versions_) {
            bool overwritten = false;
            for (const auto& local : versions_) {
                auto rel = remote.clock.compare(local.clock);
                if (rel == ClockRelation::Before || rel == ClockRelation::Equal) {
                    overwritten = true;
                    break;
                }
            }
            if (!overwritten) {
                merged.push_back(remote);
            }
        }

        versions_ = std::move(merged);
    }

    [[nodiscard]] std::vector<T> read() const {
        std::vector<T> result;
        result.reserve(versions_.size());
        for (const auto& v : versions_) {
            result.push_back(v.value);
        }
        return result;
    }

    [[nodiscard]] bool has_conflict() const noexcept {
        return versions_.size() > 1;
    }

private:
    std::vector<VersionedValue> versions_;
};
```
```c
/* mv_register.h / mv_register.c */
#include "vector_clock.h"

#define MAX_VERSIONS 8
#define MAX_VAL_LEN 64

typedef struct {
    char value[MAX_VAL_LEN];
    vector_clock_t clock;
} mvr_entry_t;

typedef struct {
    mvr_entry_t entries[MAX_VERSIONS];
    size_t count;
} mv_register_t;

void mvr_init(mv_register_t *reg) {
    reg->count = 0;
}

void mvr_write(mv_register_t *reg, const char *val, const char *actor, vector_clock_t ctx) {
    vc_increment(&ctx, actor);
    mvr_entry_t next[MAX_VERSIONS];
    size_t n_count = 0;

    /* Додаємо новий запис */
    strncpy(next[n_count].value, val, MAX_VAL_LEN - 1);
    next[n_count].value[MAX_VAL_LEN - 1] = '\0';
    next[n_count].clock = ctx;
    n_count++;

    /* Фільтруємо старі версії */
    for (size_t i = 0; i < reg->count; ++i) {
        vc_relation_t rel = vc_compare(&reg->entries[i].clock, &ctx);
        if (rel == VC_CONCURRENT || rel == VC_AFTER) {
            if (n_count < MAX_VERSIONS) {
                next[n_count++] = reg->entries[i];
            }
        }
    }

    memcpy(reg->entries, next, sizeof(mvr_entry_t) * n_count);
    reg->count = n_count;
}

void mvr_merge(mv_register_t *dst, const mv_register_t *src) {
    mvr_entry_t next[MAX_VERSIONS];
    size_t n_count = 0;

    for (size_t i = 0; i < dst->count; ++i) {
        bool dominated = false;
        for (size_t j = 0; j < src->count; ++j) {
            if (vc_compare(&dst->entries[i].clock, &src->entries[j].clock) == VC_BEFORE) {
                dominated = true;
                break;
            }
        }
        if (!dominated && n_count < MAX_VERSIONS) {
            next[n_count++] = dst->entries[i];
        }
    }

    for (size_t j = 0; j < src->count; ++j) {
        bool dominated = false;
        for (size_t i = 0; i < dst->count; ++i) {
            vc_relation_t rel = vc_compare(&src->entries[j].clock, &dst->entries[i].clock);
            if (rel == VC_BEFORE || rel == VC_EQUAL) {
                dominated = true;
                break;
            }
        }
        if (!dominated && n_count < MAX_VERSIONS) {
            next[n_count++] = src->entries[j];
        }
    }

    memcpy(dst->entries, next, sizeof(mvr_entry_t) * n_count);
    dst->count = n_count;
}
```
:::

---

### 3. Множина Observed-Remove Set (OR-Set)

В OR-Set кожна операція додавання елемента генерує унікальну точку `Dot = (actor_id, counter)`. При видаленні елемента вузол переміщує всі локально спостережені точки цього елемента в набір видалених (`tombstones`). 

Якщо інший вузол паралельно згенерував нову точку для того ж елемента, вона не входить у набір видалення і виживає при злитті. Це забезпечує семантику Add-Wins без глобальних блокувань.

Структура даних підтримує видалення елементів із подальшим їхнім безпечним повторним додаванням: кожна нова ітерація отримує свіжий ідентифікатор точки, не підвладний раніше записаним надгробкам.

:::tabs
```cpp
// ORSet.hpp
#pragma once
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <cstdint>

struct Dot {
    std::string actor;
    uint64_t counter{0};

    bool operator==(const Dot& other) const noexcept {
        return counter == other.counter && actor == other.actor;
    }
};

struct DotHash {
    size_t operator()(const Dot& d) const noexcept {
        return std::hash<std::string>{}(d.actor) ^ (std::hash<uint64_t>{}(d.counter) << 1);
    }
};

template <typename T>
class ORSet {
public:
    explicit ORSet(std::string actor_id) : actor_(std::move(actor_id)) {}

    // Додавання елемента: створюємо новий причинний Dot
    void add(const T& element) {
        Dot dot{ .actor = actor_, .counter = ++local_counter_ };
        elements_[element].insert(dot);
    }

    // Видалення елемента: додаємо всі поточні Dots у надгробки
    void remove(const T& element) {
        auto it = elements_.find(element);
        if (it != elements_.end()) {
            for (const auto& dot : it->second) {
                tombstones_.insert(dot);
            }
            elements_.erase(it);
        }
    }

    // Читання активних елементів
    [[nodiscard]] std::vector<T> read() const {
        std::vector<T> active;
        for (const auto& [elem, dots] : elements_) {
            bool has_alive_dot = false;
            for (const auto& dot : dots) {
                if (!tombstones_.contains(dot)) {
                    has_alive_dot = true;
                    break;
                }
            }
            if (has_alive_dot) {
                active.push_back(elem);
            }
        }
        return active;
    }

    // Злиття за законами напівґратки
    void merge(const ORSet<T>& other) {
        // 1. Об'єднуємо надгробки
        tombstones_.insert(other.tombstones_.begin(), other.tombstones_.end());

        // 2. Об'єднуємо елементи та їхні Dots
        for (const auto& [elem, remote_dots] : other.elements_) {
            elements_[elem].insert(remote_dots.begin(), remote_dots.end());
        }

        // 3. Локальний лічильник оновлюємо до максимуму
        local_counter_ = std::max(local_counter_, other.local_counter_);

        // 4. Очищення елементів, усі точки яких потрапили в надгробки
        for (auto it = elements_.begin(); it != elements_.end(); ) {
            std::erase_if(it->second, [this](const Dot& d) {
                return tombstones_.contains(d);
            });
            if (it->second.empty()) {
                it = elements_.erase(it);
            } else {
                ++it;
            }
        }
    }

private:
    std::string actor_;
    uint64_t local_counter_{0};
    std::unordered_map<T, std::unordered_set<Dot, DotHash>> elements_;
    std::unordered_set<Dot, DotHash> tombstones_;
};
```
```c
/* or_set.h / or_set.c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_ITEMS 32
#define MAX_DOTS 64
#define STR_LEN 32

typedef struct {
    char actor[STR_LEN];
    uint64_t counter;
} dot_t;

typedef struct {
    char element[STR_LEN];
    dot_t dots[MAX_DOTS];
    size_t dot_count;
} or_item_t;

typedef struct {
    char actor[STR_LEN];
    uint64_t counter;
    or_item_t items[MAX_ITEMS];
    size_t item_count;
    dot_t tombstones[MAX_DOTS * 2];
    size_t tomb_count;
} or_set_t;

void or_init(or_set_t *set, const char *actor) {
    strncpy(set->actor, actor, STR_LEN - 1);
    set->actor[STR_LEN - 1] = '\0';
    set->counter = 0;
    set->item_count = 0;
    set->tomb_count = 0;
}

static bool dot_in_tombstones(const or_set_t *set, const dot_t *d) {
    for (size_t i = 0; i < set->tomb_count; ++i) {
        if (set->tombstones[i].counter == d->counter &&
            strncmp(set->tombstones[i].actor, d->actor, STR_LEN) == 0) {
            return true;
        }
    }
    return false;
}

void or_add(or_set_t *set, const char *elem) {
    dot_t d;
    strncpy(d.actor, set->actor, STR_LEN - 1);
    d.actor[STR_LEN - 1] = '\0';
    d.counter = ++set->counter;

    for (size_t i = 0; i < set->item_count; ++i) {
        if (strncmp(set->items[i].element, elem, STR_LEN) == 0) {
            if (set->items[i].dot_count < MAX_DOTS) {
                set->items[i].dots[set->items[i].dot_count++] = d;
            }
            return;
        }
    }

    if (set->item_count < MAX_ITEMS) {
        strncpy(set->items[set->item_count].element, elem, STR_LEN - 1);
        set->items[set->item_count].element[STR_LEN - 1] = '\0';
        set->items[set->item_count].dots[0] = d;
        set->items[set->item_count].dot_count = 1;
        set->item_count++;
    }
}

void or_remove(or_set_t *set, const char *elem) {
    for (size_t i = 0; i < set->item_count; ++i) {
        if (strncmp(set->items[i].element, elem, STR_LEN) == 0) {
            for (size_t j = 0; j < set->items[i].dot_count; ++j) {
                if (set->tomb_count < MAX_DOTS * 2) {
                    set->tombstones[set->tomb_count++] = set->items[i].dots[j];
                }
            }
            /* Видаляємо елемент зміщенням масиву */
            set->items[i] = set->items[--set->item_count];
            return;
        }
    }
}
```
:::

---

### 4. Тестування детермінованої збіжності

Для валідації властивостей напівґратки застосовується метод генерації випадкових перестановок мережевих повідомлень (Property-based Testing):

1. **Створення кластера реплік:** ініціалізується три екземпляри структури даних (`R_A`, `R_B`, `R_C`).
2. **Генерація конкурентних дій:** кожна репліка в ізоляції виконує серію мутацій (додавання однакових ключів із різними значеннями, паралельне видалення, оновлення лічильників).
3. **Емуляція хаотичної мережі:** генеруються всі можливі перестановки викликів `merge` між парами реплік із довільними затримками, дублюванням пакетів та повторними злиттями.
4. **Верифікація тотожності:** після завершення всіх циклів обміну перевіряється інваріант:
```
∀ π_1, π_2: state(π_1) == state(π_2)
```
Будь-яка розбіжність у кінцевих даних свідчить про порушення комутативності, асоціативності або ідемпотентності оператора `⊔`.

---

### 5. Інженерні пастки та експлуатаційні ризики

1. **Роздування надгробків (Tombstones Accumulation):**
   У довгоживучих системах на базі OR-Set множина `tombstones` безперервно росте, перевищуючи розмір корисних даних у сотні разів.
   *Розв'язок:* впровадження причинного контексту на базі стисненого векторного годинника (Dotted Version Vectors, DVV). Якщо вектор підтверджує, що всі вузли застосували видалення до кроку `K`, усі надгробки з `counter ≤ K` безпечно видаляються з пам'яті під час періодичного сміттєзбору (Garbage Collection).

2. **Динамічний склад вузлів (Actor Churn):**
   Використання випадкових UUID як `actor_id` для кожного клієнтського запиту призводить до того, що довжина вектора `VectorClock` прямує до нескінченності. Вектори мусять прив'язуватися до стабільних ідентифікаторів реплік/шардів (наприклад, 3–7 фіксованих координаторів у кластері).

3. **Неподільні ресурси та гонки за ліміти:**
   Спроба використання CRDT для лічильників з обмеженням `val ≥ 0` (наприклад, складський залишок або баланс рахунку) веде до тихого перевитрачання ресурсу (overselling). Для таких операцій обов'язково потрібен розподілений консенсус або механізм резервування квот.

---

### 6. Аналіз часової та просторової складності

Для оцінки ефективності розроблених структур наведемо аналіз асимптотичної складності ключових операцій:

* **Векторний годинник (Vector Clock):**
  * Пам'ять: `O(N)`, де `N` — кількість активних вузлів.
  * Час операції `increment`: `O(1)` в C++ (хеш-таблиця) або `O(N)` у компактному масиві на C.
  * Час порівняння `compare`: `O(N)` повний прохід по елементах обох векторів.

* **Багатозначний регістр (MV-Register):**
  * Пам'ять: `O(K · N)`, де `K` — кількість паралельних конкурентних версій (siblings), `N` — розмір вектора. У стабільному стані `K = 1`, під час тривалого мережевого розриву `K` тимчасово зростає.
  * Час операції `write`: `O(K · N)` для фільтрації предків.
  * Час операції `merge`: `O(K_1 · K_2 · N)` попарне порівняння векторів обох реплік.

* **Множина Observed-Remove Set (OR-Set):**
  * Пам'ять: `O(E · D + T)`, де `E` — кількість унікальних елементів, `D` — середня кількість активних точок на елемент, `T` — накопичена кількість надгробків до очищення.
  * Час операції `add`: `O(1)` амортизовано.
  * Час операції `remove`: `O(D)` переміщення точок у надгробки.
  * Час операції `merge`: `O(S_1 + S_2)` об'єднання хеш-множин.
