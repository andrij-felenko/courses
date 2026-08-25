# 📋 Довідник програмного інтерфейсу (API) інтервального дерева

У цій вставці наведено вичерпний довідник програмного інтерфейсу (API) доповненого інтервального дерева (Augmented Interval Search Tree). Опис охоплює типізацію даних, функціональні сигнатури, параметризовані контракти, правила управління ресурсами, гарантії складності та специфікацію обробки крайових умов мовами C та C++.

---

## 1. Контракт даних та базові типи

Програмний інтерфейс оперує одновимірними замкненими інтервалами у двовимірній системі типів.

### 1.1. Тип даних `Interval` (C та C++)

Структура `Interval` репрезентує геометрію замкненого 1D-проміжку `[low, high]`.

:::tabs
```c
typedef struct Interval {
    double low;   /* Ліва (нижня) межа інтервалу */
    double high;  /* Права (верхня) межа інтервалу */
} Interval;
```
```cpp
namespace geo {
    struct Interval {
        double low;
        double high;

        [[nodiscard]] constexpr bool overlaps(const Interval& other) const noexcept;
        [[nodiscard]] constexpr bool contains(double point) const noexcept;
        [[nodiscard]] constexpr bool encloses(const Interval& other) const noexcept;
    };
}
```
:::

### 1.2. Детальна специфікація полів структури `Interval`

- `low` (тип `double`): ліва координата початку інтервалу. Мусить відповідати суворому математичному інваріанту `low ≤ high`. Використання значень `NaN` або `±Infinity` є некоректним та призводить до невизначеної поведінки (Undefined Behavior).
- `high` (тип `double`): права координата закінчення інтервалу. Завжди перевищує або дорівнює `low`. Випадок `low == high` описує вироджений точковий інтервал.

---

### 1.3. Вузол дерева `IntervalNode`

Вузол розширеного дерева містить вихідний інтервальний об'єкт, розрахований атрибут аугментації `max_high`, а також зв'язки з дочірніми елементами.

:::tabs
```c
typedef struct IntervalNode {
    Interval interval;           /* Корисні дані інтервалу */
    double max_high;             /* Супремум правих меж у піддереві */
    struct IntervalNode* left;   /* Ліве піддерево (low < node.low) */
    struct IntervalNode* right;  /* Праве піддерево (low >= node.low) */
} IntervalNode;
```
```cpp
namespace geo {
    class IntervalNode {
    public:
        Interval interval;
        double max_high;
        std::unique_ptr<IntervalNode> left;
        std::unique_ptr<IntervalNode> right;

        explicit IntervalNode(Interval it) noexcept;
        void update_max() noexcept;
    };
}
```
:::

---

## 2. Повна специфікація операцій API

Нижче наведено вичерпний опис функціонального інтерфейсу з відповідними сигнатурами C та C++.

### 2.1. Створення інтервалу та ініціалізація

:::tabs
```c
Interval create_interval(double low, double high);
```
```cpp
constexpr geo::Interval::Interval(double l, double h) noexcept : low(l), high(h) {}
```
:::

- **Призначення:** Конструює та повертає новий екземпляр структури `Interval` із вказаними межами.
- **Вхідні параметри:**
  - `low`: дійсна координата початку інтервалу.
  - `high`: дійсна координата закінчення інтервалу.
- **Преконтракт (Precondition):** Вимагається виконання фундаментального геометричного інваріанта `low ≤ high`. Допускається рівність `low == high` для конструювання точкового (виродженого) інтервалу. Використання неелементарних дійсних значень (`NaN` або нескінченностей `±Infinity`) заборонено.
- **Постконтракт (Postcondition):** Створений об'єкт гарантує `it.low == low` та `it.high == high`.
- **Помилки та винятки:** Не генерує помилок виділення пам'яті. У C-інтерфейсі при виявленні некоректних аргументів `low > high` функція виводить попередження у `stderr` і автоматично міняє значення місцями `std::swap(low, high)`.
- **Гарантія складності:** `O(1)` за часом виконання та `O(1)` додаткової пам'яті.

### 2.2. Предикат перетину

:::tabs
```c
bool intervals_overlap(Interval a, Interval b);
```
```cpp
constexpr bool geo::Interval::overlaps(const Interval& other) const noexcept;
```
:::

