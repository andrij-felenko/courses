# ⚙️ Реалізація пропускного списку на C та C++

У цій практичній роботі побудовано повнофункціональний виробничий пропускний список (англ. *Skip List*) із підтримкою вставки, пошуку, видалення, діапазонного сканування, валідації інваріантів та ітерування.

Код представлено двома паралельними ідіоматичними реалізаціями:
1. **C (C11):** низькорівнева високопродуктивна структура з єдиним блоком виділення пам'яті під вузол і гнучким масивом покажчиків `forward[]`, побітовою генерацією рівня з імовірністю `p = 1/4` та функцією зворотного виклику для діапазонних вибірок.
2. **C++ (C++20):** узагальнений шаблонний клас `SkipList<Key, Value, Compare>` із семантикою значень, поверненням `std::optional`, безпечним керуванням пам'яттю за принципом RAII та повноцінним прямим ітератором `Iterator`.

## 1. Повна реалізація: C та C++

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define SKIPLIST_MAX_LEVEL 32
#define SKIPLIST_P_FACTOR 4  /* p = 1/4 */

typedef struct SkipNode {
    int key;
    int value;
    int level;
    struct SkipNode* forward[];  /* Гнучкий масив покажчиків */
} SkipNode;

typedef struct SkipList {
    int level;          /* Поточний максимальний активний рівень */
    size_t size;        /* Загальна кількість збережених пар */
    SkipNode* head;     /* Головний вартовий вузол */
} SkipList;

/* Створення нового вузла єдиним блоком виділення пам'яті */
static SkipNode* create_node(int level, int key, int value) {
    size_t total_size = sizeof(SkipNode) + sizeof(SkipNode*) * (size_t)level;
    SkipNode* node = (SkipNode*)malloc(total_size);
    if (!node) return NULL;
    node->key = key;
    node->value = value;
    node->level = level;
    for (int i = 0; i < level; i++) {
        node->forward[i] = NULL;
    }
    return node;
}

/* Ініціалізація нового пропускного списку */
SkipList* skiplist_create(void) {
    SkipList* list = (SkipList*)malloc(sizeof(SkipList));
    if (!list) return NULL;
    list->level = 1;
    list->size = 0;
    list->head = create_node(SKIPLIST_MAX_LEVEL, 0, 0);
    if (!list->head) {
        free(list);
        return NULL;
    }
    return list;
}

/* Швидкий генератор випадкових чисел XORShift для уникнення накладних витрат rand() */
static uint32_t xorshift32_state = 2463534242U;
static uint32_t fast_rand(void) {
    uint32_t x = xorshift32_state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    xorshift32_state = x;
    return x;
}

/* Генерація випадкового рівня з геометричним розподілом p = 1/4 */
static int random_level(void) {
    int lvl = 1;
    while ((fast_rand() & (SKIPLIST_P_FACTOR - 1)) == 0 && lvl < SKIPLIST_MAX_LEVEL) {
        lvl++;
    }
    return lvl;
}

/* Пошук значення за ключем */
bool skiplist_search(const SkipList* list, int key, int* out_value) {
    if (!list) return false;
    SkipNode* current = list->head;

    /* Спуск зверху вниз від найвищого активного рівня до нульового */
    for (int i = list->level - 1; i >= 0; i--) {
        while (current->forward[i] != NULL && current->forward[i]->key < key) {
            current = current->forward[i];
        }
    }

    current = current->forward[0];

    if (current != NULL && current->key == key) {
        if (out_value) *out_value = current->value;
        return true;
    }
    return false;
}

/* Вставка ключа і значення (перезапис значення, якщо ключ уже існує) */
bool skiplist_insert(SkipList* list, int key, int value) {
    if (!list) return false;
    SkipNode* update[SKIPLIST_MAX_LEVEL];
    SkipNode* current = list->head;

    /* 1. Пошук позиції та збереження попередників на кожному рівні */
    for (int i = list->level - 1; i >= 0; i--) {
        while (current->forward[i] != NULL && current->forward[i]->key < key) {
            current = current->forward[i];
        }
        update[i] = current;
    }

    current = current->forward[0];

    /* Якщо ключ уже існує — оновлюємо значення без зміни форми списку */
    if (current != NULL && current->key == key) {
        current->value = value;
        return true;
    }

    /* 2. Вибір випадкового рівня для нового елемента */
    int new_level = random_level();

    /* Якщо новий рівень перевищує поточний — оновлюємо верхівку масиву update */
    if (new_level > list->level) {
        for (int i = list->level; i < new_level; i++) {
            update[i] = list->head;
        }
        list->level = new_level;
    }

    /* 3. Створення вузла та локальне перечіплення покажчиків */
    SkipNode* new_node = create_node(new_level, key, value);
    if (!new_node) return false;

    for (int i = 0; i < new_level; i++) {
        new_node->forward[i] = update[i]->forward[i];
        update[i]->forward[i] = new_node;
    }

    list->size++;
    return true;
}

