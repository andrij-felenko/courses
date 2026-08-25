# ⚙️ Реалізація хеш-таблиці зозулі зі схованкою та перехешуванням

Створення надійної та продуктивної хеш-таблиці зозулі вимагає ретельного інженерного балансування між швидкістю доступу, простотою коду та надійністю обробки колізій. На відміну від класичних підходів із відкритим пробуванням, де головною турботою є уникнення первинної та вторинної кластеризації навколо популярних комірок, у хешуванні зозулею центральне місце посідає управління ланцюжком витіснень (displacement chain), надійне виявлення зациклень, захист від пробуксовки (thrashing) та безшовне перехешування.

Нижче детально розібрано архітектуру повнофункціональної таблиці «ключ — значення», оптимізованої для швидкої константної вибірки з гарантованим часом відгуку. Структура спирається на дві таблиці `T₁` і `T₂` однакового розміру `capacity` та додаткову статичну схованку (stash) на 4 елементи.

## Архітектура пам'яті та хеш-функції

Кожен запис у таблиці представлений структурою `CuckooEntry`, яка містить 64-бітний цілочисельний ключ, 64-бітне значення та логічний прапорець зайнятості слота. Вирівнювання структури до 24 байтів забезпечує швидке копіювання в регістрах сучасного 64-бітного процесора.

Для генерації двох незалежних адрес використовується 64-бітний алгоритм перемішування бітів SplitMix64. Він вирізняється надзвичайно низькою обчислювальною вартістю (усього кілька операцій множення, зсуву та виключного АБО) і відмінними лавинними властивостями: зміна навіть одного біта вхідного ключа змінює кожен вихідний біт з імовірністю близько 50%. Застосування двох різних початкових констант (seeds) гарантує взаємну статистичну незалежність обох хеш-функцій `h₁` та `h₂`, що є фундаментальною передумовою для уникнення надлишкових циклів витіснення.

:::tabs
```c
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define STASH_CAPACITY 4
#define MAX_DISPLACEMENTS_FACTOR 2

typedef struct {
    uint64_t key;
    uint64_t value;
    bool occupied;
} CuckooEntry;

typedef struct {
    CuckooEntry *t1;
    CuckooEntry *t2;
    CuckooEntry stash[STASH_CAPACITY];
    size_t capacity;      /* розмір кожної з таблиць T1 і T2 */
    size_t size;          /* загальна кількість збережених елементів */
    uint64_t seed1;
    uint64_t seed2;
} CuckooMap;

/* 64-бітне швидке хешування SplitMix64 з домішуванням зерна */
static inline uint64_t hash_splitmix(uint64_t x, uint64_t seed) {
    uint64_t z = (x + seed + 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

static inline size_t index1(const CuckooMap *map, uint64_t key) {
    return (size_t)(hash_splitmix(key, map->seed1) % map->capacity);
}

static inline size_t index2(const CuckooMap *map, uint64_t key) {
    return (size_t)(hash_splitmix(key, map->seed2) % map->capacity);
}

CuckooMap *cuckoo_create(size_t initial_capacity) {
    if (initial_capacity < 8) initial_capacity = 8;
    CuckooMap *map = (CuckooMap *)malloc(sizeof(CuckooMap));
    if (!map) return NULL;

    map->capacity = initial_capacity;
    map->size = 0;
    map->seed1 = 0x8A5CD789ULL;
    map->seed2 = 0xF3B291A4ULL;

    map->t1 = (CuckooEntry *)calloc(map->capacity, sizeof(CuckooEntry));
    map->t2 = (CuckooEntry *)calloc(map->capacity, sizeof(CuckooEntry));
    if (!map->t1 || !map->t2) {
        free(map->t1);
        free(map->t2);
        free(map);
        return NULL;
    }
    memset(map->stash, 0, sizeof(map->stash));
    return map;
}

void cuckoo_destroy(CuckooMap *map) {
    if (!map) return;
    free(map->t1);
    free(map->t2);
    free(map);
}
```
```cpp
#include <array>
#include <cstdint>
#include <optional>
#include <random>
#include <utility>
#include <vector>

template <typename Key = uint64_t, typename Value = uint64_t>
class CuckooMap {
public:
    static constexpr size_t StashCapacity = 4;
    static constexpr size_t MaxDisplacementsFactor = 2;

    struct Entry {
        Key key{};
        Value value{};
        bool occupied{false};
    };

    explicit CuckooMap(size_t initial_capacity = 16)
        : capacity_(std::max<size_t>(initial_capacity, 8)), size_(0) {
        std::random_device rd;
        seed1_ = (static_cast<uint64_t>(rd()) << 32) | rd();
        seed2_ = (static_cast<uint64_t>(rd()) << 32) | rd();
        t1_.resize(capacity_);
        t2_.resize(capacity_);
    }

    [[nodiscard]] size_t size() const noexcept { return size_; }
    [[nodiscard]] size_t capacity() const noexcept { return capacity_ * 2; }
    [[nodiscard]] bool empty() const noexcept { return size_ == 0; }

private:
    std::vector<Entry> t1_;
    std::vector<Entry> t2_;
    std::array<Entry, StashCapacity> stash_{};
    size_t capacity_;
    size_t size_;
    uint64_t seed1_;
    uint64_t seed2_;

    static uint64_t splitmix(uint64_t x, uint64_t seed) noexcept {
        uint64_t z = (x + seed + 0x9E3779B97F4A7C15ULL);
        z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
        z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
        return z ^ (z >> 31);
    }

    [[nodiscard]] size_t index1(const Key &k) const noexcept {
        return static_cast<size_t>(splitmix(static_cast<uint64_t>(k), seed1_) % capacity_);
    }

    [[nodiscard]] size_t index2(const Key &k) const noexcept {
        return static_cast<size_t>(splitmix(static_cast<uint64_t>(k), seed2_) % capacity_);
    }
};
```
:::