- **Призначення:** Обчислює логічне відношення геометричного перетину `Overlap(a, b)` між двома інтервальними об'єктами.
- **Вхідні параметри:** два об'єкти типу `Interval` (`a` та `b`).
- **Повертане значення:** Повертає `true`, якщо інтервали мають принаймні одну спільну точку на числовій прямій, тобто виконується подвійна нерівність `(a.low <= b.high) && (a.high >= b.low)`. В іншому випадку повертає `false`.
- **Властивості та потокобезпечність:** Повністю чиста функція без побічних ефектів (`pure function`). Може безпечно викликатися одночасно із довільної кількості паралельних потоків обчислення без використання синхронізуючих примітивів (Lock-Free Thread Safe).
- **Гарантія складності:** `O(1)` за часом.

### 2.3. Вставка інтервалу у дерево

:::tabs
```c
IntervalNode* interval_insert(IntervalNode* root, Interval it);
```
```cpp
void geo::IntervalTree::insert(Interval it);
```
:::

- **Призначення:** Додає новий інтервальний об'єкт `it` у доповнене бінарне дерево пошуку.
- **Вхідні параметри:**
  - `root` (у мові C) / `this` (у мові C++): корінь дерева або екземпляр класу `IntervalTree`. Допускається порожнє дерево (`root == NULL`).
  - `it`: доданий інтервальний об'єкт.
- **Повертане значення:** У мові C повертає вказівник `IntervalNode*` на новий корінь піддерева (оскільки корінь міг змінитися при повороті). У мові C++ метод повертає `void` і модифікує внутрішній стан дерева.
- **Побічні ефекти та володіння ресурсами:** Виділяє динамічну пам'ять для нового вузла (`malloc` у C, `std::make_unique` у C++). Проводить підйом по рекурсивному стеку від місця вставки до кореня, автоматично перераховуючи значення атрибута `max_high` у кожному відвіданому вузлі. При необхідності викликає процедури ребалансування (повороти червоно-чорного дерева).
- **Гарантії винятків у C++:** Забезпечує **сувору гарантію винятків (Strong Exception Guarantee)**. Якщо під час виділення пам'яті викидається `std::bad_alloc`, дерево залишається у 100% вихідному цілісному стані.
- **Гарантія складності:** `O(log n)` за часом виконання у балансованому дереві, `O(log n)` додаткової пам'яті стеку рекурсії.

### 2.4. Одиничний пошук перетину (`Interval_Search`)

:::tabs
```c
IntervalNode* interval_search(IntervalNode* root, Interval query);
```
```cpp
std::optional<geo::Interval> geo::IntervalTree::find_any_overlap(const Interval& query) const noexcept;
```
:::

- **Призначення:** Здійснює пошук першого-ліпшого інтервалу у дереві, який перетинається із запитом `query`.
- **Вхідні параметри:** інтервал запиту `query`.
- **Повертане значення:** У мові C повертає вказівник на знайдений вузол `IntervalNode*` у разі успіху або `NULL`, якщо у дереві відсутні перетини. У мові C++ повертає безпечну обгортку `std::optional<Interval>`, яка містить знайдений інтервал або `std::nullopt`.
- **Алгоритмічні гарантії:** Фундаментальна теорема про коректність інтервального дерева гарантує, що якщо у дереві існує хоча б один інтервал, що перетинає `query`, дана процедура обов'язково його знайде за один ітеративний спуск від кореня до листка.
- **Гарантія складності:** `O(log n)` за часом виконання, `O(1)` додаткової пам'яті (ітеративний спуск без використання стеку).

### 2.5. Вибірка всіх перетинів (`Report-All-Overlaps`)

:::tabs
```c
void interval_search_all_recursive(IntervalNode* root, Interval query, NodeList* results);
```
```cpp
std::vector<geo::Interval> geo::IntervalTree::find_all_overlaps(const Interval& query) const;
```
:::

- **Призначення:** Знаходить та вибирає **усі** `k` інтервалів дерева, які мають спільні точки із запитом `query`.
- **Вхідні параметри:** інтервал запиту `query` та вихідний контейнер результатів (`NodeList*` у C, повертаний `std::vector` у C++).
- **Алгоритм та відсікання гілок:** Застосовує рекурсивний обхід піддерев з автоматичним відсіканням гілок. Праве піддерево відсікається, якщо `l[x] > r[q]`. Ліве піддерево відсікається, якщо `max[left[x]] < l[q]`.
- **Гарантія складності:** `O(k · log n)` за часом виконання, де `k` — кількість знайдених збігів.

