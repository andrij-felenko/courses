# ⚙️ Вартові вузли на практиці: список і червоно-чорне дерево

У структурах даних на динамічних покажчиках — зв'язних списках, бінарних деревах, префіксних деревах — найбільша кількість логічних помилок і збоїв стається на крайових умовах: вставка першого елемента в порожній список, видалення єдиного вузла, робота з коренем або листям дерева. Кожна така операція у звичайному коді вимагає серії перевірок `if (node == NULL)`, що захаращують алгоритм і створюють постійне навантаження на блок передбачення переходів процесора (англ. *branch predictor*).

Техніка **вартового вузла** (англ. *sentinel node* або *dummy node*) розв'язує цю проблему архітектурно: замість нульового покажчика кінці структури замикаються на спеціальний виділений вузол, який гарантовано завжди присутній у пам'яті.

---

### Лінійний пошук із вартовим: як усунути перевірку межі масиву

Найпростіший і водночас найбільш показовий приклад вартового в алгоритмах — це оптимізація лінійного пошуку в масиві.

У класичному лінійному пошуку кожна ітерація циклу виконує **дві перевірки**:
1. Чи не дійшли ми до кінця масиву: `i < n`.
2. Чи не знайшли ми шуканий елемент: `arr[i] == target`.

Якщо виділити в масиві одну додаткову комірку наприкінці (`arr[n]`) і перед початком пошуку записати туди шукане значення `target` як вартового, перша перевірка стає непотрібною. Елемент гарантовано буде знайдено — або в середині масиву, або в останній комірці-вартовому.

:::tabs
```c
#include <stdio.h>
#include <stddef.h>

// Класичний пошук: 2 розгалуження на кожну ітерацію циклу
size_t linear_search_classic(const int* arr, size_t n, int target) {
    for (size_t i = 0; i < n; ++i) {
        if (arr[i] == target) {
            return i;
        }
    }
    return (size_t)-1;
}

// Пошук із вартовим: рівно 1 розгалуження в тілі циклу!
// Масив arr повинен мати виділений розмір щонайменше (n + 1).
size_t linear_search_sentinel(int* arr, size_t n, int target) {
    arr[n] = target; // Ставимо вартового на кінець масиву
    size_t i = 0;
    while (arr[i] != target) {
        i++;
    }
    // Якщо зупинилися до n — елемент справжній, якщо на n — спрацював вартовий
    return (i < n) ? i : (size_t)-1;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cstddef>
#include <optional>

// Шаблонний лінійний пошук із вартовим у C++
template <typename T>
std::optional<std::size_t> search_with_sentinel(std::vector<T>& vec, const T& target) {
    if (vec.empty()) {
        return std::nullopt;
    }

    const std::size_t n = vec.size();
    vec.push_back(target); // Додаємо вартового в кінець буфера

    std::size_t i = 0;
    while (vec[i] != target) {
        ++i;
    }

    vec.pop_back(); // Прибираємо вартового

    if (i < n) {
        return i;
    }
    return std::nullopt;
}
```
:::

У внутрішніх циклах, що обробляють мільйони записів, скорочення кількості умовних переходів удвічі дає відчутний виграш у тактах процесора за рахунок усунення хибних передбачень переходів.

---

### Порівняння: двозв'язний список без вартового і з вартовим

Подивімося на фундаментальну різницю в кількості умовних переходів при видаленні вузла `node` зі списку.

У звичайному списку, де покажчики `head` і `tail` ініціалізуються значенням `NULL`, операція видалення мусить перевірити чотири незалежні гілки:
1. Чи є у вузла попередник (`node->prev != NULL`), чи це була голова списку.
2. Чи є у вузла наступник (`node->next != NULL`), чи це був хвіст списку.

У списку з круговим вартовим вузлом корінь списку — це не окремі змінні-покажчики, а фіктивний вузол `sentinel`, що з'єднує перший та останній елементи в нескінченне кільце. Список ніколи не буває «порожнім» на рівні пам'яті: у порожньому списку `sentinel.next == &sentinel` і `sentinel.prev == &sentinel`.