У варіанті для мови C виділення пам'яті здійснюється через системну функцію `calloc`, яка автоматично обнуляє виділені масиви та ініціалізує всі прапорці `occupied = false`. У версії на C++ застосовується ідіоматичний клас-шаблон `std::vector<Entry>` з керуванням ресурсами через парадигму RAII (Resource Acquisition Is Initialization), що повністю унеможливлює витоки динамічної пам'яті при виникненні винятків чи передчасному виході з області видимості.

## Детермінований пошук без зондування

Операція пошуку — це головна архітектурна перевага хешування зозулею над усіма іншими різновидами відкритої адресації. Алгоритм не виконує циклічного перебору сусідніх комірок, не обчислює кроків вторинного хешування і не перевіряє маркерів видалення.

Логіка пошуку складається з трьох детермінованих кроків:
1. **Перший слот:** Обчислюємо індекс `i₁ = index1(key)` і перевіряємо стан комірки `t1[i₁]`. Якщо слот зайнятий і ключ точно збігається з шуканим — асоційоване значення знайдено миттєво.
2. **Другий слот:** Якщо в першій таблиці ключ відсутній, обчислюємо індекс `i₂ = index2(key)` і перевіряємо комірку `t2[i₂]`. Якщо ключ збігається — значення повертається.
3. **Схованка:** Якщо ключ не знайдено в жодній із двох основних таблиць, перевіряємо статичну схованку `stash`, яка містить рівно 4 слоти (що відповідає лінійному проходу по кількох регістрах процесора).

Якщо ключ відсутній у цих трьох місцях, ми отримуємо 100% математичну гарантію того, що елемента немає в усій структурі даних.

:::tabs
```c
bool cuckoo_find(const CuckooMap *map, uint64_t key, uint64_t *out_value) {
    if (!map || map->size == 0) return false;

    /* 1. Перевірка першої таблиці */
    size_t i1 = index1(map, key);
    if (map->t1[i1].occupied && map->t1[i1].key == key) {
        if (out_value) *out_value = map->t1[i1].value;
        return true;
    }

    /* 2. Перевірка другої таблиці */
    size_t i2 = index2(map, key);
    if (map->t2[i2].occupied && map->t2[i2].key == key) {
        if (out_value) *out_value = map->t2[i2].value;
        return true;
    }

    /* 3. Перевірка схованки (фіксовані 4 слоти) */
    for (size_t s = 0; s < STASH_CAPACITY; ++s) {
        if (map->stash[s].occupied && map->stash[s].key == key) {
            if (out_value) *out_value = map->stash[s].value;
            return true;
        }
    }

    return false;
}
```
```cpp
public:
    [[nodiscard]] std::optional<Value> find(const Key &key) const {
        if (size_ == 0) return std::nullopt;

        // 1. Перевірка слота в першій таблиці
        const size_t i1 = index1(key);
        if (t1_[i1].occupied && t1_[i1].key == key) {
            return t1_[i1].value;
        }

        // 2. Перевірка слота в другій таблиці
        const size_t i2 = index2(key);
        if (t2_[i2].occupied && t2_[i2].key == key) {
            return t2_[i2].value;
        }

        // 3. Перевірка схованки
        for (const auto &slot : stash_) {
            if (slot.occupied && slot.key == key) {
                return slot.value;
            }
        }

        return std::nullopt;
    }
```
:::