### 2.6. Очищення пам'яті дерева

:::tabs
```c
void free_interval_tree(IntervalNode* root);
```
```cpp
void geo::IntervalTree::clear() noexcept;
```
:::

- **Призначення:** Повністю вивільняє динамічну пам'ять усіх збережених вузлів дерева.
- **Опис процедури:** У мові C виконує рекурсивний посторонній обхід (Post-order Traversal) із послідовним викликом `free()`. У мові C++ звільнення відбувається автоматично завдяки каскадній деструкції `std::unique_ptr`.
- **Гарантія складності:** `O(n)` за часом, `O(h)` за додатковою пам'яттю стеку.


---

## 3. Таблиця гарантій часової та просторової складності

Нижче зведено гарантії обчислювальної та просторової складності для всіх операцій доповненого інтервального дерева.

| Операція API | Сигнатура C | Метод C++ | Складність Best | Складність Worst | Складність Пам'ять |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Створення дерева** | `IntervalNode* r = NULL` | `IntervalTree tree;` | `O(1)` | `O(1)` | `O(1)` |
| **Вставка елемента** | `interval_insert` | `tree.insert(it)` | `O(1)` | `O(log n)` | `O(log n)` стек |
| **Одиничний пошук** | `interval_search` | `find_any_overlap` | `O(1)` | `O(log n)` | `O(1)` |
| **Пошук усіх `k` збігів**| `interval_search_all` | `find_all_overlaps` | `O(1)` (k=0) | `O(k log n)` | `O(k)` пам'ять |
| **Очищення ресурсу** | `free_interval_tree` | `tree.clear()` | `O(1)` | `O(n)` | `O(h)` стек |

### Аналіз теоретичних гарантій складності

1. **Операція створення дерева:** Ініціалізація нового об'єкта `IntervalTree` полягає у встановленні корінного вказівника у значення `nullptr`. Вона не виконує алокацій пам'яті та завершується за константний час `O(1)`.
2. **Операція вставки:** Виконує спуск від кореня до листка завдовжки `h = O(log n)`, виділення пам'яті для одного вузла та підйом вгору із перерахунком `max_high`. Робота з пам'яттю обмежена фіксованим зауваженням.
3. **Операція одиничного пошуку:** Алгоритм виконує ітеративний спуск по єдиній логарифмічній гілці дерева без відгалужень. Усі порівняння є скалярними операціями над дійсними числами `double`. Додаткова пам'ять у купі не використовується.
4. **Операція вибірки всіх збігів:** Кожен відвіданий рекурсивний вузол або приносить один новий інтервал-відповідь у вектор результатів, або лежить на тупиковій гілці довжиною не більше `O(log n)`. Це гарантує сувору верхню межу `O(k log n)`.

---

## 4. Специфікація обробки крайових випадків (Boundary & Edge Conditions)

Правильна обробка граничних та нетипових умов є ключовою вимогою до промислової безпеки програмної бібліотеки.

### 4.1. Порожнє дерево (`root == NULL` / `tree.empty() == true`)
- Запит `interval_search(NULL, query)` повертає `NULL`.
- Запит `tree.find_any_overlap(query)` повертає `std::nullopt`.
- Запит `tree.find_all_overlaps(query)` повертає порожній `std::vector<Interval>` розміру 0.
- Усі виклики є повністю безпечними і не призводять до `NullPointerException`, `Segmentation Fault` чи збоїв адресації пам'яті.

### 4.2. Відсутність перетинів у базі даних
- Пошуковий алгоритм проходить по найдовшій логарифмічній гілці від кореня до `NIL`-листка.
- Визначається відсутність елементів у базі даних і безпечно повертається результат відсутності збігів без модифікації пам'яті.

### 4.3. Збіг меж (Точкові та дотичні інтервали)
- Для двох інтервалів `A = [10, 20]` та `B = [20, 30]` предикат замкнених інтервалів дає `(10 <= 30) && (20 >= 20)` → `true`. Тобто дотичні інтервали вважаються перетинаючимися у точці `20`.
- Якщо в прикладній задачі вимагаються напіввідкриті інтервали `[low, high)`, розробник має змінити реалізацію `overlaps` на суворі нерівності: `(a.low < b.high) && (a.high > b.low)`.