```
Звичайний список (краї = NULL)           Список із круговим вартовим (Sentinel)
------------------------------------     ------------------------------------
if (node->prev != NULL) {                node->prev->next = node->next;
    node->prev->next = node->next;       node->next->prev = node->prev;
} else {
    list->head = node->next;             (рівно 2 присвоєння покажчиків,
}                                         нуль розгалужень if-else!)
if (node->next != NULL) {
    node->next->prev = node->prev;
} else {
    list->tail = node->prev;
}
```

---

### Робоча реалізація: круговий двозв'язний список

Нижче наведено повноцінну реалізацію двозв'язного списку з вартовим вузлом мовами C та C++. Зверніть увагу на функцію `list_insert_before`: вона є єдиною точкою вставки для будь-яких операцій (вставка на початок, у кінець або всередину списку).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

// Вузол списку: містить корисне навантаження та зв'язки
typedef struct Node {
    int value;
    struct Node* prev;
    struct Node* next;
} Node;

// Структура списку: тримає фіктивний вартовий вузол прямо за значенням
typedef struct List {
    Node sentinel;
    size_t size;
} List;

// Ініціалізація: вартовий вузол замикається сам на себе
void list_init(List* list) {
    list->sentinel.next = &list->sentinel;
    list->sentinel.prev = &list->sentinel;
    list->sentinel.value = 0; // Значення вартового ніколи не читається
    list->size = 0;
}

// Універсальна вставка НОВОГО вузла ПЕРЕД вказаним вузлом pos.
// Завдяки вартовому працює однаково для вставки на початок, в кінець чи всередину!
void list_insert_before(List* list, Node* pos, int value) {
    Node* new_node = (Node*)malloc(sizeof(Node));
    if (!new_node) return;

    new_node->value = value;
    new_node->next = pos;
    new_node->prev = pos->prev;

    pos->prev->next = new_node;
    pos->prev = new_node;

    list->size++;
}

void list_push_back(List* list, int value) {
    // Вставка в кінець = вставка перед вартовим вузлом!
    list_insert_before(list, &list->sentinel, value);
}

void list_push_front(List* list, int value) {
    // Вставка на початок = вставка перед першим елементом (sentinel.next)!
    list_insert_before(list, list->sentinel.next, value);
}

// Універсальне видалення вузла: жодного розгалуження if
void list_remove(List* list, Node* node) {
    if (node == &list->sentinel) return; // Захист: не можна видаляти вартового

    node->prev->next = node->next;
    node->next->prev = node->prev;

    free(node);
    list->size--;
}

void list_clear(List* list) {
    Node* curr = list->sentinel.next;
    while (curr != &list->sentinel) {
        Node* next = curr->next;
        free(curr);
        curr = next;
    }
    list_init(list);
}

void list_print(const List* list) {
    printf("List (size=%zu): [ ", list->size);
    for (Node* curr = list->sentinel.next; curr != &list->sentinel; curr = curr->next) {
        printf("%d ", curr->value);
    }
    printf("]\n");
}

int main(void) {
    List l;
    list_init(&l);

    list_push_back(&l, 10);
    list_push_back(&l, 20);
    list_push_front(&l, 5);
    list_print(&l); // [ 5 10 20 ]

    // Видаляємо перший реальний елемент
    list_remove(&l, l.sentinel.next);
    list_print(&l); // [ 10 20 ]

    list_clear(&l);
    return 0;
}
```
```cpp
#include <iostream>
#include <cstddef>
#include <utility>

// Шаблонний круговий двозв'язний список з вартовим вузлом
template <typename T>
class SentinelList {
    struct NodeBase {
        NodeBase* prev{nullptr};
        NodeBase* next{nullptr};
    };

    struct Node : public NodeBase {
        T value;
        template <typename... Args>
        explicit Node(Args&&... args) : value(std::forward<Args>(args)...) {}
    };

    NodeBase sentinel_{};
    std::size_t size_{0};