/* Видалення ключа зі списку */
bool skiplist_delete(SkipList* list, int key) {
    if (!list) return false;
    SkipNode* update[SKIPLIST_MAX_LEVEL];
    SkipNode* current = list->head;

    /* 1. Фіксація попередників */
    for (int i = list->level - 1; i >= 0; i--) {
        while (current->forward[i] != NULL && current->forward[i]->key < key) {
            current = current->forward[i];
        }
        update[i] = current;
    }

    current = current->forward[0];

    if (current == NULL || current->key != key) {
        return false;
    }

    /* 2. Перечіплення покажчиків в обхід видаленого вузла */
    for (int i = 0; i < list->level; i++) {
        if (update[i]->forward[i] != current) {
            break;
        }
        update[i]->forward[i] = current->forward[i];
    }

    free(current);

    /* 3. Коригування висоти списку при видаленні найвищого вузла */
    while (list->level > 1 && list->head->forward[list->level - 1] == NULL) {
        list->level--;
    }

    list->size--;
    return true;
}

/* Діапазонне сканування з функцією зворотного виклику */
void skiplist_range(const SkipList* list, int min_key, int max_key,
                    void (*callback)(int k, int v, void* ctx), void* ctx) {
    if (!list || !callback) return;
    SkipNode* current = list->head;

    for (int i = list->level - 1; i >= 0; i--) {
        while (current->forward[i] != NULL && current->forward[i]->key < min_key) {
            current = current->forward[i];
        }
    }

    current = current->forward[0];
    while (current != NULL && current->key <= max_key) {
        callback(current->key, current->value, ctx);
        current = current->forward[0];
    }
}