### 4.4. Дублікати лівих меж `l[i] == l[j]`
- Якщо у дерево додається інтервал `it`, чия ліва межа дорівнює вже наявному вузлу (`it.low == node.interval.low`), новий вузол розміщується у правому піддереві за умовою `it.low >= node.interval.low`.
- Інваріант `max_high` та порядок BST підтримуються без порушень.

---

## 5. Правила володіння пам'яттю та багатопотоковості

### 5.1. Володіння пам'яттю (Memory Ownership)

1. **Контракт мови C:**
   - Функція `interval_insert()` виділяє пам'ять через `malloc()`. Відповідальність за звільнення всієї структури лежить на викликаючій стороні через обов'язковий виклик `free_interval_tree()`.
   - Повернені вказівники з `interval_search()` є спостерігачами (`non-owning pointers`). Викликаюча сторона не повинна викликати `free()` для окремих повернутих вузлів.

2. **Контракт мови C++:**
   - Клас `IntervalTree` повністю володіє всіма вузлами через контейнери `std::unique_ptr`.
   - Методи `find_any_overlap` та `find_all_overlaps` повертають копії значень `Interval`, що виключає ризик появи висячих вказівників (Dangling Pointers) при зміні дерева.

### 5.2. Потокобезпечність (Thread Safety)

- **Конкурентне читання:** Метод `find_any_overlap` та функція `interval_search` позначені як константні (`const`) і можуть викликатися одночасно із багатьох паралельних потоків без використання блокувань (Lock-Free Read).
- **Модифікація:** Одночасні операції вставки `insert()` та читання вимагають зовнішнього синхронізатора (наприклад, `std::shared_mutex` з розмежуванням `shared_lock` для читання та `unique_lock` для запису).

---

## 6. Специфікація ітераторів та обходу (Iterator API)

Для послідовного сканування всіх елементів інтервального дерева у порядку зростання лівих меж `low` надається двонаправлений ітератор.

:::tabs
```c
typedef struct IntervalTreeIterator {
    IntervalNode* stack[64];
    int top;
    IntervalNode* current;
} IntervalTreeIterator;

IntervalTreeIterator iterator_begin(IntervalNode* root);
bool iterator_has_next(const IntervalTreeIterator* it);
IntervalNode* iterator_next(IntervalTreeIterator* it);
```
```cpp
namespace geo {
    class IntervalTreeIterator {
    public:
        using iterator_category = std::forward_iterator_tag;
        using value_type        = Interval;
        using difference_type   = std::ptrdiff_t;
        using pointer           = const Interval*;
        using reference         = const Interval&;

        IntervalTreeIterator() noexcept = default;
        explicit IntervalTreeIterator(const IntervalNode* root) noexcept;

        reference operator*() const noexcept;
        pointer operator->() const noexcept;
        IntervalTreeIterator& operator++() noexcept;
        bool operator==(const IntervalTreeIterator& other) const noexcept;
    };
}
```
:::

### Детальні гарантії ітераторів

- **Призначення:** Забезпечує ітеративний центрований обхід (In-order Traversal) без викликів рекурсії.
- **Гарантії пам'яті:** Використовує внутрішній статичний стек розміру 64 (достатньо для обходу дерев висотою до 64 рівнів, що охоплює `2⁶⁴` елементів). Не виконує динамічних алокацій у купі.
- **Інвалідація ітераторів:** Будь-яка вставка `insert()` або вилучення вузла може змінити топологію дерева і робить існуючі ітератори недійсними (Iterator Invalidation).

---

## 7. Специфікація сумісності бінарного інтерфейсу (C ABI Stability)

Для використання реалізації у вигляді динамічної бібліотеки (`.so` у Linux або `.dll` у Windows) заголовочний файл надає суворі гарантії C ABI:

1. **Компіляція `extern "C"`:** Усі сигнатури мови C обгорнуті макросом `extern "C"` для запобігання декоруванню імен (Name Mangling) компілятором C++.
2. **Вирівнювання структур (Structure Alignment):** Поля структури `Interval` розташовані у порядку спадання розміру (`double low`, `double high`), що усуває міжблокові заповнювачі (padding) і забезпечує точний розмір 16 байт на всіх 64-бітних платформах.
3. **Стабільність розміру вузла:** Структура `IntervalNode` має строго визначений розмір 40 байт у x86-64 ABI.

