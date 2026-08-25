# ⚙️ Реалізація біноміальної купи мовами C та C++

Ця вставка містить повну, виробничо-готову та ідіоматичну реалізацію біноміальної купи (Binomial Heap) мовами **C** та **C++**. Наведено детальний розбір ключових алгоритмічних блоків, покрокове простеження дій при вставці та вилученні, а також аналіз практичних підводних каменів керування пам'яттю.

---

## 1. Архітектурні деталі та зв'язування дерев

Кожен вузол біноміального дерева зберігає ключ, свій степінь (`degree`) та три вказівники за схемою *Left-Child, Right-Sibling*:
- `parent` — батьківський вузол (`NULL` для коренів лісу);
- `child` — найлівіша дитина (перше дерево у списку дітей);
- `sibling` — наступний правий брат у списку (для коренів — наступне дерево у кореневому списку; для дітей — наступна дитина одного батька).

Ключовою атомарною операцією є **зв'язування двох дерев одинакового степеня** `binomial_link(y, z)`: корінь `y` стає найлівішою дитиною кореня `z` (припускаючи `z->key <= y->key`).

```
       z (key=10)                z (key=10)
      /                         / \
     ◯                         y   ◯
                              /
                             ◯
       y (key=15)           (y додається як найлівіша дитина z)
      /
     ◯
```

Ця дія виконується за сталий час `O(1)` шляхом перепризначення кількох вказівників: `y->parent = z`, `y->sibling = z->child`, `z->child = y`, `z->degree++`.

---

## 2. Реалізація мовами C та C++

Переключення між мовами доступне у вкладках нижче. Версія мовою C демонструє Низькорівневе керування вказівниками та вручну виділеною пам'яттю, тоді як версія на C++ пропонує шаблонізований клас із гарантіями RAII та автоматичним вивільненням ресурсів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <stdbool.h>

// Вузол біноміального дерева
typedef struct BinomialNode {
    int key;
    int degree;
    struct BinomialNode *parent;
    struct BinomialNode *child;
    struct BinomialNode *sibling;
} BinomialNode;

// Створення нового вузла
BinomialNode* node_create(int key) {
    BinomialNode* node = (BinomialNode*)malloc(sizeof(BinomialNode));
    if (!node) return NULL;
    node->key = key;
    node->degree = 0;
    node->parent = NULL;
    node->child = NULL;
    node->sibling = NULL;
    return node;
}

// Зв'язування двох дерев B_k з утворенням B_{k+1}
// Вузол y робиться дитиною вузла z (припускається z->key <= y->key)
static void binomial_link(BinomialNode* y, BinomialNode* z) {
    y->parent = z;
    y->sibling = z->child;
    z->child = y;
    z->degree++;
}

// Злиття двох відсортованих списків коренів за зростанням степеня (як у MergeSort)
static BinomialNode* merge_root_lists(BinomialNode* h1, BinomialNode* h2) {
    if (!h1) return h2;
    if (!h2) return h1;

    BinomialNode* head = NULL;
    BinomialNode** tail = &head;

    while (h1 && h2) {
        if (h1->degree <= h2->degree) {
            *tail = h1;
            h1 = h1->sibling;
        } else {
            *tail = h2;
            h2 = h2->sibling;
        }
        tail = &((*tail)->sibling);
    }
    *tail = h1 ? h1 : h2;
    return head;
}

// Основна операція: об'єднання двох біноміальних куп
BinomialNode* binomial_heap_union(BinomialNode* h1, BinomialNode* h2) {
    BinomialNode* head = merge_root_lists(h1, h2);
    if (!head) return NULL;

    BinomialNode* prev = NULL;
    BinomialNode* curr = head;
    BinomialNode* next = curr->sibling;

    while (next) {
        // Випадок 1 і 2: степені різні АБО три послідовні дерева мають одинаковий степінь
        if ((curr->degree != next->degree) ||
            (next->sibling && next->sibling->degree == curr->degree)) {
            prev = curr;
            curr = next;
        } else {
            // Випадок 3 і 4: однакові степені — об'єднуємо у відповідну сторону
            if (curr->key <= next->key) {
                curr->sibling = next->sibling;
                binomial_link(next, curr);
            } else {
                if (!prev) {
                    head = next;
                } else {
                    prev->sibling = next;
                }
                binomial_link(curr, next);
                curr = next;
            }
        }
        next = curr->sibling;
    }
    return head;
}

// Вставка нового ключа у купу
BinomialNode* binomial_heap_insert(BinomialNode* heap, int key) {
    BinomialNode* temp = node_create(key);
    return binomial_heap_union(heap, temp);
}