/* Повне звільнення всіх виділених ресурсів */
void skiplist_destroy(SkipList* list) {
    if (!list) return;
    SkipNode* current = list->head->forward[0];
    while (current != NULL) {
        SkipNode* next = current->forward[0];
        free(current);
        current = next;
    }
    free(list->head);
    free(list);
}
```
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <optional>
#include <random>
#include <functional>
#include <cstdint>
#include <utility>

template <typename Key, typename Value, typename Compare = std::less<Key>>
class SkipList {
public:
    static constexpr size_t kMaxLevel = 32;
    static constexpr double kBranchingProb = 0.25;

private:
    struct Node {
        Key key;
        Value value;
        std::vector<Node*> forward;

        Node(const Key& k, const Value& v, size_t level)
            : key(k), value(v), forward(level, nullptr) {}

        explicit Node(size_t level)
            : key{}, value{}, forward(level, nullptr) {}
    };

    size_t current_level_{1};
    size_t element_count_{0};
    std::unique_ptr<Node> head_;
    Compare comp_{};

    std::mt19937 rng_{std::random_device{}()};
    std::uniform_real_distribution<double> dist_{0.0, 1.0};

    size_t random_level() {
        size_t lvl = 1;
        while (dist_(rng_) < kBranchingProb && lvl < kMaxLevel) {
            lvl++;
        }
        return lvl;
    }

public:
    class Iterator {
    public:
        using iterator_category = std::forward_iterator_tag;
        using value_type = std::pair<const Key&, Value&>;
        using difference_type = std::ptrdiff_t;

        explicit Iterator(Node* node = nullptr) : current_(node) {}

        std::pair<const Key&, Value&> operator*() const {
            return {current_->key, current_->value};
        }

        Iterator& operator++() {
            if (current_) {
                current_ = current_->forward[0];
            }
            return *this;
        }

        Iterator operator++(int) {
            Iterator tmp = *this;
            ++(*this);
            return tmp;
        }

        bool operator==(const Iterator& other) const noexcept {
            return current_ == other.current_;
        }

        bool operator!=(const Iterator& other) const noexcept {
            return current_ != other.current_;
        }

    private:
        Node* current_;
        friend class SkipList;
    };

    SkipList() : head_(std::make_unique<Node>(kMaxLevel)) {}

    ~SkipList() {
        clear();
    }

    SkipList(const SkipList&) = delete;
    SkipList& operator=(const SkipList&) = delete;

    SkipList(SkipList&& other) noexcept
        : current_level_(other.current_level_),
          element_count_(other.element_count_),
          head_(std::move(other.head_)),
          comp_(std::move(other.comp_)),
          rng_(std::move(other.rng_)) {
        other.current_level_ = 1;
        other.element_count_ = 0;
        other.head_ = std::make_unique<Node>(kMaxLevel);
    }

    SkipList& operator=(SkipList&& other) noexcept {
        if (this != &other) {
            clear();
            current_level_ = other.current_level_;
            element_count_ = other.element_count_;
            head_ = std::move(other.head_);
            comp_ = std::move(other.comp_);
            rng_ = std::move(other.rng_);
            other.current_level_ = 1;
            other.element_count_ = 0;
            other.head_ = std::make_unique<Node>(kMaxLevel);
        }
        return *this;
    }

    [[nodiscard]] size_t size() const noexcept { return element_count_; }
    [[nodiscard]] bool empty() const noexcept { return element_count_ == 0; }

    Iterator begin() const noexcept { return Iterator(head_->forward[0]); }
    Iterator end() const noexcept { return Iterator(nullptr); }

    [[nodiscard]] std::optional<Value> find(const Key& key) const {
        const Node* curr = head_.get();

        for (int i = static_cast<int>(current_level_) - 1; i >= 0; --i) {
            while (curr->forward[i] != nullptr && comp_(curr->forward[i]->key, key)) {
                curr = curr->forward[i];
            }
        }

        curr = curr->forward[0];
        if (curr != nullptr && !comp_(key, curr->key) && !comp_(curr->key, key)) {
            return curr->value;
        }
        return std::nullopt;
    }

    bool insert(const Key& key, const Value& value) {
        std::vector<Node*> update(kMaxLevel, nullptr);
        Node* curr = head_.get();

        for (int i = static_cast<int>(current_level_) - 1; i >= 0; --i) {
            while (curr->forward[i] != nullptr && comp_(curr->forward[i]->key, key)) {
                curr = curr->forward[i];
            }
            update[i] = curr;
        }

        curr = curr->forward[0];

        if (curr != nullptr && !comp_(key, curr->key) && !comp_(curr->key, key)) {
            curr->value = value;
            return false;
        }

        size_t new_level = random_level();
        if (new_level > current_level_) {
            for (size_t i = current_level_; i < new_level; ++i) {
                update[i] = head_.get();
            }
            current_level_ = new_level;
        }

        auto* new_node = new Node(key, value, new_level);
        for (size_t i = 0; i < new_level; ++i) {
            new_node->forward[i] = update[i]->forward[i];
            update[i]->forward[i] = new_node;
        }

        element_count_++;
        return true;
    }

    bool erase(const Key& key) {
        std::vector<Node*> update(kMaxLevel, nullptr);
        Node* curr = head_.get();

        for (int i = static_cast<int>(current_level_) - 1; i >= 0; --i) {
            while (curr->forward[i] != nullptr && comp_(curr->forward[i]->key, key)) {
                curr = curr->forward[i];
            }
            update[i] = curr;
        }

        curr = curr->forward[0];

        if (curr == nullptr || comp_(key, curr->key) || comp_(curr->key, key)) {
            return false;
        }

        for (size_t i = 0; i < current_level_; ++i) {
            if (update[i]->forward[i] != curr) {
                break;
            }
            update[i]->forward[i] = curr->forward[i];
        }

        delete curr;

        while (current_level_ > 1 && head_->forward[current_level_ - 1] == nullptr) {
            current_level_--;
        }

        element_count_--;
        return true;
    }

    Iterator lower_bound(const Key& key) const {
        Node* curr = head_.get();
        for (int i = static_cast<int>(current_level_) - 1; i >= 0; --i) {
            while (curr->forward[i] != nullptr && comp_(curr->forward[i]->key, key)) {
                curr = curr->forward[i];
            }
        }
        return Iterator(curr->forward[0]);
    }

    void clear() noexcept {
        Node* curr = head_->forward[0];
        while (curr != nullptr) {
            Node* next = curr->forward[0];
            delete curr;
            curr = next;
        }
        for (size_t i = 0; i < kMaxLevel; ++i) {
            head_->forward[i] = nullptr;
        }
        current_level_ = 1;
        element_count_ = 0;
    }
};
```
:::