    void reset_sentinel() noexcept {
        sentinel_.next = &sentinel_;
        sentinel_.prev = &sentinel_;
        size_ = 0;
    }

public:
    SentinelList() noexcept {
        reset_sentinel();
    }

    ~SentinelList() {
        clear();
    }

    SentinelList(const SentinelList&) = delete;
    SentinelList& operator=(const SentinelList&) = delete;

    SentinelList(SentinelList&& other) noexcept {
        if (other.empty()) {
            reset_sentinel();
        } else {
            sentinel_.next = other.sentinel_.next;
            sentinel_.prev = other.sentinel_.prev;
            sentinel_.next->prev = &sentinel_;
            sentinel_.prev->next = &sentinel_;
            size_ = other.size_;
            other.reset_sentinel();
        }
    }

    [[nodiscard]] bool empty() const noexcept { return size_ == 0; }
    [[nodiscard]] std::size_t size() const noexcept { return size_; }

    template <typename... Args>
    void emplace_back(Args&&... args) {
        // Вставка в кінець — це вставка перед sentinel_
        insert_before(&sentinel_, std::forward<Args>(args)...);
    }

    template <typename... Args>
    void emplace_front(Args&&... args) {
        // Вставка на початок — це вставка перед першим елементом
        insert_before(sentinel_.next, std::forward<Args>(args)...);
    }

    void pop_front() noexcept {
        if (!empty()) {
            remove_node(static_cast<Node*>(sentinel_.next));
        }
    }

    void pop_back() noexcept {
        if (!empty()) {
            remove_node(static_cast<Node*>(sentinel_.prev));
        }
    }

    void clear() noexcept {
        NodeBase* curr = sentinel_.next;
        while (curr != &sentinel_) {
            NodeBase* next = curr->next;
            delete static_cast<Node*>(curr);
            curr = next;
        }
        reset_sentinel();
    }

    void print() const {
        std::cout << "List (size=" << size_ << "): [ ";
        for (NodeBase* curr = sentinel_.next; curr != &sentinel_; curr = curr->next) {
            std::cout << static_cast<Node*>(curr)->value << " ";
        }
        std::cout << "]\n";
    }

private:
    template <typename... Args>
    void insert_before(NodeBase* pos, Args&&... args) {
        auto* new_node = new Node(std::forward<Args>(args)...);
        new_node->next = pos;
        new_node->prev = pos->prev;

        pos->prev->next = new_node;
        pos->prev = new_node;

        ++size_;
    }

    void remove_node(Node* node) noexcept {
        node->prev->next = node->next;
        node->next->prev = node->prev;
        delete node;
        --size_;
    }
};

int main() {
    SentinelList<int> list;
    list.emplace_back(100);
    list.emplace_back(200);
    list.emplace_front(50);
    list.print(); // [ 50 100 200 ]

    list.pop_front();
    list.print(); // [ 100 200 ]

    return 0;
}
```
:::

---

### Вартові вузли в червоно-чорних деревах (Red-Black Trees)

У класичному підручнику Кормена, Лейзерсона, Рівеста та Стайна (CLRS) «Вступ до алгоритмів» реалізація збалансованих червоно-чорних дерев базується на використанні єдиного спільного вартового вузла `T.nil`.

У червоно-чорному дереві кожне листя (відсутня дитина) та батько кореня вказують на `T.nil`, колір якого жорстко зафіксований як **BLACK** (чорний).

```
          [ Корень: 20 (Black) ]
               /            \
     [ 10 (Red) ]       [ 30 (Black) ]
       /       \            /       \
   T.nil     T.nil      T.nil     T.nil
 (Black)   (Black)    (Black)   (Black)
```

Властивості червоно-чорного дерева вимагають, щоб усі нульові нащадки вважалися чорними вузлами. Якщо замість вартового використовувати `NULL`, то кожна перевірка кольору вузла в дереві повинна починатися з перевірки на нульовий покажчик:

:::tabs
```c
// Класична перевірка БЕЗ вартового: заплутана й повільна
typedef enum { RED, BLACK } Color;
typedef struct RBNode {
    int key;
    Color color;
    struct RBNode *left, *right, *parent;
} RBNode;