---

## 8. Функції зворотного виклику та балансування (Rebalance Callbacks)

При інтеграції інтервального дерева у балансовані основи (наприклад, червоно-чорне дерево) процедури поворотів повинні викликати функції коригування `max_high`.

:::tabs
```c
typedef void (*node_update_fn)(IntervalNode* node);

void on_left_rotate(IntervalNode* old_parent, IntervalNode* new_parent) {
    update_node_max(old_parent);
    update_node_max(new_parent);
}
```
```cpp
template <typename Node>
void on_left_rotate(Node* old_parent, Node* new_parent) noexcept {
    old_parent->update_max();
    new_parent->update_max();
}
```
:::

- **Порядок виконання:** При повороті `Left-Rotate(old_parent)` спочатку обов'язково оновлюється колишній батьківський вузол `old_parent` (який опустився нижче), і лише після цього — новий корінь `new_parent` (який піднявся вище).

---

## 9. Специфікація кодів помилок та обробки виняткових ситуацій

### 9.1. Таблиця системних кодів помилок (C API)

У низькорівневому C-інтерфейсі розширені функції повертають цілочисельний код статусу `int`:

| Код помилки | Константа | Опис умови | Стратегія обробки |
| :--- | :--- | :--- | :--- |
| `0` | `INTERVAL_TREE_SUCCESS` | Операцію виконано успішно без зауважень | Повернення запитаних даних |
| `-1` | `INTERVAL_TREE_ERR_INVAL` | Некоректні вхідні параметри (`low > high` або `NaN`) | Відхилення операції, встановлення `errno = EINVAL` |
| `-2` | `INTERVAL_TREE_ERR_NOMEM` | Неможливість виділення пам'яті в купі (`malloc` повертає `NULL`) | Встановлення `errno = ENOMEM`, зберігання стану дерева |
| `-3` | `INTERVAL_TREE_ERR_NOTFOUND` | У дереві не знайдено жодного перетину з запитом | Повернення `NULL` або `0` знайдених елементів |

---

## 10. Контракт кастомних алокаторів пам'яті (Custom Allocator Hooks)

:::tabs
```c
typedef void* (*custom_alloc_fn)(size_t size);
typedef void  (*custom_free_fn)(void* ptr);

typedef struct IntervalAllocator {
    custom_alloc_fn alloc_func;
    custom_free_fn  free_func;
} IntervalAllocator;

void interval_tree_set_allocator(IntervalAllocator alloc);
```
```cpp
template <typename T, typename Allocator = std::allocator<T>>
class CustomIntervalTree {
    Allocator alloc_;
public:
    explicit CustomIntervalTree(const Allocator& alloc = Allocator());
};
```
:::

- **Вимоги до алокаторів:** Кастомний алокатор пам'яті повинен забезпечувати 8-байтове вирівнювання повернутих вказівників.

---

## 11. Специфікація атомарного доступності та синхронізації

:::tabs
```c
typedef struct AtomicIntervalNode {
    Interval interval;
    _Atomic double max_high;
    struct AtomicIntervalNode* _Atomic left;
    struct AtomicIntervalNode* _Atomic right;
} AtomicIntervalNode;
```
```cpp
namespace geo {
    struct AtomicIntervalNode {
        Interval interval;
        std::atomic<double> max_high;
        std::atomic<AtomicIntervalNode*> left;
        std::atomic<AtomicIntervalNode*> right;
    };
}
```
:::

- **Гарантії потокобезпечності:** Застосування `std::atomic<double>` для `max_high` дозволяє паралельним потокам-читачам обходити дерево без блокувань mtx, бачачи завжди узгоджені значення.

---

## 12. Специфікація API центрованого інтервального дерева (Centered Interval Tree API)

:::tabs
```c
typedef struct CenteredIntervalNode {
    double x_mid;                    /* Медіанна лінія розбиття простору */
    Interval* intervals_by_low;      /* Масив A_L, відсортований за low (зростання) */
    Interval* intervals_by_high;     /* Масив A_R, відсортований за high (спадання) */
    size_t count;                    /* Кількість інтервалів у даному вузлі */
    struct CenteredIntervalNode* left;  /* Інтервали строго ліворуч (high < x_mid) */
    struct CenteredIntervalNode* right; /* Інтервали строго праворуч (low > x_mid) */
} CenteredIntervalNode;
```
```cpp
namespace geo {
    class CenteredIntervalTree {
        double x_mid_;
        std::vector<Interval> intervals_by_low_;
        std::vector<Interval> intervals_by_high_;
        std::unique_ptr<CenteredIntervalTree> left_;
        std::unique_ptr<CenteredIntervalTree> right_;
    public:
        explicit CenteredIntervalTree(std::span<const Interval> intervals);
        [[nodiscard]] std::vector<Interval> query_point(double p) const;
    };
}
```
:::