// Пошук вузла з мінімальним ключем серед коренів
BinomialNode* binomial_heap_find_min(BinomialNode* heap) {
    if (!heap) return NULL;
    BinomialNode* min_node = heap;
    BinomialNode* curr = heap->sibling;
    while (curr) {
        if (curr->key < min_node->key) {
            min_node = curr;
        }
        curr = curr->sibling;
    }
    return min_node;
}

// Допоміжна функція розвороту списку дітей
static BinomialNode* reverse_list(BinomialNode* node) {
    BinomialNode* prev = NULL;
    BinomialNode* curr = node;
    while (curr) {
        BinomialNode* next = curr->sibling;
        curr->sibling = prev;
        curr->parent = NULL; // Корені нової купи не мають батька
        prev = curr;
        curr = next;
    }
    return prev;
}

// Вилучення мінімального ключа з купи
BinomialNode* binomial_heap_extract_min(BinomialNode* heap, int* out_min_key) {
    if (!heap) return NULL;

    // 1. Знаходимо мінімальний корінь та його попередника у списку
    BinomialNode* min_node = heap;
    BinomialNode* min_prev = NULL;

    BinomialNode* curr = heap;
    BinomialNode* prev = NULL;

    while (curr) {
        if (curr->key < min_node->key) {
            min_node = curr;
            min_prev = prev;
        }
        prev = curr;
        curr = curr->sibling;
    }

    if (out_min_key) *out_min_key = min_node->key;

    // 2. Вилучаємо min_node зі списку коренів
    if (min_prev) {
        min_prev->sibling = min_node->sibling;
    } else {
        heap = min_node->sibling;
    }

    // 3. Розвертаємо список дітей min_node, утворюючи нову купу
    BinomialNode* child_heap = reverse_list(min_node->child);
    free(min_node);

    // 4. Об'єднуємо залишок купи з новою купою дітей
    return binomial_heap_union(heap, child_heap);
}

// Зменшення ключа вузла
void binomial_heap_decrease_key(BinomialNode* node, int new_key) {
    if (!node || new_key > node->key) return;

    node->key = new_key;
    BinomialNode* curr = node;
    BinomialNode* parent = curr->parent;

    // Просіювання вгору (sift-up)
    while (parent && curr->key < parent->key) {
        // Обмін значеннями ключів
        int temp = curr->key;
        curr->key = parent->key;
        parent->key = temp;

        curr = parent;
        parent = curr->parent;
    }
}

// Рекурсивне звільнення пам'яті купи
void binomial_heap_free(BinomialNode* heap) {
    while (heap) {
        BinomialNode* sibling = heap->sibling;
        if (heap->child) {
            binomial_heap_free(heap->child);
        }
        free(heap);
        heap = sibling;
    }
}
```
```cpp
#include <iostream>
#include <memory>
#include <optional>
#include <stdexcept>
#include <utility>

namespace ds {

template <typename T>
class BinomialHeap {
private:
    struct Node {
        T key;
        int degree{0};
        Node* parent{nullptr};
        Node* child{nullptr};
        Node* sibling{nullptr};

        explicit Node(T val) : key(std::move(val)) {}
    };

    Node* head_{nullptr};

    static void link_trees(Node* y, Node* z) {
        y->parent = z;
        y->sibling = z->child;
        z->child = y;
        z->degree++;
    }

    static Node* merge_root_lists(Node* h1, Node* h2) {
        if (!h1) return h2;
        if (!h2) return h1;

        Node* head = nullptr;
        Node** tail = &head;

        while (h1 && h2) {
            if (h1->degree <= h2->degree) {
                *tail = h1;
                h1 = h1->sibling;
            } else {
                *tail = h2;
                h2 = h2->sibling;
            }
            tail = &((*tail)->sibling);
        }
        *tail = h1 ? h1 : h2;
        return head;
    }

    static Node* union_heaps(Node* h1, Node* h2) {
        Node* head = merge_root_lists(h1, h2);
        if (!head) return nullptr;

        Node* prev = nullptr;
        Node* curr = head;
        Node* next = curr->sibling;

        while (next) {
            if ((curr->degree != next->degree) ||
                (next->sibling && next->sibling->degree == curr->degree)) {
                prev = curr;
                curr = next;
            } else {
                if (curr->key <= next->key) {
                    curr->sibling = next->sibling;
                    link_trees(next, curr);
                } else {
                    if (!prev) {
                        head = next;
                    } else {
                        prev->sibling = next;
                    }
                    link_trees(curr, next);
                    curr = next;
                }
            }
            next = curr->sibling;
        }
        return head;
            }

    static Node* reverse_list(Node* node) {
        Node* prev = nullptr;
        Node* curr = node;
        while (curr) {
            Node* next = curr->sibling;
            curr->sibling = prev;
            curr->parent = nullptr;
            prev = curr;
            curr = next;
        }
        return prev;
    }

