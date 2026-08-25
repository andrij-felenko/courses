# ⚙️ Індексована двійкова купа: повна реалізація для задач маршрутизації

Класична двійкова купа оптимізована для швидкого вилучення глобального екстремуму (`pop` за час `O(log N)`), однак вона не підтримує швидкого довільного доступу до елементів за їхніми зовнішніми ідентифікаторами. Щоб знайти вузол із заданим числовим дескриптором у звичайному масиві двійкової купи, доводиться виконувати повне лінійне сканування за час `O(N)`. Через це операція зміни пріоритету (`decrease-key`), яка лежить в основі класичних графів алгоритмів Дейкстри та Прима, у наївній купі стає неприпустимо повільною і руйнує теоретичну швидкодію системи.

**Індексована двійкова купа** (Indexed Binary Heap) долає це обмеження завдяки симетричній системі подвійної адресації, знижуючи час операцій `decrease-key`, `increase-key`, `contains` та довільного вилучення `delete_element` до `O(log N)` або `O(1)`.

## Архітектура двох масивів та інваріант узгодженості

Індексована купа зберігає два узгоджених масиви фіксованого або динамічного розміру:
1. `heap[]`: фізичний масив купи, елементами якого є пари `{id, key}` (де `id` — унікальний цілочисельний дескриптор об'єкта в діапазоні від `0` до `capacity - 1`, а `key` — його пріоритет або числова вага).
2. `pos[]`: масив зворотного відображення розміру `capacity`. Запис `pos[id] = i` зберігає поточний індекс елемента з дескриптором `id` всередині масиву `heap[]`. Якщо об'єкт із таким `id` наразі відсутній у структурі, `pos[id] = -1`.

Для забезпечення математичної коректності структури даних на кожному кроці модифікації підтримується строгий двосторонній інваріант:

```
pos[heap[i].id] == i   для всіх 0 ≤ i < size
heap[pos[id]].id == id для всіх активних id (де pos[id] ≠ -1)
```

Будь-яка перестановка двох елементів `swap(heap[i], heap[j])` під час просіювання вгору або вниз зобов'язана синхронно оновлювати зворотні покажчики: `pos[heap[i].id] = i` та `pos[heap[j].id] = j`. Це забезпечує константний час `O(1)` для знаходження комірки будь-якого вузла в купі.

## Повна реалізація мовами C та C++

Нижче наведено промислову реалізацію індексованої Min-купи для цілочисельних ключів (пріоритетів), оптимізовану для використання в системах маршрутизації та мережевих графах.

:::tabs
== C
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <limits.h>

typedef struct {
    int id;
    int key;
} HeapNode;

typedef struct {
    HeapNode *data;
    int *pos;
    int size;
    int capacity;
} IndexedMinHeap;

IndexedMinHeap* indexed_heap_create(int capacity) {
    if (capacity <= 0) return NULL;
    IndexedMinHeap *h = (IndexedMinHeap*)malloc(sizeof(IndexedMinHeap));
    if (!h) return NULL;
    h->data = (HeapNode*)malloc(sizeof(HeapNode) * capacity);
    h->pos = (int*)malloc(sizeof(int) * capacity);
    if (!h->data || !h->pos) {
        free(h->data);
        free(h->pos);
        free(h);
        return NULL;
    }
    h->size = 0;
    h->capacity = capacity;
    for (int i = 0; i < capacity; ++i) {
        h->pos[i] = -1;
    }
    return h;
}

void indexed_heap_free(IndexedMinHeap *h) {
    if (!h) return;
    free(h->data);
    free(h->pos);
    free(h);
}

static inline void heap_swap(IndexedMinHeap *h, int i, int j) {
    HeapNode temp = h->data[i];
    h->data[i] = h->data[j];
    h->data[j] = temp;
    h->pos[h->data[i].id] = i;
    h->pos[h->data[j].id] = j;
}

static void sift_up(IndexedMinHeap *h, int i) {
    while (i > 0) {
        int p = (i - 1) / 2;
        if (h->data[i].key < h->data[p].key) {
            heap_swap(h, i, p);
            i = p;
        } else {
            break;
        }
    }
}

static void sift_down(IndexedMinHeap *h, int i) {
    while (2 * i + 1 < h->size) {
        int left = 2 * i + 1;
        int right = 2 * i + 2;
        int smallest = left;

        if (right < h->size && h->data[right].key < h->data[left].key) {
            smallest = right;
        }
        if (h->data[smallest].key < h->data[i].key) {
            heap_swap(h, i, smallest);
            i = smallest;
        } else {
            break;
        }
    }
}

bool indexed_heap_contains(const IndexedMinHeap *h, int id) {
    if (!h || id < 0 || id >= h->capacity) return false;
    return h->pos[id] != -1;
}

bool indexed_heap_push(IndexedMinHeap *h, int id, int key) {
    if (!h || h->size >= h->capacity || indexed_heap_contains(h, id)) {
        return false;
    }
    int idx = h->size++;
    h->data[idx].id = id;
    h->data[idx].key = key;
    h->pos[id] = idx;
    sift_up(h, idx);
    return true;
}

bool indexed_heap_pop(IndexedMinHeap *h, int *out_id, int *out_key) {
    if (!h || h->size == 0) return false;
    if (out_id) *out_id = h->data[0].id;
    if (out_key) *out_key = h->data[0].key;

    h->pos[h->data[0].id] = -1;
    h->size--;
    if (h->size > 0) {
        h->data[0] = h->data[h->size];
        h->pos[h->data[0].id] = 0;
        sift_down(h, 0);
    }
    return true;
}

bool indexed_heap_decrease_key(IndexedMinHeap *h, int id, int new_key) {
    if (!h || !indexed_heap_contains(h, id)) return false;
    int idx = h->pos[id];
    if (new_key > h->data[idx].key) return false;
    h->data[idx].key = new_key;
    sift_up(h, idx);
    return true;
}

bool indexed_heap_increase_key(IndexedMinHeap *h, int id, int new_key) {
    if (!h || !indexed_heap_contains(h, id)) return false;
    int idx = h->pos[id];
    if (new_key < h->data[idx].key) return false;
    h->data[idx].key = new_key;
    sift_down(h, idx);
    return true;
}

bool indexed_heap_delete(IndexedMinHeap *h, int id) {
    if (!h || !indexed_heap_contains(h, id)) return false;
    int idx = h->pos[id];
    int old_key = h->data[idx].key;
    h->pos[id] = -1;
    h->size--;

    if (idx == h->size) {
        return true;
    }

    h->data[idx] = h->data[h->size];
    h->pos[h->data[idx].id] = idx;

    if (h->data[idx].key < old_key) {
        sift_up(h, idx);
    } else {
        sift_down(h, idx);
    }
    return true;
}
```
== C++
```cpp
#include <vector>
#include <optional>
#include <stdexcept>
#include <utility>
#include <concepts>

template <typename Key = int, typename Compare = std::less<Key>>
class IndexedMinHeap {
public:
    struct Node {
        int id;
        Key key;
    };

    explicit IndexedMinHeap(size_t capacity, Compare comp = Compare{})
        : comp_(comp), pos_(capacity, -1) {
        data_.reserve(capacity);
    }

    [[nodiscard]] bool empty() const noexcept {
        return data_.empty();
    }

    [[nodiscard]] size_t size() const noexcept {
        return data_.size();
    }

    [[nodiscard]] size_t capacity() const noexcept {
        return pos_.size();
    }

    [[nodiscard]] bool contains(int id) const noexcept {
        if (id < 0 || static_cast<size_t>(id) >= pos_.size()) return false;
        return pos_[id] != -1;
    }

    [[nodiscard]] std::optional<Key> key_of(int id) const noexcept {
        if (!contains(id)) return std::nullopt;
        return data_[pos_[id]].key;
    }

    [[nodiscard]] std::optional<Node> top() const noexcept {
        if (empty()) return std::nullopt;
        return data_.front();
    }

    void push(int id, Key key) {
        if (id < 0 || static_cast<size_t>(id) >= pos_.size()) {
            throw std::out_of_range("ID out of indexed heap capacity");
        }
        if (contains(id)) {
            throw std::invalid_argument("ID already present in heap");
        }
        int idx = static_cast<int>(data_.size());
        data_.push_back(Node{id, std::move(key)});
        pos_[id] = idx;
        sift_up(idx);
    }

    Node pop() {
        if (empty()) {
            throw std::runtime_error("Pop from empty indexed heap");
        }
        Node root = data_.front();
        pos_[root.id] = -1;

        if (data_.size() == 1) {
            data_.pop_back();
        } else {
            data_.front() = std::move(data_.back());
            data_.pop_back();
            pos_[data_.front().id] = 0;
            sift_down(0);
        }
        return root;
    }

    void decrease_key(int id, Key new_key) {
        if (!contains(id)) {
            throw std::invalid_argument("ID not found in heap");
        }
        int idx = pos_[id];
        if (comp_(data_[idx].key, new_key)) {
            throw std::invalid_argument("New key is greater in decrease_key");
        }
        data_[idx].key = std::move(new_key);
        sift_up(idx);
    }

    void increase_key(int id, Key new_key) {
        if (!contains(id)) {
            throw std::invalid_argument("ID not found in heap");
        }
        int idx = pos_[id];
        if (comp_(new_key, data_[idx].key)) {
            throw std::invalid_argument("New key is smaller in increase_key");
        }
        data_[idx].key = std::move(new_key);
        sift_down(idx);
    }

    void erase(int id) {
        if (!contains(id)) return;
        int idx = pos_[id];
        Key old_key = data_[idx].key;
        pos_[id] = -1;

        if (idx == static_cast<int>(data_.size()) - 1) {
            data_.pop_back();
            return;
        }

        data_[idx] = std::move(data_.back());
        data_.pop_back();
        pos_[data_[idx].id] = idx;

        if (comp_(data_[idx].key, old_key)) {
            sift_up(idx);
        } else {
            sift_down(idx);
        }
    }

private:
    Compare comp_;
    std::vector<Node> data_;
    std::vector<int> pos_;

    void swap_nodes(int i, int j) noexcept {
        std::swap(data_[i], data_[j]);
        pos_[data_[i].id] = i;
        pos_[data_[j].id] = j;
    }

    void sift_up(int i) {
        while (i > 0) {
            int p = (i - 1) / 2;
            if (comp_(data_[i].key, data_[p].key)) {
                swap_nodes(i, p);
                i = p;
            } else {
                break;
            }
        }
    }

    void sift_down(int i) {
        int n = static_cast<int>(data_.size());
        while (2 * i + 1 < n) {
            int left = 2 * i + 1;
            int right = 2 * i + 2;
            int best = left;

            if (right < n && comp_(data_[right].key, data_[left].key)) {
                best = right;
            }
            if (comp_(data_[best].key, data_[i].key)) {
                swap_nodes(i, best);
                i = best;
            } else {
                break;
            }
        }
    }
};
```
:::

## Аналіз крайових випадків та відновлення інваріантів

Під час експлуатації індексованої купи виникає кілька тонких ситуацій, у яких некоректне оновлення масиву `pos[]` призводить до фатального розсинхрону пам'яті:

### 1. Видалення останнього елемента масиву
Якщо вузол, що підлягає видаленню, вже розташований на останній позиції масиву (`idx == size - 1`), процедура заміни коренем останнього елемента не потрібна. Достатньо лише встановити `pos[id] = -1` та зменшити лічильник `size--`. Спроба виконати `swap` або самоперепризначення у цій ситуації може перезаписати валідні індекси.

### 2. Заміна внутрішнього вузла останнім елементом
Коли видаляється довільний внутрішній вузол `idx < size - 1`, його місце займає останній елемент масиву `heap[size - 1]`. Новий ключ, що опинився в позиції `idx`, може бути як меншим, так і більшим за ключ видаленого вузла:
- Якщо новий ключ менший за старий, елемент міг порушити інваріант відносно батька — викликається `sift_up(idx)`;
- Якщо новий ключ більший або рівний старому, елемент міг порушити інваріант відносно дітей — викликається `sift_down(idx)`.
Ця перевірка дозволяє уникнути двох непотрібних повних просіювань, гарантуючи виконання лише одного спрямованого руху.

### 3. Оновлення масиву позицій при динамічній зміні розміру
Якщо місткість купи `capacity` вичерпано і потрібне динамічне розширення вектора, розмір масиву `pos[]` повинен бути збільшений відповідно до нового діапазону дескрипторів `id`. При цьому всі новостворені комірки `pos[id]` обов'язково ініціалізуються маркерним значенням `-1`.

## Застосування: алгоритм Дейкстри без надлишкових дублікатів

У багатьох аматорських реалізаціях алгоритму Дейкстри на базі стандартного `std::priority_queue` оновлення коротшої відстані до вершини моделюється простим додаванням нової пари `(dist, vertex)` у хвіст купи. Оскільки стандартна купа не має методу видалення або оновлення існуючого елемента, старі довші шляхи залишаються в купі як сміття («ліниве видалення»).

Цей підхід має суттєві недоліки:
- Розмір черги у найгіршому випадку розростається до загальної кількості ребер `O(E)`, що збільшує витрати оперативної пам'яті;
- Час кожної операції вилучення зростає до `O(log E)`, а загальна кількість викликів `pop()` становить `O(E)` замість `O(V)`;
- У щільних графах виникає значний оверхед на кеш-промахи через перекачування непотрібних дублікатів.

З використанням індексованої двійкової купи кожна вершина графа `v` присутня в купі щонайбільше в одному екземплярі:
1. Якщо вершина `to` ще не була додана до черги, викликається `push(to, new_dist)`.
2. Якщо вершина вже знаходиться в купі й знайдено коротший шлях, викликається `decrease_key(to, new_dist)`.
3. Вилучення мінімальної вершини `pop()` виконується рівно `V` разів, а кількість операцій зміни пріоритету не перевищує `E`.

Це забезпечує класичну асимптотичну складність `O((V + E) log V)` при строго детермінованому використанні пам'яті `O(V)`.

## Практичний вибір: Індексована двійкова купа чи Фібоначчієва купа?

У теоретичному аналізі алгоритмів на графах Фібоначчієва купа (Fibonacci Heap) вважається кращою, оскільки забезпечує час `O(1)` для операції `decrease-key` проти `O(log V)` у двійкової купи, що знижує загальний час алгоритму Дейкстри до `O(E + V log V)`.

Проте в реальних мережевих протоколах (таких як реалізації OSPF та IS-IS у ядрах Linux та роутерах Cisco/Juniper) майже завжди використовується саме індексована двійкова (або 4-арна) купа. Причини цього суто практичні:
- **Константний множник**: Фібоначчієва купа вимагає виділення динамічних об'єктів у купі з чотирма покажчиками на кожен вузол (`parent`, `child`, `left`, `right`), що спричиняє постійні кеш-промахи при навігації вказівниками.
- **Кеш-локальність**: Індексована купа зберігається у двох щільних одновимірних масивах. При просіюванні процесор ефективно використовує апаратний префетчер L1/L2 кешу.
- **Обсяг графів**: Для більшості практичних графів мереж (де `V < 10^6`) висота дерева `log_2(V) ≤ 20`. Двадцять простих порівнянь у кеші процесора виконуються в рази швидше, ніж розплутування списків Фібоначчієвого дерева.