## 2. Анатомія пам'яті та кеш-локальність

У наївних реалізаціях зв'язаних структур кожен вузол часто розбивають на кілька незалежних виділень пам'яті: окремий об'єкт для корисного навантаження (ключ і значення) та окремий динамічний масив `forward` під покажчики переходів.

Такий підхід є неефективним у високопродуктивних системах із двох причин:
1. **Подвійне навантаження на системний алокатор:** створення кожного вузла вимагає двох викликів `malloc()`, що подвоює витрати часу процесора на пошук вільних блоків у купі та збільшує загальну фрагментацію пам'яті.
2. **Промахи повз лінії кешу процесора (англ. *cache misses*):** розіменування покажчика на масив веде в іншу ділянку віртуальної пам'яті. Замість зчитування компактного блоку даних процесор змушений завантажувати нову 64-байтну лінію кешу L1/L2/L3, що призводить до простою конвеєра інструкцій (англ. *pipeline stall*).

У наведеній вище реалізації на мові C застосовано підхід із гнучким масивом (англ. *flexible array member*), де корисні дані та покажчики переходів розміщуються в єдиному суцільному блоці пам'яті. У реалізації на C++ для спрощення керування життєвим циклом застосовано `std::vector<Node*>`, однак для високошвидкісних сховищ (наприклад, LevelDB/RocksDB) застосовують виділення пам'яті через спеціалізований арена-алокатор (англ. *Arena allocator*), де масив покажчиків і вузол розміщуються в єдиному масиві байтів.

Порівняємо структури опису вузлів в обох мовах:

:::tabs
```c
/* У C покажчики forward[] розташовані одразу за полями вузла */
typedef struct SkipNode {
    int key;
    int value;
    int level;
    struct SkipNode* forward[];  /* пам'ять виділяється разом із вузлом */
} SkipNode;
```
```cpp
// У C++ вузол інкапсулює вектор покажчиків та типи шаблону Key, Value
struct Node {
    Key key;
    Value value;
    std::vector<Node*> forward;

    Node(const Key& k, const Value& v, size_t level)
        : key(k), value(v), forward(level, nullptr) {}
};
```
:::

## 3. Генерація випадкового рівня без системних сповільнень

Швидкість генерації випадкового рівня безпосередньо впливає на час виконання операції `insert()`. Стандартна бібліотечна функція `rand()` у мові C містить внутрішні м'ютекси для потокобезпечності, що робить її вузьким місцем під час паралельної обробки.

Для усунення цих накладних витрат у коді на C використано генератор випадкових чисел XORShift, який виконує лише три побітові операції зміщення та виключного АБО (`^`, `<<`, `>>`). У коді на C++ застосовано високоефективний алгоритм `std::mt19937` у поєднанні з дійсним розподілом `std::uniform_real_distribution`.

Оскільки кожні 2 біти випадкового цілого числа набувають значення `00` рівно з імовірністю `1/4` (25%), побітова операція `fast_rand() & 3` виконується за один такт процесора, забезпечуючи високу швидкість створення нових вузлів.

Порівняння генераторів рівнів:

:::tabs
```c
/* C: побітова перевірка (rand & 3 == 0) дає ймовірність 1/4 за 1 такт */
static uint32_t xorshift32_state = 2463534242U;
static uint32_t fast_rand(void) {
    uint32_t x = xorshift32_state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    xorshift32_state = x;
    return x;
}

static int random_level(void) {
    int lvl = 1;
    while ((fast_rand() & 3) == 0 && lvl < SKIPLIST_MAX_LEVEL) {
        lvl++;
    }
    return lvl;
}
```
```cpp
// C++: генерація на базі вихору Мерсенна та рівномірного розподілу
size_t random_level() {
    size_t lvl = 1;
    while (dist_(rng_) < kBranchingProb && lvl < kMaxLevel) {
        lvl++;
    }
    return lvl;
}
```
:::