У C++ версії метод повертає `std::optional<Value>`, що дозволяє природно та безпечно розрізняти ситуацію відсутності ключа та наявність збереженого значення, яке дорівнює нулю, без використання додаткових вихідних покажчиків чи магічних числових констант.

## Видалення без маркерів надгробків

У класичному лінійному або подвійному хешуванні видалення елемента вимагає залишати в комірці спеціальний фіктивний запис — «надгробок» (tombstone). Це необхідно, щоб наступні операції пошуку не зупинялися на цій порожній комірці передчасно, думаючи, що ланцюжок зондування завершився. З часом накопичення надгробків забруднює таблицю і вимагає періодичного очищення й реорганізації.

У хешуванні зозулею поняття ланцюжка зондування відсутнє як таке: кожен ключ завжди живе тільки у двох своїх законних домівках. Якщо елемент видаляється, його комірка просто позначається як вільна (`occupied = false`), а лічильник `size` зменшується.

:::tabs
```c
bool cuckoo_erase(CuckooMap *map, uint64_t key) {
    if (!map || map->size == 0) return false;

    size_t i1 = index1(map, key);
    if (map->t1[i1].occupied && map->t1[i1].key == key) {
        map->t1[i1].occupied = false;
        map->size--;
        return true;
    }

    size_t i2 = index2(map, key);
    if (map->t2[i2].occupied && map->t2[i2].key == key) {
        map->t2[i2].occupied = false;
        map->size--;
        return true;
    }

    for (size_t s = 0; s < STASH_CAPACITY; ++s) {
        if (map->stash[s].occupied && map->stash[s].key == key) {
            map->stash[s].occupied = false;
            map->size--;
            return true;
        }
    }

    return false;
}
```
```cpp
public:
    bool erase(const Key &key) {
        if (size_ == 0) return false;

        const size_t i1 = index1(key);
        if (t1_[i1].occupied && t1_[i1].key == key) {
            t1_[i1].occupied = false;
            --size_;
            return true;
        }

        const size_t i2 = index2(key);
        if (t2_[i2].occupied && t2_[i2].key == key) {
            t2_[i2].occupied = false;
            --size_;
            return true;
        }

        for (auto &slot : stash_) {
            if (slot.occupied && slot.key == key) {
                slot.occupied = false;
                --size_;
                return true;
            }
        }

        return false;
    }
```
:::

Звільнений у такий спосіб слот миттєво стає доступним як точка зупинки для майбутніх ланцюжків витіснення під час наступних вставок.

## Покрокове витіснення та перехешування

Операція вставки втілює класичну поведінку пташеняти зозулі, розгортаючи динамічний ланцюжок переселень:
1. **Перевірка на оновлення:** Спочатку перевіряємо, чи ключ уже присутній у структурі. Якщо так, оновлюємо значення та повертаємо `true`.
2. **Первинне поселення:** Новий елемент намагається зайняти слот `T₁[h₁(x)]`. Якщо слот вільний — вставка завершена за один крок.
3. **Естафета витіснень:** Якщо слот зайнятий елементом `y`, новий елемент записується на його місце, а `y` стає «жертвою» (victim) і спрямовується у свій альтернативний слот `T₂[h₂(y)]`. Якщо цей слот теж зайнятий елементом `z`, `z` витісняється у свою альтернативну позицію в `T₁`, і процес продовжується.
4. **Контроль зациклення:** Щоб уникнути нескінченного циклу у випадку утворення біциклічної топології в графі колізій, кількість витіснень обмежується порогом `max_steps = capacity · 2`.
5. **Схованка як рятівний круг:** Якщо ліміт кроків вичерпано, витіснений елемент поміщається у вільний слот схованки `stash`. Це рятує систему від дорогого перехешування при локальних збігах.
6. **Динамічне перехешування:** Якщо і схованка виявляється повністю заповненою, таблиця подвоює розмір (`capacity · 2`), генерує нові випадкові зерна хешування та послідовно перевставляє всі збережені елементи.