    static void destroy_tree(Node* node) {
        while (node) {
            Node* next = node->sibling;
            if (node->child) {
                destroy_tree(node->child);
            }
            delete node;
            node = next;
        }
    }

public:
    using NodeHandle = Node*;

    BinomialHeap() = default;
    
    ~BinomialHeap() {
        destroy_tree(head_);
    }

    BinomialHeap(const BinomialHeap&) = delete;
    BinomialHeap& operator=(const BinomialHeap&) = delete;

    BinomialHeap(BinomialHeap&& other) noexcept : head_(other.head_) {
        other.head_ = nullptr;
    }

    BinomialHeap& operator=(BinomialHeap&& other) noexcept {
        if (this != &other) {
            destroy_tree(head_);
            head_ = other.head_;
            other.head_ = nullptr;
        }
        return *this;
    }

    [[nodiscard]] bool empty() const noexcept {
        return head_ == nullptr;
    }

    NodeHandle insert(T key) {
        auto* node = new Node(std::move(key));
        head_ = union_heaps(head_, node);
        return node;
    }

    void merge(BinomialHeap& other) {
        if (this == &other) return;
        head_ = union_heaps(head_, other.head_);
        other.head_ = nullptr;
    }

    [[nodiscard]] std::optional<T> find_min() const {
        if (!head_) return std::nullopt;
        Node* min_node = head_;
        Node* curr = head_->sibling;
        while (curr) {
            if (curr->key < min_node->key) {
                min_node = curr;
            }
            curr = curr->sibling;
        }
        return min_node->key;
    }

    T extract_min() {
        if (!head_) {
            throw std::underflow_error("BinomialHeap is empty");
        }

        Node* min_node = head_;
        Node* min_prev = nullptr;
        Node* curr = head_;
        Node* prev = nullptr;

        while (curr) {
            if (curr->key < min_node->key) {
                min_node = curr;
                min_prev = prev;
            }
            prev = curr;
            curr = curr->sibling;
        }

        if (min_prev) {
            min_prev->sibling = min_node->sibling;
        } else {
            head_ = min_node->sibling;
        }

        Node* child_heap = reverse_list(min_node->child);
        T min_val = std::move(min_node->key);
        delete min_node;

        head_ = union_heaps(head_, child_heap);
        return min_val;
    }