## 4. Покрокове простеження вставки та масив update[]

Ключовим механізмом операцій модифікації є локальний масив покажчиків попередників `update[]`.

Розглянемо покроковий стан покажчиків під час вставки нового вузла з ключем `25` та згенерованим рівнем `3` у список, що вже містить ключі `10` (рівень 2), `17` (рівень 4) та `35` (рівень 3).

### Крок 1. Пошук позиції та збір попередників

Пошук стартує з вузла `HEAD` на найвищому активному рівні 4:
- **На рівні 3:** перехід від `HEAD` до `17` (`17 < 25`). Наступний елемент після `17` — `NULL`, тому спуск униз. Записуємо `update[3] = 17`.
- **На рівні 2:** перехід від `17` до наступного елемента `35` неможливий, оскільки `35 > 25`. Спуск униз. Записуємо `update[2] = 17`.
- **На рівні 1:** наступний елемент `35 > 25`. Спуск униз. Записуємо `update[1] = 17`.
- **На рівні 0:** наступний елемент `35 > 25`. Спуск завершено. Записуємо `update[0] = 17`.

У результаті масив `update[0...3]` містить покажчики на вузол `17` для всіх рівнів від 0 до 3.

### Крок 2. Локальне перечіплення покажчиків

Новий вузол `25` має висоту 3. Для кожного рівня від 0 до 2 виконується локальне перепризначення:
1. `new_node->forward[i] = update[i]->forward[i]` — новий вузол бере собі наступника від вузла `17` (покажчик на вузол `35`).
2. `update[i]->forward[i] = new_node` — вузол `17` перенаправляє свій покажчик на новий вузол `25`.

Рівень 3 залишається без змін, оскільки новий вузол має висоту лише 3. Жоден інший вузол списку не зазнає модифікацій, що забезпечує виконання вставки за локальний час `O(1)` після завершення пошуку.

Порівняння циклу перечіплення покажчиків:

:::tabs
```c
/* C: пряме перепризначення в масивах покажчиків */
for (int i = 0; i < new_level; i++) {
    new_node->forward[i] = update[i]->forward[i];
    update[i]->forward[i] = new_node;
}
```
```cpp
// C++: оновлення векторів forward
for (size_t i = 0; i < new_level; ++i) {
    new_node->forward[i] = update[i]->forward[i];
    update[i]->forward[i] = new_node;
}
```
:::

## 5. Механізм видалення та очищення порожніх рівнів

Операція видалення є дзеркальним відображенням вставки, проте містить важливий крок оптимізації висоти структури:

1. **Локалізація цільового вузла:** за допомогою масиву `update[]` знаходять вузли-попередники на всіх рівнях.
2. **Перепризначення в обхід:** покажчик `update[i]->forward[i]` перенаправляється на `current->forward[i]`. Важливо, що як тільки на черговому рівні `update[i]->forward[i] != current`, цикл негайно зупиняється (`break`), оскільки цільовий вузол більше не присутній на вищих рівнях.
3. **Зниження поточної висоти списку:** якщо видалений елемент мав унікальну максимальну висоту, після його видалення покажчик `head->forward[list->level - 1]` стає рівним `NULL`. Спеціальний цикл зменшує `list->level`, запобігаючи зайвим холостим ітераціям при наступних пошуках.

Порівняння логіки видалення:

:::tabs
```c
/* C: видалення вузла та коригування висоти списку */
for (int i = 0; i < list->level; i++) {
    if (update[i]->forward[i] != current) break;
    update[i]->forward[i] = current->forward[i];
}
free(current);
while (list->level > 1 && list->head->forward[list->level - 1] == NULL) {
    list->level--;
}
```
```cpp
// C++: видалення та динамічне зниження current_level_
for (size_t i = 0; i < current_level_; ++i) {
    if (update[i]->forward[i] != curr) break;
    update[i]->forward[i] = curr->forward[i];
}
delete curr;
while (current_level_ > 1 && head_->forward[current_level_ - 1] == nullptr) {
    current_level_--;
}
```
:::