:::tabs
```c
static bool cuckoo_insert_entry(CuckooMap *map, CuckooEntry curr);

static bool cuckoo_rehash(CuckooMap *map, size_t new_capacity) {
    CuckooEntry *old_t1 = map->t1;
    CuckooEntry *old_t2 = map->t2;
    CuckooEntry old_stash[STASH_CAPACITY];
    memcpy(old_stash, map->stash, sizeof(old_stash));
    size_t old_cap = map->capacity;

    map->t1 = (CuckooEntry *)calloc(new_capacity, sizeof(CuckooEntry));
    map->t2 = (CuckooEntry *)calloc(new_capacity, sizeof(CuckooEntry));
    if (!map->t1 || !map->t2) {
        free(map->t1);
        free(map->t2);
        map->t1 = old_t1;
        map->t2 = old_t2;
        return false;
    }
    memset(map->stash, 0, sizeof(map->stash));
    map->capacity = new_capacity;
    map->size = 0;
    map->seed1 += 0x9E3779B9ULL;
    map->seed2 += 0xC6A4A793ULL;

    /* Перевставка всіх елементів з попередніх масивів */
    for (size_t i = 0; i < old_cap; ++i) {
        if (old_t1[i].occupied) cuckoo_insert_entry(map, old_t1[i]);
        if (old_t2[i].occupied) cuckoo_insert_entry(map, old_t2[i]);
    }
    for (size_t s = 0; s < STASH_CAPACITY; ++s) {
        if (old_stash[s].occupied) cuckoo_insert_entry(map, old_stash[s]);
    }

    free(old_t1);
    free(old_t2);
    return true;
}

static bool cuckoo_insert_entry(CuckooMap *map, CuckooEntry curr) {
    size_t max_steps = map->capacity * MAX_DISPLACEMENTS_FACTOR;

    for (size_t step = 0; step < max_steps; ++step) {
        /* Спроба помістити в T1 */
        size_t i1 = index1(map, curr.key);
        if (!map->t1[i1].occupied) {
            map->t1[i1] = curr;
            map->size++;
            return true;
        }

        /* Витіснення з T1 */
        CuckooEntry victim1 = map->t1[i1];
        map->t1[i1] = curr;
        curr = victim1;

        /* Спроба помістити витісненого в T2 */
        size_t i2 = index2(map, curr.key);
        if (!map->t2[i2].occupied) {
            map->t2[i2] = curr;
            map->size++;
            return true;
        }

        /* Витіснення з T2 */
        CuckooEntry victim2 = map->t2[i2];
        map->t2[i2] = curr;
        curr = victim2;
    }

    /* Ліміт витіснень вичерпано: пробуємо покласти в схованку */
    for (size_t s = 0; s < STASH_CAPACITY; ++s) {
        if (!map->stash[s].occupied) {
            map->stash[s] = curr;
            map->size++;
            return true;
        }
    }

    /* Схованка заповнена: потрібне перехешування */
    if (!cuckoo_rehash(map, map->capacity * 2)) {
        return false;
    }
    return cuckoo_insert_entry(map, curr);
}

bool cuckoo_insert(CuckooMap *map, uint64_t key, uint64_t value) {
    if (!map) return false;

    /* Якщо ключ уже існує — оновлюємо значення */
    size_t i1 = index1(map, key);
    if (map->t1[i1].occupied && map->t1[i1].key == key) {
        map->t1[i1].value = value;
        return true;
    }
    size_t i2 = index2(map, key);
    if (map->t2[i2].occupied && map->t2[i2].key == key) {
        map->t2[i2].value = value;
        return true;
    }
    for (size_t s = 0; s < STASH_CAPACITY; ++s) {
        if (map->stash[s].occupied && map->stash[s].key == key) {
            map->stash[s].value = value;
            return true;
        }
    }

    CuckooEntry entry = { .key = key, .value = value, .occupied = true };
    return cuckoo_insert_entry(map, entry);
}
```
```cpp
public:
    bool insert(const Key &key, const Value &value) {
        // Оновлення значення, якщо ключ уже присутній
        const size_t i1 = index1(key);
        if (t1_[i1].occupied && t1_[i1].key == key) {
            t1_[i1].value = value;
            return true;
        }
        const size_t i2 = index2(key);
        if (t2_[i2].occupied && t2_[i2].key == key) {
            t2_[i2].value = value;
            return true;
        }
        for (auto &slot : stash_) {
            if (slot.occupied && slot.key == key) {
                slot.value = value;
                return true;
            }
        }

        Entry current{key, value, true};
        return insert_entry(current);
    }

private:
    bool insert_entry(Entry current) {
        const size_t max_steps = capacity_ * MaxDisplacementsFactor;

        for (size_t step = 0; step < max_steps; ++step) {
            // Спроба вставки в T1
            const size_t p1 = index1(current.key);
            if (!t1_[p1].occupied) {
                t1_[p1] = current;
                ++size_;
                return true;
            }
            std::swap(t1_[p1], current);

            // Спроба вставки в T2
            const size_t p2 = index2(current.key);
            if (!t2_[p2].occupied) {
                t2_[p2] = current;
                ++size_;
                return true;
            }
            std::swap(t2_[p2], current);
        }

        // Розміщення в схованці при перевищенні ліміту витіснень
        for (auto &slot : stash_) {
            if (!slot.occupied) {
                slot = current;
                ++size_;
                return true;
            }
        }

        // Перехешування та подвоєння місткості
        rehash(capacity_ * 2);
        return insert_entry(current);
    }

    void rehash(size_t new_capacity) {
        std::vector<Entry> old_t1 = std::move(t1_);
        std::vector<Entry> old_t2 = std::move(t2_);
        std::array<Entry, StashCapacity> old_stash = stash_;

        capacity_ = new_capacity;
        size_ = 0;
        seed1_ += 0x9E3779B9ULL;
        seed2_ += 0xC6A4A793ULL;

        t1_.assign(capacity_, Entry{});
        t2_.assign(capacity_, Entry{});
        stash_.fill(Entry{});

        for (const auto &entry : old_t1) {
            if (entry.occupied) insert_entry(entry);
        }
        for (const auto &entry : old_t2) {
            if (entry.occupied) insert_entry(entry);
        }
        for (const auto &entry : old_stash) {
            if (entry.occupied) insert_entry(entry);
        }
    }
```
:::