bool is_uncle_red_classic(RBNode* z) {
    if (z->parent != NULL && z->parent->parent != NULL) {
        RBNode* grandparent = z->parent->parent;
        if (grandparent->right != NULL && grandparent->right != z->parent) {
            return grandparent->right->color == RED;
        }
    }
    return false;
}
```
```cpp
// Елегантна перевірка З ВАРТОВИМ T.nil у C++
enum class RBColor : uint8_t { Red, Black };

struct RBNode {
    int key{0};
    RBColor color{RBColor::Black};
    RBNode* left{nullptr};
    RBNode* right{nullptr};
    RBNode* parent{nullptr};
};

bool is_uncle_red_sentinel(const RBNode* z, const RBNode* nil) noexcept {
    // Вказівник grandparent->right ніколи не дорівнює nullptr:
    // якщо вузла немає, він вказує на nil, колір якого завжди Black!
    const RBNode* uncle = z->parent->parent->right;
    return uncle->color == RBColor::Red;
}
```
:::

#### Переваги єдиного вартового `T.nil` в алгоритмах дерев:
1. **Спрощення лівих та правих обертань (`rotations`)**: під час обертання вузлів зв'язки переприв'язуються без перевірки, чи була присутня дитина у переміщуваного вузла. Батько `T.nil->parent` може тимчасово перезаписуватися, не створюючи жодної загрози аварійного завершення.
2. **Зменшення споживання пам'яті**: замість виділення окремих нульових покажчиків для кожного листка дерево зберігає лише одну статичну комірку пам'яті `T.nil` на все дерево.
3. **Регулярність пам'яті для конвеєра CPU**: відсутність вкладених умовних операторів дозволяє компілятору генерувати лінійні послідовності інструкцій без дорогих переходів.

---

### Вартові значення у геш-таблицях (Open Addressing)

Ще одна фундаментальна область застосування вартових — це геш-таблиці з відкритою адресацією (англ. *open addressing*) та лінійним пробуванням (англ. *linear probing*).

Коли елемент видаляється з геш-таблиці з відкритою адресацією, комірку не можна просто очистити до стану `EMPTY` (порожньо). Якщо наступні елементи під час колізії були зміщені праворуч від цієї комірки, наявність `EMPTY` передчасно зупинить подальший пошук за ланцюжком колізій, і валідні ключі стануть «невидимими».

Для розв'язання цієї проблеми в таблиці використовуються два різні вартові ключі:
- `EMPTY` (наприклад, `0xFFFFFFFF`) — комірка ніколи не містила елемента; лінійний пошук зупиняється.
- `TOMBSTONE` / «Могила» (наприклад, `0xFFFFFFFE`) — комірка містила елемент, який було видалено; пошук продовжується далі, але операція вставки нового елемента має право перевикористати цю комірку.

Використання двох внутрішньосмугових вартових ключів дозволяє реалізувати гранично компактні геш-таблиці без жодних зв'язних списків чи додаткових байтів пам'яті на кожен елемент.

---

### Вартовий слот у кільцевих буферах (Lock-Free Ring Buffers)

У багатопотокових безблокувальних кільцевих буферах для одного виробника й одного споживача (англ. *SPSC Ring Buffer*) постає класична дилема: як розрізнити стан «буфер повністю порожній» та стан «буфер повністю заповнений», якщо в обох випадках індекс запису `tail` наздоганяє індекс читання `head`?

Традиційне рішення — зберігати окрему атомарну змінну `count` — вимагає постійної між'ядерної синхронізації кеш-ліній (cache line bouncing), що різко знижує пропускну здатність.

Елегантне розв'язання полягає у виділенні **одного вартового слота**: буфер місткістю `N` елементів виділяє масив розміром `N + 1`. Стан «порожньо» фіксується умовою `head == tail`, а стан «заповнено» — умовою `(tail + 1) % (N + 1) == head`. Один вартовий слот усуває потребу в спільній змінній лічильника, дозволяючи потокам читання та запису працювати повністю незалежно на максимальній швидкості пам'яті.