## 6. Діапазонні запити та пряме ітерування

Однією з головних переваг пропускного списку над хеш-таблицями є природна підтримка швидких діапазонних вибірок (англ. *range queries*). Оскільки всі вузли нульового рівня утворюють нерозривний відсортований однозв'язаний список, діапазонний запит виконується за два простих кроки:
1. Логарифмічний пошук першого вузла, ключ якого задовольняє умову `key >= min_key`.
2. Послідовний лінійний прохід по покажчиках `forward[0]` до досягнення вузла з ключем `key > max_key`.

У мові C діапазонна вибірка реалізується через функцію зворотного виклику (англ. *callback*), яка приймає вказівник на контекст користувача. У C++ реалізовано стандартний патерн `lower_bound()` та оператори ітератора `begin()` / `end()`:

:::tabs
```c
/* C: використання callback для діапазонного проходу */
void print_item(int k, int v, void* ctx) {
    printf("Key: %d, Value: %d\n", k, v);
}

/* Виклик у клієнтському коді: */
skiplist_range(list, 10, 50, print_item, NULL);
```
```cpp
// C++: використання lower_bound та стандартного циклу по ітератору
auto it = list.lower_bound(10);
while (it != list.end() && (*it).first <= 50) {
    std::cout << "Key: " << (*it).first << ", Value: " << (*it).second << "\n";
    ++it;
}
```
:::

## 7. Детальний аналіз крайових випадків

У промисловому коді надійність структури даних визначається її поведінкою на граничних станах:

1. **Вставка в порожній список:** головний вартовий вузол `head` ініціалізується з `forward[0...MaxLevel-1] = NULL`. Вставка першого вузла коректно зв'язує `head` із новим елементом, а поточний рівень списку `list->level` встановлюється рівним висоті першого вузла.
2. **Вставка найменшого ключа:** якщо новий ключ менший за всі наявні у списку, масив `update[]` на всіх рівнях містить покажчик на `head`. Новий вузол коректно стає першим елементом списку.
3. **Вставка найбільшого ключа:** якщо новий ключ більший за всі наявні, масив `update[]` містить покажчики на останні елементи відповідних рівнів, а покажчики `new_node->forward[]` ініціалізуються значеннями `NULL`.
4. **Обробка дублікатів ключів:** якщо переданий ключ уже присутній у списку, алгоритм виявляє точний збіг на нульовому рівні `current->key == key`, перезаписує значення `current->value = value` і повертає керування без створення нового вузла та без зміни структури зв'язків.
5. **Видалення єдиного вузла на рівні:** якщо видалений вузол був єдиним представником найвищого активного рівня (після видалення `head->forward[level - 1] == NULL`), алгоритм автоматично зменшує `list->level` у циклі `while`, що запобігає холостим циклам у майбутніх пошуках.
6. **Повне очищення пам'яті:** функція `skiplist_destroy` (або деструктор у C++) ітерується суворо по нульовому рівню `forward[0]`, гарантуючи звільнення кожного вузла рівно один раз без витоків пам'яті.

## 8. Арена-алокація у високопродуктивних базах даних

У високонавантажених сховищах даних на базі LSM-дерев (таких як RocksDB або LevelDB) створення об'єктів через стандартний `malloc` є неприпустимим через фрагментацію віртуальної пам'яті та блокування в системних алокаторах.

Для оптимізації використовують патерн **Арена-алокатора** (англ. *Arena allocator*): великі блоки пам'яті (наприклад, по 2–4 МБ) виділяються заздалегідь, а вузли пропускного списку нарізаються простим переміщенням покажчика зміщення `offset += node_size` без будь-яких системних викликів.

Головна перевага такого підходу: під час скидання `MemTable` на диск (операція `Flush`) уся пам'ять пропускного списку звільняється одномоментно знищенням самої Арени за час `O(1)`, повністю усуваючи необхідність повузлового виклику `free()`.

## 9. Автоматична валідація інваріантів структури

Для тестування коректності реалізації корисно реалізувати діагностичну функцію `validate()`, яка перевіряє дотримання ключових інваріантів пропускного списку:
1. **Інваріант строгого монотонного зростання:** на кожному рівні `i` ключі вузлів строго зростають (`node->key < node->forward[i]->key`).
2. **Інваріант підмножини рівнів:** будь-який вузол, присутній на рівні `i > 0`, обов'язково повинен бути присутнім на рівні `i - 1`.
3. **Відповідність кількості елементів:** підрахунок кількості вузлів на нульовому рівні повинен точно збігатися з полем `size`.