Зверніть увагу на лаконічність C++ реалізації: виклик `std::swap` одночасно записує новий елемент у комірку та витягує старого мешканця в змінну `current`, позбавляючи потреби у тимчасових змінних жертви.

## Верифікація коректності та тестування

Для підтвердження повної працездатності коду розроблено тестовий сценарій, який послідовно виконує:
1. Вставку 10 000 унікальних числових ключів із багаторазовим динамічним розширенням таблиці та численними витісненнями.
2. Повну верифікацію наявності кожного вставленого ключа та перевірку правильності збереженого значення.
3. Масове видалення всіх непарних ключів (рівно 5 000 записів).
4. Фінальну верифікацію: перевірку, що всі парні ключі залишилися недоторканими, а всі непарні — гарантовано відсутні.

:::tabs
```c
int main(void) {
    CuckooMap *map = cuckoo_create(16);
    if (!map) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return 1;
    }

    const uint64_t N = 10000;
    for (uint64_t k = 1; k <= N; ++k) {
        if (!cuckoo_insert(map, k, k * 10)) {
            fprintf(stderr, "Збій вставки ключа %llu\n", (unsigned long long)k);
            cuckoo_destroy(map);
            return 1;
        }
    }

    /* Перевірка наявності */
    for (uint64_t k = 1; k <= N; ++k) {
        uint64_t val = 0;
        if (!cuckoo_find(map, k, &val) || val != k * 10) {
            fprintf(stderr, "Збій пошуку ключа %llu\n", (unsigned long long)k);
            cuckoo_destroy(map);
            return 1;
        }
    }

    /* Перевірка видалення половини елементів */
    for (uint64_t k = 1; k <= N; k += 2) {
        cuckoo_erase(map, k);
    }

    for (uint64_t k = 1; k <= N; ++k) {
        uint64_t val = 0;
        bool found = cuckoo_find(map, k, &val);
        if (k % 2 != 0 && found) {
            fprintf(stderr, "Помилка: видалений ключ %llu знайдено\n", (unsigned long long)k);
            cuckoo_destroy(map);
            return 1;
        }
        if (k % 2 == 0 && (!found || val != k * 10)) {
            fprintf(stderr, "Помилка: збережений ключ %llu не знайдено\n", (unsigned long long)k);
            cuckoo_destroy(map);
            return 1;
        }
    }

    printf("Усі тести хешування зозулею пройдено успішно. Розмір: %zu, Місткість: %zu\n",
           map->size, map->capacity * 2);
    cuckoo_destroy(map);
    return 0;
}
```
```cpp
#include <iostream>

int main() {
    CuckooMap<uint64_t, uint64_t> map(16);
    constexpr uint64_t N = 10000;

    for (uint64_t k = 1; k <= N; ++k) {
        map.insert(k, k * 10);
    }

    for (uint64_t k = 1; k <= N; ++k) {
        auto val = map.find(k);
        if (!val.has_value() || *val != k * 10) {
            std::cerr << "Помилка пошуку ключа " << k << '\n';
            return 1;
        }
    }

    for (uint64_t k = 1; k <= N; k += 2) {
        map.erase(k);
    }

    for (uint64_t k = 1; k <= N; ++k) {
        auto val = map.find(k);
        if (k % 2 != 0 && val.has_value()) {
            std::cerr << "Помилка: видалений ключ " << k << " знайдено\n";
            return 1;
        }
        if (k % 2 == 0 && (!val.has_value() || *val != k * 10)) {
            std::cerr << "Помилка: збережений ключ " << k << " не знайдено\n";
            return 1;
        }
    }

    std::cout << "Усі C++ тести пройдено. Розмір: " << map.size()
              << ", Місткість: " << map.capacity() << '\n';
    return 0;
}
```
:::