- **Особливості використання:** Центроване дерево конструюється статично для множини з `n` інтервалів і забезпечує пошук точкових перетинів за оптимальний час `O(k + log n)`.

---

## 13. Приклад використання API (C та C++ tabs)

:::tabs
```c
#include <stdio.h>
#include "interval_tree.h"

int main(void) {
    IntervalNode* tree = NULL;
    tree = interval_insert(tree, create_interval(15.0, 20.0));
    tree = interval_insert(tree, create_interval(10.0, 30.0));
    
    Interval query = {21.0, 25.0};
    IntervalNode* result = interval_search(tree, query);
    if (result != NULL) {
        printf("Знайдено перетин: [%g, %g]\n", result->interval.low, result->interval.high);
    }
    
    free_interval_tree(tree);
    return 0;
}
```
```cpp
#include <iostream>
#include "IntervalTree.hpp"

int main() {
    geo::IntervalTree tree;
    tree.insert({15.0, 20.0});
    tree.insert({10.0, 30.0});

    if (auto match = tree.find_any_overlap({21.0, 25.0}); match) {
        std::cout << "Знайдено перетин: [" << match->low << ", " << match->high << "]\n";
    }
    return 0;
}
```
:::

---

## 15. Концепти C++20 та специфікація PMR (Polymorphic Memory Resources)

У сучасній C++20 розробці клас `IntervalTree` надається як шаблонізована структура `BasicIntervalTree<T, Alloc>`, де тип координат `T` обмежений концептом `std::floating_point` або `std::integral`.

### 15.1. Концепти координат `IntervalCoordinate`

```cpp
template <typename T>
concept IntervalCoordinate = std::is_arithmetic_v<T> && requires(T a, T b) {
    { a < b }  -> std::convertible_to<bool>;
    { a <= b } -> std::convertible_to<bool>;
    { a == b } -> std::convertible_to<bool>;
};
```

- **Призначення:** Гарантує на натапі компіляції (Compile-Time Validation), що тип точок має впорядкування і не викликає невизначеної поведінки при порівняннях.

### 15.2. Використання поліморфної пам'яті `std::pmr`

Для критичних систем real-time розробки бібліотека підтримує заголовок `<memory_resource>`:

```cpp
namespace geo::pmr {
    using IntervalTree = BasicIntervalTree<double, std::pmr::polymorphic_allocator<IntervalNode>>;
}
```

- **Переваги:** Дозволяє виділяти вузли інтервального дерева всередині арени `std::pmr::monotonic_buffer_resource` без викликів системного менеджерку пам'яті. Вилучення всього дерева при використанні арени виконується за `O(1)` шляхом одноразового скидання арени (Arena Reset).

### 15.3. Специфікація серіалізації та збереження стану (Persistence API)

Для збереження структури інтервального дерева на диск або передачі по мережі між вузлами розподіленої системи бібліотека надає бінарний API серіалізації:

- **Формат збереження:** Дерево серіалізується шляхом прямого обходу (Pre-order Traversal), що гарантує відновлення ідентичного балансованого дерева без потреби виконання додаткових операцій повороту під час завантаження.
- **Гарантія відновлення:** Десеріалізатор повністю відновлює інваріант `max_high` для кожного вузла за знизу-вгору алгоритмом за один лінійний прохід `O(n)` із перевіркою цілісності хеш-суми даних. Це запобігає завантаженню пошкодженого або фальсифікованого індексу з зовнішнього сховища даних.



---

## 16. Підсумковий висновок

Описаний програмний інтерфейс (API) забезпечує суворий інженерний контракт, поєднуючи високу низькорівневу продуктивність мови C із математичною безпекою типів та автоматичним керуванням ресурсами мови C++. Дотримання наведених специфікацій гарантує повну сумісність при розробці складних підсистем обробки геопросторових та часових даних.