Реалізація перевірки інваріантів:

:::tabs
```c
/* C: повна перевірка інваріантів списку */
bool skiplist_validate(const SkipList* list) {
    if (!list || !list->head) return false;
    size_t count = 0;
    SkipNode* curr = list->head->forward[0];
    int prev_key = -2147483648; /* INT_MIN */

    /* Перевірка нульового рівня */
    while (curr != NULL) {
        if (count > 0 && curr->key <= prev_key) return false;
        prev_key = curr->key;
        count++;
        curr = curr->forward[0];
    }
    if (count != list->size) return false;

    /* Перевірка вищих рівнів */
    for (int i = 1; i < list->level; i++) {
        curr = list->head->forward[i];
        while (curr != NULL) {
            if (curr->level <= i) return false;
            if (curr->forward[i] != NULL && curr->forward[i]->key <= curr->key) return false;
            curr = curr->forward[i];
        }
    }
    return true;
}
```
```cpp
// C++: метод валідації інваріантів у класі SkipList
bool validate() const {
    if (!head_) return false;
    size_t count = 0;
    Node* curr = head_->forward[0];

    while (curr != nullptr) {
        if (curr->forward[0] != nullptr && !comp_(curr->key, curr->forward[0]->key)) {
            return false;
        }
        count++;
        curr = curr->forward[0];
    }
    if (count != element_count_) return false;

    for (size_t i = 1; i < current_level_; ++i) {
        curr = head_->forward[i];
        while (curr != nullptr) {
            if (curr->forward[i] != nullptr && !comp_(curr->key, curr->forward[i]->key)) {
                return false;
            }
            curr = curr->forward[i];
        }
    }
    return true;
}
```
:::

## 10. Основи неблокувальної багатопотокової обробки (Lock-Free)

Головна перевага пропускного списку перед деревами полягає у відсутності глобальних поворотів, що робить його ідеальним кандидатом для паралельних неблокувальних реалізацій (англ. *lock-free concurrent skip list*).

Для організації паралельного доступу без взаємних блокувань (англ. *mutexes*) використовують атомарні інструкції `Compare-And-Swap` (CAS). Вставка нового вузла виконується знизу вгору: спершу новий вузол атомарно приєднується на нульовому рівні, після чого по черзі зв'язується на вищих рівнях. Читачі завжди бачать валідний зв'язаний список і не потребують жодних блокувань.

Для операції видалення застосовують техніку **двоетапного логічного та фізичного маркування** (англ. *logical and physical deletion*, алгоритм Гарріса–Фомічова):
1. **Логічне маркування:** наймолодший біт покажчика `forward[i]` встановлюється в 1 за допомогою CAS. Це сигналізує всім потокам, що вузол позначено на видалення і нові вставки після нього заборонені.
2. **Фізичне перечіплення:** покажчик попередника перемикається в обхід позначеного вузла наступним CAS.

Така схема дозволяє тисячам паралельних потоків одночасно читати, додавати та видаляти дані з пропускного списку без деградації продуктивності, що неможливо повторити у традиційних червоно-чорних чи AVL-деревах.

## 11. Інтеграція в архітектуру сучасних сховищ (LSM-Tree MemTable)

У дискових сховищах типу LevelDB та RocksDB впорядкований пропускний список виконує роль головного буфера оперативної пам'яті — `MemTable`.

Життєвий цикл запису в такій системі виглядає наступним чином:
1. **Журналювання:** клієнтський запит на запис `Put(Key, Value)` спершу послідовно записується в журнал випереджального запису (англ. *Write-Ahead Log*, WAL) на диску для забезпечення відмовостійкості.
2. **Вставка в оперативну пам'ять:** запис вставляється в поточний активний `MemTable` (на базі `ConcurrentSkipList`) за час `O(log n)`. Оскільки Skip List постійно підтримує дані у відсортованому стані, запис не потребує сортування перед збереженням на накопичувач.
3. **Заморожування:** коли розмір `MemTable` досягає порогового значення (наприклад, 64 МБ), він переводиться в режим тільки для читання (стає `Immutable MemTable`), а для нових записів створюється новий порожній пропускний список.
4. **Скидання на диск (Flush):** фоновий потік просто послідовно ітерується по нульовому рівню `Immutable MemTable` від початку до кінця за час `O(n)` і записує вже відсортований блок даних на диск у форматі таблиці статичних рядків (SSTable, англ. *Sorted String Table*).