    void decrease_key(NodeHandle handle, T new_key) {
        if (!handle || new_key > handle->key) {
            throw std::invalid_argument("New key must be smaller than current key");
        }

        handle->key = std::move(new_key);
        Node* curr = handle;
        Node* parent = curr->parent;

        while (parent && curr->key < parent->key) {
            std::swap(curr->key, parent->key);
            curr = parent;
            parent = curr->parent;
        }
    }
};

} // namespace ds
```
:::

---

## 3. Практичні підводні камені та тонкощі реалізації

Під час проектування та підтримання біноміальної купи в реальних програмних продуктах розробники найчастіше стикаються з трьома критичними підводними каміннями.

### 3.1. Необхідність розвороту списку дітей при `extract_min`

Розглянемо вилучення мінімального кореня `min_node`. Усі його діти зв'язані за допомогою вказівників `sibling`. Проте за інваріантом біноміального дерева ці діти розташовані у порядку **спадання степенів**: від `B_{k-1}` до `B_0`.

Які наслідки виникнуть, якщо передати цей список у функцію `union_heaps` без попереднього розвороту?
1. Переданий список порушуватиме інваріант суворого зростання коренів.
2. Процедура `merge_root_lists` не зможе правильно злити два списки за логарифмічний час, що призведе до збоїв при об'єднанні однакових степенів та руйнування всієї структури купи.

Саме тому функція `reverse_list` є обов'язковим елементом операції `extract_min`. Вона обертає вказівники `sibling` так, що діти шикуються у порядку `B_0, B_1, ..., B_{k-1}`, перетворюючись на коректну біноміальну купу.

### 3.2. Обробка трьох послідовних однаковим степенів при злитті

Під час роботи другого етапу функції `binomial_heap_union` виникає ситуація, коли три послідовні дерева `curr`, `next` та `next->sibling` мають один і той самий степінь `k`. 

Це відбувається при додаванні переносу від попередньої пари дерев до двох наявних дерев поточного розряду.

Якщо неуважно злити перше дерево `curr` із другом `next`, ми отримаємо дерево степеня `k+1`, але після цього у списку залишиться дерево `next->sibling` степеня `k`. У результаті порушиться впорядкованість списку за степенями (степінь `k+1` опиниться раніше за степінь `k`).

Правильне вирішення (Випадок 2 у коді): при виявленні трьох послідовних дерев однакового степеня слід **ігнорувати перше дерево `curr` і зливати друге з третім**. Це зберігає впорядкованість списку і правильно обробляє перенос у наступний розряд.

### 3.3. Збереження дескрипторів вузлів у `decrease_key`

У багатьох практичних алгоритмах (зокрема у алгоритмі Дійкстри) користувач зберігає зовнішні вказівники на вузли купи (`NodeHandle`), щоб пізніше швидко викликати `decrease_key`.

При виконанні просіювання вгору (sift-up) є дві стратегії відновлення інваріанта купи:
1. **Стратегія А:** Обмінювати значення полів `key` між батьком і дитиною.
2. **Стратегія Б:** Перепризначувати самі вказівники `parent`, `child` та `sibling`, переміщуючи вузли в дереві.

Стратегія Б виглядає привабливо, але вона є катастрофічною: зміна зв'язків вузлів у пам'яті призводить до того, що зовнішні вказівники `NodeHandle` починають вказувати на інші елементи дерева, що повністю ламає логіку зовнішнього алгоритму.

У наведених реалізаціях мовами C та C++ застосовано **Стратегію А**: під час просіювання вгору обмінюються лише значення `key`, завдяки чому вузли залишаються на своїх місцях у пам'яті, а зовнішні дескриптори `NodeHandle` зберігають свою дійсність.

---

## 4. Оптимізація виділення пам'яті: Пул-алокатори (Pool Allocation)

Виділення пам'яті під один вузол `sizeof(BinomialNode)` через стандартні функції `malloc` або `operator new` створює високі накладні витрати часу та спричиняє фрагментацію купи операційної системи. Оскільки кожен вузол є дрібним об'єктом (40 байтів), викликати системний алокатор на кожну вставку стає неефективним на гарячих шляхах обчислень.

Для підвищення продуктивності в системному програмуванні застосовують **алокатор пулу (Pool Allocator)** або арену пам'яті (Memory Arena):
1. Пам'ять під вузли виділяється великими блоками (наприклад, по 1024 вузли за один системний виклик `malloc`).
2. Вільні вузли організовуються у зв'язаний список вільних блоків (Free List).
3. Операція `node_create` бере вузол із голови Free List за сталий час `O(1)` без системних викликів.
4. При вилученні вузла в `extract_min` або `free` вузол повертається у Free List за `O(1)`.

Цей підхід суттєво покращує локальність даних у кеші процесора (L1/L2 data cache), оскільки суміжні вузли дерев розташовуються поруч у фізичній пам'яті.

---

## 5. Покрокове простеження (Trace) вставки та вилучення

### 5.1. Покрокова вставка елементів
Розглянемо покроковий приклад створення біноміальної купи шляхом послідовного додавання ключів: `{10, 20, 5, 15}`.

1. **Вставка 10:** Створюється `B_0(10)`. Купа містить: `[B_0(10)]`.
2. **Вставка 20:** Створюється `B_0(20)`. При злитті з `B_0(10)` два `B_0` утворюють `B_1` з коренем 10 та дитиною 20. Купа містить: `[B_1(10)]`.
3. **Вставка 5:** Створюється `B_0(5)`. Оскільки степені 0 та 1 різні, злиття просто додає `B_0(5)` у корінь списку. Купа містить: `[B_0(5), B_1(10)]`. (Загалом 3 елементи = `011₂`).
4. **Вставка 15:** Створюється `B_0(15)`. 
   - `B_0(15)` та `B_0(5)` зливаються в `B_1(5)` з дитиною 15.
   - Тепер ми маємо два дерева `B_1`: `B_1(5)` та наявне `B_1(10)`.
   - Зливаємо їх у `B_2(5)`: корінь 5 бере дитиною корінь 10.
   - Результат: купа з 4 елементів (`100₂`), яка складається з єдиного дерева `B_2` з коренем 5.

### 5.2. Покрокове вилучення мінімуму з купи з 4 елементів
Виконаємо `extract_min` над купою, створеною на попередньому кроці (дерево `B_2(5)`):
1. Скануємо кореневий список, корінь з найменшим ключем — `5`.
2. Вилучаємо корінь 5. Його дітьми є корені дерев `B_1(10)` та `B_0(15)`.
3. Список дітей до розвороту: `B_1(10) -> B_0(15)`.
4. Розвертаємо список дітей: одержуємо нову купу `H'' = [B_0(15), B_1(10)]`.
5. Початкова купа після вилучення кореня стала порожньою: `H' = NULL`.
6. Зливаємо `H'` та `H''`: результатом є купа з 3 елементів `[B_0(15), B_1(10)]`. Повернутий мінімальний ключ — 5.