## Стратегії обходу: DFS проти BFS

У наведеній вище базовій реалізації застосовано жадібний обхід у глибину (Depth-First Search, DFS): кожен витіснений елемент негайно намагається поселитися у свій альтернативний слот, безпосередньо перезаписуючи дані в пам'яті. Це простий і компактний підхід, проте він має недолік: якщо на шляху виникає цикл, алгоритм може виконати десятки марних перезаписів у пам'ять до того, як зафіксує перевищення ліміту `max_steps`.

У промислових бібліотеках (зокрема `libcuckoo` від університету Карнегі — Меллона) застосовують обхід у ширину (Breadth-First Search, BFS):
1. **Фаза планування шляху:** Алгоритм будує дерево можливих витіснень у тимчасовій невеликій черзі, не змінюючи саму хеш-таблицю.
2. **Знаходження найкоротшого шляху:** BFS гарантовано знаходить найкоротшу послідовність переміщень до найближчого вільного слота.
3. **Атомарне виконання:** Знайдений шлях переміщень застосовується з кінця до початку (від вільного слота до точки входу). Це забезпечує мінімальну кількість операцій запису в пам'ять і робить алгоритм надзвичайно стійким у багатопотокових середовищах.

## Типові підводні камені та оптимізації продуктивності

Практична експлуатація хеш-таблиці зозулі в навантажених сервісах вимагає врахування таких тонкощів:
- **Запобігання пробуксовці (Thrashing):** Якщо коефіцієнт заповнення наближається до 50% у 2-хешовій таблиці з розміром кошика `b = 1`, середня довжина ланцюжка витіснень зростає експоненційно. На практиці автоматичне подвоєння таблиці налаштовують на поріг `α = 40–45%`, щоб зберігати швидкість вставок на рівні кількох тактів.
- **Підтримка блокових кошиків (Bucketing):** Для досягнення коефіцієнта заповнення 90%+ кожен елемент `t1` та `t2` перетворюють на кошик із 4 слотів. Усі 4 слоти кошика розташовують поруч у суцільній пам'яті, щоб процесор зчитував їх єдиним 64-байтовим кеш-рядком за одне звернення до L1/L2-кешу.
- **Порядок паралельних запитів:** У багатопотокових середовищах операція пошуку може виконуватися паралельно з операціями витіснення без блокувань читання (lock-free read), якщо запис нового значення виконується атомарно до очищення старого слота, а читач перевіряє `T₁`, `T₂` та `stash` у строго визначеному порядку.