Ця архітектура повністю усуває випадковий доступ до диска при записі, перетворюючи всі операції на послідовний потоковий вивід завдяки постійній внутрішній впорядкованості пропускного списку.

## 12. Практичні вимірювання продуктивності та профілювання

При порівнянні продуктивності пропускного списку з іншими стандартними структурами даних спостерігаються такі закономірності:

- **Точковий пошук проти хеш-таблиці (`std::unordered_map`):** хеш-таблиця демонструє константний час `O(1)` і випереджає Skip List приблизно в 2–3 рази на поодиноких читаннях. Проте хеш-таблиця принципово не здатна виконувати впорядковані діапазонні запити та вимагає періодичної дорогої перехешування (англ. *rehashing*).
- **Вставка та діапазони проти червоно-чорного дерева (`std::map`):** однопотоковий Skip List демонструє майже ідентичний час пошуку та вставки з червоно-чорним деревом (різниця становить менше 5–8%), але під час діапазонного сканування послідовний прохід по `forward[0]` у пропускному списку виявляється на 30–40% швидшим завдяки прямолінійній локальності покажчиків і відсутності рекурсії.
- **Багатопотокова масштабованість:** при переході до 8 і більше паралельних потоків-письменників пропускний список із неблокувальним CAS випереджає дерево з блокуваннями піддерев у 4–10 разів за пропускною здатністю, уникаючи взаємного очікування потоків. Навантажувальні тести показують стабільну затримку p99 на рівні часток мілісекунди навіть при мільйонах операцій за секунду.

## 13. Типові інженерні пастки та рекомендації щодо надійності

Під час розробки та промислової експлуатації пропускних списків розробники часто стикаються з трьома критичними підводними каменями:

### 1. Вирівнювання пам'яті та фальшивий поділ ліній кешу (False Sharing)

У багатопотоковому середовищі, коли кілька потоків одночасно модифікують суміжні вузли списку, критично важливо уникати ситуації, коли вузли потрапляють в одну 64-байтну лінію процесорного кешу L1/L2. Якщо два ядра модифікують змінні в межах однієї лінії кешу, протокол когерентності кешу (MESI) змушений постійно інвалідувати кеш-лінії між ядрами, викликаючи значне сповільнення шини пам'яті. Використання вирівнювання пам'яті `alignas(64)` або алокація вузлів через незалежні арени повністю усуває цю проблему.

### 2. Спільний генератор випадкових чисел як пляшкове горло

Якщо всі потоки звертаються до єдиного екземпляра генератора випадкових чисел або використовують стандартний `rand()`, внутрішнє блокування генератора повністю нівелює переваги паралельного пропускного списку. Кожен робочий потік повинен володіти власним локальним екземпляром генератора (через специфікатор `thread_local` у C++ або передачу стану генератора у функцію потоку в C).

### 3. Проблема ABA та безпечне звільнення пам'яті

У неблокувальних реалізаціях на базі CAS існує ризик проблеми ABA: вузол видаляється з пам'яті одним потоком, пам'ять перевиділяється під новий вузол із тією самою адресою, і інший потік помилково вважає, що покажчик не змінювався. Для вирішення цієї проблеми у виробничих системах застосовують безпечні схеми відкладеного звільнення пам'яті: покажчики небезпеки (англ. *Hazard Pointers*) або епохальне звільнення пам'яті (англ. *Epoch-Based Reclamation*, RCU), коли пам'ять фізично звільняється лише тоді, коли всі активні потоки завершили читання.

У сховищах на кшталт Redis для невеликих наборів даних застосовують гібридну оптимізацію: поки кількість елементів у впорядкованій множині менша за 128, використовується суцільний компактний масив `ziplist` для максимальної економії байтів. Як тільки розмір перевищує поріг, колекція прозоро трансформується у повноцінний Skip List для збереження швидкодії `O(log n)`.
